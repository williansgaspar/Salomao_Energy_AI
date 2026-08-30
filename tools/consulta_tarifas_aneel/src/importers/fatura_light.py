"""Extração local de faturas Light dos Grupos A e B, com fallback de OCR."""

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
    pagina: int = 0


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


def _tokens_ocr(imagem, pagina=0):
    resultado, _ = _ocr_engine()(np.asarray(imagem.convert("RGB")))
    tokens = []
    largura, altura = imagem.size
    for caixa, texto, confianca in resultado or []:
        x = sum(p[0] for p in caixa) / 4 / largura
        y = sum(p[1] for p in caixa) / 4 / altura
        tokens.append(Token(x, y, texto, float(confianca), pagina))
    return tokens


def _tokens_pdf(conteudo):
    """Renderiza o PDF antes do OCR para manter a geometria igual à de imagens.

    A camada textual de alguns PDFs Light tem caixas de texto que não coincidem
    com as colunas visuais da fatura. Usá-la diretamente deslocava quantidade,
    tributos e alíquota, embora o texto em si estivesse correto.

    Cada token é marcado com o número da página de origem: uma fatura Light
    real quase sempre chega em várias páginas (nota fiscal + boleto, ou duas
    UCs no mesmo PDF sob "Ambas"), e cada página tem sua própria coordenada Y
    relativa (0 a 1). Sem a marcação, linhas de páginas diferentes na mesma
    altura relativa eram agrupadas como se fossem uma única linha da tabela
    fiscal, misturando quantidade, tarifa e tributos de itens não relacionados.
    """
    documento = pymupdf.open(stream=conteudo, filetype="pdf")
    tokens = []
    for indice, pagina in enumerate(documento):
        pix = pagina.get_pixmap(dpi=180, colorspace=pymupdf.csRGB, alpha=False)
        imagem = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        tokens.extend(_tokens_ocr(imagem, pagina=indice))
    return tokens, "OCR local do PDF"


def _texto_nativo_pdf(conteudo):
    """Recupera a camada textual somente para os metadados do documento.

    A geometria da camada textual não é confiável para a tabela fiscal da
    Light, razão pela qual os itens continuam sendo lidos por OCR. Já campos
    compactos como Grupo/Subgrupo costumam estar íntegros nessa camada e são
    uma fonte complementar mais precisa que a imagem renderizada.
    """
    documento = pymupdf.open(stream=conteudo, filetype="pdf")
    try:
        return " ".join(pagina.get_text("text") for pagina in documento)
    finally:
        documento.close()


def _texto_cabecalho_pdf(conteudo):
    """Lê em alta resolução a caixa de classificação da primeira página Light.

    Em faturas digitalizadas, o campo compacto ``Grupo / Subgrupo`` perde
    definição na renderização integral usada para a tabela fiscal. O recorte
    preserva a resolução necessária sem alterar a extração geométrica dos
    itens da fatura.
    """
    documento = pymupdf.open(stream=conteudo, filetype="pdf")
    try:
        if not documento:
            return ""
        pagina = documento[0]
        retangulo = pagina.rect
        # Faixa superior esquerda: classificação, tipo de fornecimento e UC.
        recorte = pymupdf.Rect(
            retangulo.x0 + retangulo.width * 0.12,
            retangulo.y0 + retangulo.height * 0.15,
            retangulo.x0 + retangulo.width * 0.58,
            retangulo.y0 + retangulo.height * 0.25,
        )
        pix = pagina.get_pixmap(dpi=400, clip=recorte, colorspace=pymupdf.csRGB, alpha=False)
        imagem = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        return " ".join(token.texto for token in _tokens_ocr(imagem))
    finally:
        documento.close()


def _agrupar_linhas(tokens, tolerancia=0.006):
    linhas = []
    for token in sorted(tokens, key=lambda t: (t.pagina, t.y, t.x)):
        linha = next(
            (l for l in linhas if l[0].pagina == token.pagina and abs(l[0].y - token.y) <= tolerancia),
            None,
        )
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


def _extrair_itens(tokens, modalidade=None, grupo=None):
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
        base_icms = _valor_zona(linha, 0.5905, 0.6345, 0.611)
        aliquota_icms = _valor_zona(linha, 0.6345, 0.6785, 0.658)
        icms = _valor_zona(linha, 0.6785, 0.719, 0.699)
        tarifa_liquida = _valor_zona(linha, 0.719, 0.764, 0.740)
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
        if grupo == "B" and tipo == "Energia":
            faltantes = ["Não se aplica"] * len(desconhecidos)
        elif grupo == "B":
            faltantes = []
        elif tipo == "Demanda" and modalidade == "Verde":
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


def _metadados(tokens, texto_adicional=""):
    texto = " ".join(t.texto for t in tokens)
    if texto_adicional:
        texto = f"{texto} {texto_adicional}"
    normal = _normalizar(texto)
    competencia = None
    meses = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}
    achou = re.search(r"\b(" + "|".join(meses) + r")[/\s-]*(20\d{2})\b", normal)
    if achou:
        competencia = f"{int(achou.group(2)):04d}-{meses[achou.group(1)]:02d}"
    else:
        competencia_numerica = re.search(r"\b(0?[1-9]|1[0-2])\s*/\s*(20\d{2})\b", normal)
        if competencia_numerica:
            competencia = f"{int(competencia_numerica.group(2)):04d}-{int(competencia_numerica.group(1)):02d}"
    grupo_explicito = re.search(r"\bgrupo\s*[:\-]?\s*([ab8])\b", normal)
    grupo = grupo_explicito.group(1).upper().replace("8", "B") if grupo_explicito else None
    # B3 frequentemente chega como B 3, B-3, B:3 ou 83 no OCR. A conversão
    # do 8 é restrita à estrutura de subgrupo para não alterar outros números.
    subgrupos = [
        re.sub(r"[\s\-:./]", "", g).upper().replace("8", "B")
        for g in re.findall(r"\b[ab8][\s\-:./]*[1-4]\b", normal)
    ]
    subgrupo = next((g for g in subgrupos if not grupo or g.startswith(grupo)), None)
    if grupo is None and subgrupo:
        grupo = subgrupo[0]
    modalidade = (
        "Azul" if "azul" in normal else "Verde" if "verde" in normal
        else "Convencional" if "convencional" in normal or grupo == "B" else None
    )
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
        "competencia": competencia, "subgrupo": subgrupo, "grupo": grupo, "modalidade": modalidade,
        "classe": classe, "subclasse": subclasse,
        "detalhe": "SCEE" if "scee" in normal else "APE" if re.search(r"\bape\b", normal) else None,
        "pis_percentual": next((v for v in taxas if v < 2), None),
        "cofins_percentual": next((v for v in taxas if 2 <= v < 10), None),
        "icms_percentual": None,
    }


def extrair_fatura(conteudo, nome_arquivo):
    extensao = nome_arquivo.lower().rsplit(".", 1)[-1]
    texto_metadados = ""
    if extensao == "pdf":
        tokens, metodo = _tokens_pdf(conteudo)
        texto_metadados = f"{_texto_nativo_pdf(conteudo)} {_texto_cabecalho_pdf(conteudo)}"
    elif extensao in {"png", "jpg", "jpeg", "webp"}:
        tokens, metodo = _tokens_ocr(Image.open(io.BytesIO(conteudo))), "OCR local"
    else:
        raise ValueError("Formato de fatura não suportado.")
    metadados = _metadados(tokens, texto_metadados)
    itens = _extrair_itens(tokens, metadados.get("modalidade"), metadados.get("grupo"))
    metadados["icms_percentual"] = next((i["aliquota_icms"] for i in itens if i.get("aliquota_icms") is not None), None)
    if metadados["icms_percentual"] is None:
        texto_normalizado = " ".join(t.texto for t in tokens)
        percentuais = [float(v.replace(",", ".")) for v in re.findall(r"(\d{1,2},\d{2,3})\s*%", texto_normalizado)]
        metadados["icms_percentual"] = next((v for v in percentuais if 10 <= v <= 40), None)
    avisos = []
    faltantes = grandezas_ausentes({**metadados, "itens": itens})
    if metadados.get("grupo") is None:
        avisos.append("Grupo tarifário não identificado pelo OCR; confira subgrupo, modalidade e grandezas antes de calcular.")
    elif faltantes:
        avisos.append("Revise os campos não reconhecidos: " + ", ".join(faltantes))
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
            if fatura.get("grupo") == "B":
                posto = "Não se aplica"
            grandezas["consumos_mwh"][posto] = float(quantidade) / 1000
        elif item.get("tipo") == "Demanda":
            grandezas["demandas_kw"][posto] = float(quantidade)
    return grandezas


def grandezas_ausentes(fatura):
    """Valida grandezas segundo o Grupo A, Grupo B ou perfil ainda indeterminado."""
    grandezas = grandezas_da_fatura(fatura)
    grupo = fatura.get("grupo") or str(fatura.get("subgrupo") or "").strip().upper()[:1]
    if grupo not in {"A", "B"} and fatura.get("modalidade") in {"Verde", "Azul"}:
        grupo = "A"
    if grupo == "B":
        return [] if grandezas["consumos_mwh"] else ["Consumo de energia"]
    if grupo != "A":
        return []
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
