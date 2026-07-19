#!/usr/bin/env python3
"""
CLI para consultar a BBCE Curva Forward via API do BBCE Connect (Portal do
Desenvolvedor BBCE). Requer credenciais proprias (plano Essentials) -- ver
README.md e .env.example.
"""

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

import bbce_api as api

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def montar_parser():
    p = argparse.ArgumentParser(description="Consulta a BBCE Curva Forward (precos futuros de energia).")
    p.add_argument("-d", "--data", default=date.today().isoformat(),
                    help="Data de referencia da curva (AAAA-MM-DD). Padrao: hoje.")
    p.add_argument("--fonte", choices=api.FONTES_ENERGIA,
                    help="Fonte de energia (CON, I0, I5, I1, CQ5).")
    p.add_argument("--regiao", choices=api.SUBMERCADOS,
                    help="Submercado (SE, SU, NE, NO). So se aplica a curva geral.")
    p.add_argument("--tipo-curva", choices=api.TIPOS_CURVA_PRODUTO,
                    help="Tipo de preco (PrecoFixo ou SWAP). So se aplica a curva por produto.")
    p.add_argument("--por-produto", action="store_true",
                    help="Consulta a curva por produto/ticker (v1/curve-product/bbce-fwd) em vez da curva geral.")
    p.add_argument("-o", "--output", help="Caminho do CSV de saida. Padrao: output/curva_forward_<data>.csv")
    p.add_argument("--sem-amostra", action="store_true", help="Nao imprime amostra no terminal.")
    return p


def salvar_csv(registros, caminho):
    if not registros:
        print("Nenhum registro retornado para os filtros informados.")
        return
    caminho.parent.mkdir(parents=True, exist_ok=True)
    campos = sorted({chave for registro in registros for chave in registro.keys()})
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        writer.writeheader()
        writer.writerows(registros)
    print(f"CSV salvo em {caminho} ({len(registros)} registros)")


def main():
    load_dotenv(SCRIPT_DIR / ".env")
    args = montar_parser().parse_args()
    credenciais = api.BBCECredenciais()
    session = api.nova_sessao()

    try:
        if args.por_produto:
            registros = api.curva_por_produto(
                session, credenciais, args.data, fonte=args.fonte, tipo_curva=args.tipo_curva,
            )
        else:
            registros = api.curva_forward(
                session, credenciais, args.data, fonte=args.fonte, regiao=args.regiao,
            )
    except api.BBCEAuthError as erro:
        print(f"Erro de autenticacao: {erro}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as erro:
        print(f"Erro ao consultar a API: {erro}", file=sys.stderr)
        sys.exit(1)

    if not args.sem_amostra:
        for registro in registros[:10]:
            print(registro)

    destino = Path(args.output) if args.output else OUTPUT_DIR / f"curva_forward_{args.data}.csv"
    salvar_csv(registros, destino)


if __name__ == "__main__":
    main()
