#!/usr/bin/env python3
"""
Consulta tarifas de distribuidoras de energia elétrica homologadas pela ANEEL.

Fonte: API de Dados Abertos da ANEEL (CKAN, pública, sem autenticação)
Dataset: https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica
Recurso: tarifas-homologadas-distribuidoras-energia-eletrica.csv (datastore ativo)

Para uma interface web com filtros de Distribuidora / Ano / REH, veja app.py
(rode com: streamlit run app.py).

Exemplos de uso:
    python consulta_tarifas_aneel.py --listar-distribuidoras
    python consulta_tarifas_aneel.py --listar-subgrupos
    python consulta_tarifas_aneel.py --listar-modalidades

    python consulta_tarifas_aneel.py -d "LIGHT" --subgrupo B1 --modalidade Convencional
    python consulta_tarifas_aneel.py -d "LIGHT" --subgrupo A4 --data-vigencia 2026-01-15
    python consulta_tarifas_aneel.py -d "CPFL JAGUARI" -o cpfl_jaguari.csv
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from aneel_api import (
    CAMPOS,
    DistribuidoraAmbigua,
    DistribuidoraNaoEncontrada,
    buscar_paginado,
    converter_valor_brl,
    nova_sessao,
    resolver_distribuidora,
    valores_distintos,
)

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def data_dentro_da_vigencia(registro, data_ref=None, data_ini=None, data_fim=None):
    """Filtro client-side de vigência (a API não filtra por intervalo de datas)."""
    try:
        ini = datetime.strptime(registro["DatInicioVigencia"], "%Y-%m-%d").date()
    except (ValueError, KeyError, TypeError):
        return True  # não descarta registro com data mal formatada
    fim_txt = registro.get("DatFimVigencia")
    fim = None
    if fim_txt:
        try:
            fim = datetime.strptime(fim_txt, "%Y-%m-%d").date()
        except ValueError:
            fim = None

    if data_ref:
        if ini > data_ref:
            return False
        if fim and fim < data_ref:
            return False
        return True

    if data_ini and fim and fim < data_ini:
        return False
    if data_fim and ini > data_fim:
        return False
    return True


def montar_filtros(args):
    filtros = {}
    if args.subgrupo:
        filtros["DscSubGrupo"] = args.subgrupo.upper()
    if args.modalidade:
        filtros["DscModalidadeTarifaria"] = args.modalidade.strip().title()
    if args.classe:
        filtros["DscClasse"] = args.classe
    if args.subclasse:
        filtros["DscSubClasse"] = args.subclasse
    if args.base_tarifaria:
        filtros["DscBaseTarifaria"] = args.base_tarifaria
    if args.reh:
        filtros["DscREH"] = args.reh
    if args.cnpj:
        filtros["NumCNPJDistribuidora"] = args.cnpj.replace(".", "").replace("/", "").replace("-", "")
    return filtros


def salvar_csv(registros, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        writer.writeheader()
        for r in registros:
            linha = {campo: r.get(campo, "") for campo in CAMPOS}
            linha["VlrTUSD"] = converter_valor_brl(r.get("VlrTUSD"))
            linha["VlrTE"] = converter_valor_brl(r.get("VlrTE"))
            writer.writerow(linha)


def imprimir_amostra(registros, n=10):
    if not registros:
        print("Nenhum registro encontrado com os filtros informados.")
        return
    print(f"\nAmostra ({min(n, len(registros))} de {len(registros)} registros):\n")
    cabecalho = ["Distribuidora", "Vigência", "SubGrupo", "Modalidade", "Classe", "Posto", "TUSD", "TE"]
    print(" | ".join(cabecalho))
    for r in registros[:n]:
        print(" | ".join([
            r.get("SigAgente", ""),
            f"{r.get('DatInicioVigencia', '')} a {r.get('DatFimVigencia', '')}",
            r.get("DscSubGrupo", ""),
            r.get("DscModalidadeTarifaria", ""),
            r.get("DscClasse", ""),
            r.get("NomPostoTarifario", ""),
            str(converter_valor_brl(r.get("VlrTUSD"))),
            str(converter_valor_brl(r.get("VlrTE"))),
        ]))


def parse_data(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Data inválida '{texto}'. Use o formato AAAA-MM-DD.")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta tarifas de distribuidoras de energia elétrica na API de Dados Abertos da ANEEL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("-d", "--distribuidora", help="Nome (ou parte do nome) da distribuidora, ex.: 'LIGHT', 'CPFL JAGUARI'")
    parser.add_argument("--cnpj", help="CNPJ da distribuidora (com ou sem máscara)")
    parser.add_argument("--reh", help="Descrição exata da REH (Resolução Homologatória), ex.: 'RESOLUÇÃO HOMOLOGATÓRIA Nº 1.085, DE 3 DE NOVEMBRO DE 2010'")
    parser.add_argument("--subgrupo", help="Subgrupo tarifário, ex.: A4, B1, B3")
    parser.add_argument("--modalidade", help="Modalidade tarifária, ex.: Convencional, Branca, Azul, Verde")
    parser.add_argument("--classe", help="Classe de consumo, ex.: Residencial, Industrial")
    parser.add_argument("--subclasse", help="Subclasse de consumo")
    parser.add_argument("--base-tarifaria", help="'Tarifa de Aplicação' ou 'Base Econômica'")
    parser.add_argument("--data-vigencia", type=parse_data, help="Filtra tarifas vigentes nesta data (AAAA-MM-DD)")
    parser.add_argument("--data-inicio", type=parse_data, help="Filtra vigências que se sobrepõem a partir desta data (AAAA-MM-DD)")
    parser.add_argument("--data-fim", type=parse_data, help="Filtra vigências que se sobrepõem até esta data (AAAA-MM-DD)")
    parser.add_argument("--ano", type=int, help="Filtra pelo ano de início de vigência, ex.: 2026")
    parser.add_argument("--limit", type=int, help="Número máximo de registros a retornar")
    parser.add_argument("-o", "--output", help="Caminho do CSV de saída (padrão: output/tarifas_<timestamp>.csv)")
    parser.add_argument("--sem-amostra", action="store_true", help="Não imprime amostra dos resultados no terminal")
    parser.add_argument("--atualizar-cache", action="store_true", help="Força atualização do cache de valores distintos (distribuidoras etc.)")

    grupo_listagem = parser.add_mutually_exclusive_group()
    grupo_listagem.add_argument("--listar-distribuidoras", action="store_true", help="Lista os nomes (SigAgente) de distribuidoras disponíveis e sai")
    grupo_listagem.add_argument("--listar-subgrupos", action="store_true", help="Lista os subgrupos tarifários disponíveis e sai")
    grupo_listagem.add_argument("--listar-modalidades", action="store_true", help="Lista as modalidades tarifárias disponíveis e sai")
    grupo_listagem.add_argument("--listar-classes", action="store_true", help="Lista as classes de consumo disponíveis e sai")

    args = parser.parse_args()

    session = nova_sessao()

    listagens = {
        "listar_distribuidoras": "SigAgente",
        "listar_subgrupos": "DscSubGrupo",
        "listar_modalidades": "DscModalidadeTarifaria",
        "listar_classes": "DscClasse",
    }
    for arg_nome, campo in listagens.items():
        if getattr(args, arg_nome):
            valores = valores_distintos(session, campo, forcar_atualizacao=args.atualizar_cache)
            print(f"\n{len(valores)} valores distintos em '{campo}':\n")
            for v in valores:
                print(f"  {v}")
            return

    filtros = montar_filtros(args)

    if args.distribuidora:
        try:
            sig_agente = resolver_distribuidora(session, args.distribuidora, forcar_atualizacao=args.atualizar_cache)
        except DistribuidoraAmbigua as erro:
            print(f"\nO termo '{erro.termo}' é ambíguo. Distribuidoras encontradas:", file=sys.stderr)
            for c in erro.candidatas:
                print(f"  - {c}", file=sys.stderr)
            print("\nRefine o termo de busca (--distribuidora) com um nome mais específico.", file=sys.stderr)
            sys.exit(1)
        except DistribuidoraNaoEncontrada as erro:
            print(f"\nNenhuma distribuidora encontrada para '{erro.termo}'.", file=sys.stderr)
            print("Use --listar-distribuidoras para ver os nomes (SigAgente) disponíveis.", file=sys.stderr)
            sys.exit(1)
        filtros["SigAgente"] = sig_agente
        print(f"Distribuidora resolvida: {sig_agente}", file=sys.stderr)

    print("Consultando API da ANEEL...", file=sys.stderr)
    registros, total_bruto = buscar_paginado(session, filters=filtros, limit_total=args.limit)
    print(f"{len(registros)} registro(s) obtido(s) (de {total_bruto} correspondentes aos filtros de igualdade).", file=sys.stderr)

    if args.data_vigencia or args.data_inicio or args.data_fim or args.ano:
        antes = len(registros)
        registros = [
            r for r in registros
            if data_dentro_da_vigencia(r, data_ref=args.data_vigencia, data_ini=args.data_inicio, data_fim=args.data_fim)
            and (args.ano is None or r.get("DatInicioVigencia", "").startswith(str(args.ano)))
        ]
        print(f"Filtro de vigência/ano aplicado localmente: {antes} -> {len(registros)} registro(s).", file=sys.stderr)

    if not args.sem_amostra:
        imprimir_amostra(registros)

    if args.output:
        caminho_saida = Path(args.output)
        if not caminho_saida.is_absolute():
            caminho_saida = OUTPUT_DIR / caminho_saida
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_saida = OUTPUT_DIR / f"tarifas_{timestamp}.csv"

    if registros:
        salvar_csv(registros, caminho_saida)
        print(f"\nArquivo salvo em: {caminho_saida}")
    else:
        print("\nNenhum registro para salvar.")


if __name__ == "__main__":
    main()
