"""Extração local de faturas Light Grupo A, com fallback de OCR."""

import io
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pymupdf
from PIL import Image
from rapidocr_onnxruntime import RapidOCR


@dataclass
class Token:
    x: float
    y: float
    texto: str
    confianca: float = 1.0


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", texto).strip()


def _numero_br(texto):
    if texto is None:
        return None
    s = re.sub(r"[^0-9,.-]", "", str(texto))
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


@lru_cache(maxsize=1)
def _ocr_engine():
    return RapidOCR()


def _tokens_ocr(imagem):
    resultado, _ = _ocr_engine()(np.asarray(imagem.convert("RGB")))
    tokens = []
    largura, altura = imagem.size
    for caixa, texto, confianca in resultado or []:
        x = sum(p[0] for p in caixa) / 4 / largura
        y = sum(p[1] for p in caixa) / 4 / altura
        tokens.append(Token(x, y, texto, float(confianca)))
    return tokens


def _tokens_pdf(conteudo):
    """Renderiza o PDF antes do OCR para manter a geometria igual à de imagens.

    A camada textual de alguns PDFs Light tem caixas de texto que não coincidem
    com as colunas visuais da fatura. Usá-la diretamente deslocava quantidade,
    tributos e alíquota, embora o texto em si estivesse correto.
    """
    documento = pymupdf.open(stream=conteudo, filetype="pdf")
    tokens = []
    for pagina in documento:
        pix = pagina.get_pixmap(dpi=180, colorspace=pymupdf.csRGB, alpha=False)
        imagem = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        tokens.extend(_tokens_ocr(imagem))
    return tokens, "OCR local do PDF"


def _agrupar_linhas(tokens, tolerancia=0.006):
    linhas = []
    for token in sorted(tokens, key=lambda t: (t.y, t.x)):
        linha = next((l for l in linhas if abs(l[0].y - token.y) <= tolerancia), None)
        if linha is None:
            linhas.append([token])
        else:
            linha.append(token)
    return [sorted(linha, key=lambda t: t.x) for linha in linhas]


def _classificar_rotulo(rotulo):
    n = _normalizar(rotulo)
    energia = ("energia" in n or "nergia" in n) and ("ativa" in n or "kwh" in n)
    demanda_nome = "demanda" in n or "manda" in n or bool(re.search(r"\b[a-z]?anda\b", n))
    demanda = demanda_nome and ("ativa" in n or "aiva" in n or "a&va" in n or "asva" in n or "kw" in n)
    if not (energia or demanda) or "reativ" in n:
        return None
    if "hfp" in n or "fora ponta" in n or "unico" in n:
        posto = "Fora ponta"
    elif re.search(r"\bhp\b", n) or "ponta" in n:
        posto = "Ponta"
    else:
        posto = "Não se aplica"
    return ("Energia" if energia else "Demanda"), posto


def _valor_zona(linha, minimo, maximo, alvo):
    candidatos = [(abs(t.x - alvo), _numero_br(t.texto), t) for t in linha if minimo <= t.x < maximo]
    candidatos = [c for c in candidatos if c[1] is not None]
    return min(candidatos, default=(None, None, None), key=lambda c: c[0])[1]


def _quantidade_apos_unidade(linha):
    """Lê Quant. pela posição relativa a kW/kWh, independente da largura do PDF."""
    unidades = [t for t in linha if _normalizar(t.texto) in {"kw", "kwh"} and t.x > 0.25]
    if not unidades:
        return None, None
    unidade = min(unidades, key=lambda t: t.x)
    candidatos = [
        (t.x - unidade.x, _numero_br(t.texto))
        for t in linha if 0.015 <= t.x - unidade.x <= 0.09 and _numero_br(t.texto) is not None
    ]
    quantidade = min(candidatos, default=(None, None), key=lambda c: c[0])[1]
    return ("kWh" if _normalizar(unidade.texto) == "kwh" else "kW"), quantidade


def _extrair_itens(tokens, modalidade=None):
    itens = []
    linhas = _agrupar_linhas(tokens)
    cabecalho_quant = next(
        ((indice, token.x) for indice, linha in enumerate(linhas) for token in linha
         if _normalizar(token.texto).startswith("quant")),
        (None, None),
    )
    indice_cabecalho, x_quantidade = cabecalho_quant
    for ordem, linha in enumerate(linhas):
        # Somente a tabela fiscal contém as quantidades faturadas. Leituras do
        # medidor, histórico e grandezas contratadas repetem kW/kWh e não podem
        # alimentar o perfil de cálculo.
        if indice_cabecalho is not None and ordem <= indice_cabecalho:
            continue
        if indice_cabecalho is not None and ordem > indice_cabecalho + 10:
            break
        texto_linha = _normalizar(" ".join(t.texto for t in linha))
        if texto_linha == "total" or texto_linha.startswith("medidor"):
            break
        rotulo = " ".join(t.texto for t in linha if t.x < 0.30)
        classificacao = _classificar_rotulo(rotulo)
        unidade_detectada, quantidade_relativa = _quantidade_apos_unidade(linha)
        if "reativ" in _normalizar(rotulo):
            continue
        if (
            not classificacao and quantidade_relativa is None and indice_cabecalho is not None
            and indice_cabecalho < ordem <= indice_cabecalho + 7
        ):
            candidatos_quantidade = [
                (abs(t.x - x_quantidade), _numero_br(t.texto)) for t in linha
                if abs(t.x - x_quantidade) <= 0.035 and _numero_br(t.texto) is not None
            ]
            quantidade_relativa = min(candidatos_quantidade, default=(None, None), key=lambda c: c[0])[1]
            if quantidade_relativa is not None and ordem + 1 < len(linhas):
                proximo_rotulo = " ".join(t.texto for t in linhas[ordem + 1] if t.x < 0.30)
                proxima_classificacao = _classificar_rotulo(proximo_rotulo)
                if proxima_classificacao == ("Demanda", "Ponta"):
                    classificacao = ("Demanda", "Fora ponta")
        if not classificacao and unidade_detectada and quantidade_relativa is not None:
            classificacao = ("Energia" if unidade_detectada == "kWh" else "Demanda", None)
        if not classificacao:
            continue
        tipo, posto = classificacao
        quantidade = quantidade_relativa if quantidade_relativa is not None else _valor_zona(linha, 0.29, 0.37, 0.34)
        preco_com_tributos = _valor_zona(linha, 0.43, 0.49, 0.452)
        valor_com_tributos = _valor_zona(linha, 0.49, 0.54, 0.509)
        pis_cofins = _valor_zona(linha, 0.54, 0.58, 0.560)
        base_icms = _valor_zona(linha, 0.58, 0.61, 0.591)
        aliquota_icms = _valor_zona(linha, 0.61, 0.645, 0.626)
        icms = _valor_zona(linha, 0.645, 0.68, 0.661)
        tarifa_liquida = _valor_zona(linha, 0.68, 0.72, 0.694)
        # Guardas semânticas: um deslocamento de coluna nunca pode transformar
        # valor monetário em percentual nem produzir tributo superior ao item.
        if aliquota_icms is not None and not 0 <= aliquota_icms <= 100:
            aliquota_icms = None
        if valor_com_tributos is not None:
            if pis_cofins is not None and not 0 <= pis_cofins <= valor_com_tributos:
                pis_cofins = None
            if icms is not None and not 0 <= icms <= valor_com_tributos:
                icms = None
        if quantidade is None and all(v is not None for v in (valor_com_tributos, pis_cofins, icms, tarifa_liquida)) and tarifa_liquida:
            quantidade = (valor_com_tributos - pis_cofins - icms) / tarifa_liquida
        if tarifa_liquida is None and quantidade and all(v is not None for v in (valor_com_tributos, pis_cofins, icms)):
            tarifa_liquida = (valor_com_tributos - pis_cofins - icms) / quantidade
        if pis_cofins is None and quantidade and all(v is not None for v in (valor_com_tributos, icms, tarifa_liquida)):
            pis_cofins = valor_com_tributos - icms - tarifa_liquida * quantidade
        itens.append({
            "tipo": tipo, "posto": posto, "unidade": "kWh" if tipo == "Energia" else "kW",
            "quantidade": quantidade, "consumo_mwh": quantidade / 1000 if tipo == "Energia" and quantidade is not None else None,
            "preco_com_tributos": preco_com_tributos, "valor_com_tributos": valor_com_tributos,
            "pis_cofins": pis_cofins, "base_icms": base_icms, "aliquota_icms": aliquota_icms,
            "icms": icms, "tarifa_liquida": tarifa_liquida, "_ordem": ordem,
        })
    for tipo in ("Energia", "Demanda"):
        itens_tipo = [i for i in itens if i["tipo"] == tipo]
        desconhecidos = [i for i in itens_tipo if i["posto"] is None]
        conhecidos = {i["posto"] for i in itens_tipo if i["posto"]}
        if tipo == "Demanda" and modalidade == "Verde":
            faltantes = ["Fora ponta"]
        else:
            faltantes = [p for p in ("Fora ponta", "Ponta") if p not in conhecidos]
        for item, posto_inferido in zip(sorted(desconhecidos, key=lambda i: i["_ordem"]), faltantes):
            item["posto"] = posto_inferido
    for item in itens:
        item.pop("_ordem", None)
    unicos = {}
    for item in itens:
        chave = (item["tipo"], item["posto"])
        if chave not in unicos or sum(v is not None for v in item.values()) > sum(v is not None for v in unicos[chave].values()):
            unicos[chave] = item
    return list(unicos.values())


def _metadados(tokens):
    texto = " ".join(t.texto for t in tokens)
    normal = _normalizar(texto)
    competencia = None
    meses = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}
    achou = re.search(r"\b(" + "|".join(meses) + r")[/\s-]*(20\d{2})\b", normal)
    if achou:
        competencia = f"{int(achou.group(2)):04d}-{meses[achou.group(1)]:02d}"
    subgrupo = next((g.upper() for g in re.findall(r"\ba[1-4]\b", normal)), None)
    modalidade = "Azul" if "azul" in normal else "Verde" if "verde" in normal else None
    classe = "Poder Público" if "poder publico" in normal else None
    subclasse = "Poder Público Federal" if "poder publico federal" in normal else None
    # O OCR pode concatenar base de cálculo e alíquota (ex.:
    # ``492.252,210,88%``). A busca de um dígito preserva o 0,88% final;
    # a de dois dígitos cobre alíquotas como 24,000%.
    taxas_um_digito = [float(x.replace(",", ".")) for x in re.findall(r"(\d,\d{2,3})\s*%", texto)]
    taxas_dois_digitos = [float(x.replace(",", ".")) for x in re.findall(r"(\d{2},\d{2,3})\s*%", texto)]
    taxas = taxas_um_digito + taxas_dois_digitos
    return {
        "distribuidora": "LIGHT SESA" if "light" in normal else None,
        "competencia": competencia, "subgrupo": subgrupo, "modalidade": modalidade,
        "classe": classe, "subclasse": subclasse,
        "pis_percentual": next((v for v in taxas if v < 2), None),
        "cofins_percentual": next((v for v in taxas if 2 <= v < 10), None),
        "icms_percentual": None,
    }


def extrair_fatura(conteudo, nome_arquivo):
    extensao = nome_arquivo.lower().rsplit(".", 1)[-1]
    if extensao == "pdf":
        tokens, metodo = _tokens_pdf(conteudo)
    elif extensao in {"png", "jpg", "jpeg", "webp"}:
        tokens, metodo = _tokens_ocr(Image.open(io.BytesIO(conteudo))), "OCR local"
    else:
        raise ValueError("Formato de fatura não suportado.")
    metadados = _metadados(tokens)
    itens = _extrair_itens(tokens, metadados.get("modalidade"))
    metadados["icms_percentual"] = next((i["aliquota_icms"] for i in itens if i.get("aliquota_icms") is not None), None)
    if metadados["icms_percentual"] is None:
        texto_normalizado = " ".join(t.texto for t in tokens)
        percentuais = [float(v.replace(",", ".")) for v in re.findall(r"(\d{1,2},\d{2,3})\s*%", texto_normalizado)]
        metadados["icms_percentual"] = next((v for v in percentuais if 10 <= v <= 40), None)
    avisos = []
    esperados = {("Energia", "Ponta"), ("Energia", "Fora ponta"), ("Demanda", "Fora ponta")}
    if metadados.get("modalidade") != "Verde":
        esperados.add(("Demanda", "Ponta"))
    encontrados = {(i["tipo"], i["posto"]) for i in itens if i.get("quantidade") is not None}
    faltantes = esperados - encontrados
    if faltantes:
        avisos.append("Revise os campos não reconhecidos: " + ", ".join(f"{t} {p}" for t, p in sorted(faltantes)))
    return {**metadados, "metodo": metodo, "itens": itens, "avisos": avisos}


def totais_tributos(fatura):
    """Consolida os tributos monetários reconhecidos nas linhas tarifárias."""
    itens = fatura.get("itens", [])
    return {
        "pis_cofins": sum(float(item.get("pis_cofins") or 0) for item in itens),
        "icms": sum(float(item.get("icms") or 0) for item in itens),
    }


def grandezas_da_fatura(fatura):
    """Retorna as grandezas faturadas por posto, prontas para a simulação."""
    grandezas = {"consumos_mwh": {}, "demandas_kw": {}}
    for item in fatura.get("itens", []):
        quantidade = item.get("quantidade")
        posto = item.get("posto")
        if quantidade is None or not posto:
            continue
        if item.get("tipo") == "Energia":
            grandezas["consumos_mwh"][posto] = float(quantidade) / 1000
        elif item.get("tipo") == "Demanda":
            grandezas["demandas_kw"][posto] = float(quantidade)
    return grandezas


def grandezas_ausentes(fatura):
    """Valida as grandezas obrigatórias conforme a modalidade tarifária."""
    grandezas = grandezas_da_fatura(fatura)
    verificacoes = [
        ("Consumo HFP", "Fora ponta" in grandezas["consumos_mwh"]),
        ("Consumo HPT", "Ponta" in grandezas["consumos_mwh"]),
        ("Demanda HFP", "Fora ponta" in grandezas["demandas_kw"]),
    ]
    if fatura.get("modalidade") != "Verde":
        verificacoes.append(("Demanda HPT", "Ponta" in grandezas["demandas_kw"]))
    return [nome for nome, presente in verificacoes if not presente]


def reconciliar_com_aneel(fatura, tarifas_mwh, tarifas_kw):
    linhas = []
    for item in fatura.get("itens", []):
        posto = item["posto"]
        if item["tipo"] == "Energia":
            tusd, te = tarifas_mwh.get(posto, (None, None))
            soma = (tusd + te) if tusd is not None and te is not None else None
        else:
            tusd = tarifas_kw.get(posto, tarifas_kw.get("Não se aplica", (None, None)))[0]
            te, soma = None, tusd
        liquida = item.get("tarifa_liquida")
        liquida_comparavel = liquida * 1000 if liquida is not None and item["tipo"] == "Energia" else liquida
        diferenca = liquida_comparavel - soma if liquida_comparavel is not None and soma is not None else None
        linhas.append({
            **item, "tarifa_liquida_comparavel": liquida_comparavel,
            "tusd_aneel": tusd, "te_aneel": te, "soma_aneel": soma, "diferenca_tarifa": diferenca,
        })
    return linhas
