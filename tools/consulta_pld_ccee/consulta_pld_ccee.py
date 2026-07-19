#!/usr/bin/env python3
"""
Consulta o PLD (Preço de Liquidação das Diferenças) na API de Dados Abertos da CCEE.

Fonte: API de Dados Abertos da CCEE (CKAN, pública, sem autenticação)
Datasets cobertos (ver ccee_api.DATASETS):
    pld_horario          https://dadosabertos.ccee.org.br/dataset/pld_horario
    pld_media_diaria     https://dadosabertos.ccee.org.br/dataset/pld_media_diaria
    pld_media_mensal     https://dadosabertos.ccee.org.br/dataset/pld_media_mensal
    pld_final_historico  https://dadosabertos.ccee.org.br/dataset/pld_final_historico

Para uma interface web com filtros de Dataset / Submercado / Ano, veja app.py
(rode com: streamlit run app.py).

Exemplos de uso:
    python consulta_pld_ccee.py --listar-datasets
    python consulta_pld_ccee.py --dataset pld_horario --listar-campos
    python consulta_pld_ccee.py --dataset pld_horario --listar-submercados

    python consulta_pld_ccee.py --dataset pld_horario --submercado SE --data-inicio 2026-01-01 --data-fim 2026-01-31
    python consulta_pld_ccee.py --dataset pld_media_mensal --submercado NE -o pld_mensal_ne.csv
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

# Console do Windows por padrão usa cp1252, que não cobre todos os caracteres que
# podem aparecer em descrições/dados da CCEE (ex.: símbolos gregos) — força UTF-8
# na saída para não derrubar o script por causa de encoding.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from ccee_api import (
    DATASETS,
    DatasetInvalido,
    buscar_dataset,
    detectar_campos,
    nova_sessao,
    obter_campos,
    resolver_recursos,
    valores_distintos,
)

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def parse_data(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Data inválida '{texto}'. Use o formato AAAA-MM-DD.")


def dentro_do_intervalo(registro, campo_data, data_ini=None, data_fim=None):
    """Filtro client-side de data (a API não filtra por intervalo nativamente)."""
    if not campo_data or (data_ini is None and data_fim is None):
        return True
    bruto = registro.get(campo_data)
    if not bruto:
        return True
    texto = str(bruto)[:10]  # cobre tanto "AAAA-MM-DD" quanto "AAAA-MM-DDTHH:MM:SS"
    try:
        data = datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        return True  # não descarta registro com data em formato inesperado
    if data_ini and data < data_ini:
        return False
    if data_fim and data > data_fim:
        return False
    return True


def salvar_csv(registros, campos_ordem, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos_ordem, delimiter=";")
        writer.writeheader()
        for r in registros:
            writer.writerow({campo: r.get(campo, "") for campo in campos_ordem})


def imprimir_amostra(registros, campos_detectados, n=10):
    if not registros:
        print("Nenhum registro encontrado com os filtros informados.")
        return
    print(f"\nAmostra ({min(n, len(registros))} de {len(registros)} registros):\n")
    colunas = [c for c in campos_detectados.values() if c]
    if not colunas:
        colunas = list(registros[0].keys())
    print(" | ".join(colunas))
    for r in registros[:n]:
        print(" | ".join(str(r.get(c, "")) for c in colunas))


def main():
    parser = argparse.ArgumentParser(
        description="Consulta o PLD (Preço de Liquidação das Diferenças) na API de Dados Abertos da CCEE.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dataset", default="pld_horario", choices=list(DATASETS),
        help="Dataset CCEE a consultar (padrão: pld_horario). Ver --listar-datasets.",
    )
    parser.add_argument("--submercado", help="Filtra por submercado (ex.: SE, S, NE, N) — nome exato do campo detectado")
    parser.add_argument("--data-inicio", type=parse_data, help="Filtra registros a partir desta data (AAAA-MM-DD, filtro local)")
    parser.add_argument("--data-fim", type=parse_data, help="Filtra registros até esta data (AAAA-MM-DD, filtro local)")
    parser.add_argument("--limit", type=int, help="Número máximo de registros a retornar")
    parser.add_argument("-o", "--output", help="Caminho do CSV de saída (padrão: output/pld_<dataset>_<timestamp>.csv)")
    parser.add_argument("--sem-amostra", action="store_true", help="Não imprime amostra dos resultados no terminal")
    parser.add_argument("--atualizar-cache", action="store_true", help="Força atualização do cache de recursos/valores distintos")

    grupo_listagem = parser.add_mutually_exclusive_group()
    grupo_listagem.add_argument("--listar-datasets", action="store_true", help="Lista os datasets PLD disponíveis e sai")
    grupo_listagem.add_argument("--listar-recursos", action="store_true", help="Lista os recursos (resource_id) do --dataset e sai")
    grupo_listagem.add_argument("--listar-campos", action="store_true", help="Lista os campos (colunas) do --dataset, com a detecção heurística de submercado/data/valor, e sai")
    grupo_listagem.add_argument("--listar-submercados", action="store_true", help="Lista os submercados distintos do --dataset e sai")

    args = parser.parse_args()

    if args.listar_datasets:
        print("Datasets PLD disponíveis:\n")
        for dataset_id, descricao in DATASETS.items():
            print(f"  {dataset_id:<20} {descricao}")
        return

    session = nova_sessao()

    try:
        if args.listar_recursos:
            recursos = resolver_recursos(session, args.dataset, forcar_atualizacao=args.atualizar_cache)
            print(f"\n{len(recursos)} recurso(s) em '{args.dataset}':\n")
            for r in recursos:
                print(f"  {r['id']}  {r['name']}  ({r['format']}, atualizado em {r['last_modified']})")
            return

        if args.listar_campos:
            recursos = resolver_recursos(session, args.dataset, forcar_atualizacao=args.atualizar_cache)
            campos = obter_campos(session, recursos[0]["id"])
            detectados = detectar_campos(campos)
            print(f"\nCampos de '{args.dataset}' (recurso de referência: {recursos[0]['name']}):\n")
            for c in campos:
                print(f"  {c['id']:<30} tipo={c.get('type')}")
            print("\nDetecção heurística (confira antes de confiar em produção):")
            for chave, valor in detectados.items():
                print(f"  {chave:<12} -> {valor or '(não detectado)'}")
            return

        if args.listar_submercados:
            campos = obter_campos(session, resolver_recursos(session, args.dataset)[0]["id"])
            campo_submercado = detectar_campos(campos)["submercado"]
            if not campo_submercado:
                print("Não foi possível detectar automaticamente a coluna de submercado. Use --listar-campos e filtre manualmente.", file=sys.stderr)
                sys.exit(1)
            valores = valores_distintos(session, args.dataset, campo_submercado, forcar_atualizacao=args.atualizar_cache)
            print(f"\n{len(valores)} submercado(s) distinto(s) em '{campo_submercado}':\n")
            for v in valores:
                print(f"  {v}")
            return
    except DatasetInvalido as erro:
        print(f"\n{erro}", file=sys.stderr)
        sys.exit(1)

    campos = obter_campos(session, resolver_recursos(session, args.dataset)[0]["id"])
    campos_detectados = detectar_campos(campos)

    filtros = {}
    if args.submercado and campos_detectados["submercado"]:
        filtros[campos_detectados["submercado"]] = args.submercado.upper()
    elif args.submercado:
        print("Aviso: coluna de submercado não detectada automaticamente; filtro --submercado ignorado. Use --listar-campos.", file=sys.stderr)

    print(f"Consultando dataset '{args.dataset}' na API da CCEE...", file=sys.stderr)
    registros, campos_detectados = buscar_dataset(
        session, args.dataset, filters=filtros or None, limit_total=args.limit,
        forcar_atualizacao=args.atualizar_cache,
    )
    print(f"{len(registros)} registro(s) obtido(s).", file=sys.stderr)

    if args.data_inicio or args.data_fim:
        antes = len(registros)
        campo_data = campos_detectados["data"]
        registros = [r for r in registros if dentro_do_intervalo(r, campo_data, args.data_inicio, args.data_fim)]
        print(f"Filtro de data aplicado localmente (coluna '{campo_data}'): {antes} -> {len(registros)} registro(s).", file=sys.stderr)

    if not args.sem_amostra:
        imprimir_amostra(registros, campos_detectados)

    if args.output:
        caminho_saida = Path(args.output)
        if not caminho_saida.is_absolute():
            caminho_saida = OUTPUT_DIR / caminho_saida
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_saida = OUTPUT_DIR / f"pld_{args.dataset}_{timestamp}.csv"

    if registros:
        campos_ordem = [c["id"] for c in campos]
        salvar_csv(registros, campos_ordem, caminho_saida)
        print(f"\nArquivo salvo em: {caminho_saida}")
    else:
        print("\nNenhum registro para salvar.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as erro:
        print(f"\nErro: {erro}", file=sys.stderr)
        print(
            "Se o erro for '403 Forbidden', o WAF da CCEE pode estar bloqueando esta "
            "rede/origem — tente novamente de outra rede antes de abrir chamado com a CCEE.",
            file=sys.stderr,
        )
        sys.exit(1)
