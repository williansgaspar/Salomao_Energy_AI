"""Parâmetros legais da transição do SCEE para uso na simulação.

As siglas GD I, GD II e GD III são rótulos operacionais do aplicativo. Os
percentuais decorrem dos arts. 26 e 27 da Lei nº 14.300/2022; não substituem
o enquadramento formal da unidade ou a memória de cálculo da distribuidora.
"""

ANOS_TRANSICAO = tuple(range(2023, 2029))

_FIO_B_GD_II = {
    2023: 0.15,
    2024: 0.30,
    2025: 0.45,
    2026: 0.60,
    2027: 0.75,
    2028: 0.90,
}


def parametros_regulatorios_scee(enquadramento, ano_referencia):
    """Retorna os fatores de incidência da Lei 14.300/2022.

    A regra do art. 17 passa a reger a cobrança a partir de 2029. Como a API
    tarifária usada pelo app não abre os componentes necessários para aquela
    regra, esta função restringe a estimativa aos anos de transição expressos
    no art. 27.
    """
    if enquadramento not in {"GD I", "GD II", "GD III"}:
        raise ValueError("Enquadramento SCEE inválido.")
    if ano_referencia not in ANOS_TRANSICAO:
        raise ValueError("A estimativa regulatória está disponível somente para 2023 a 2028.")

    if enquadramento == "GD I":
        return {
            "fio_b": 0.0,
            "fio_a_conexao": 0.0,
            "pde_ee_tfsee": 0.0,
            "fundamento": "Lei nº 14.300/2022, art. 26.",
        }
    if enquadramento == "GD II":
        return {
            "fio_b": _FIO_B_GD_II[ano_referencia],
            "fio_a_conexao": 0.0,
            "pde_ee_tfsee": 0.0,
            "fundamento": "Lei nº 14.300/2022, art. 27, caput.",
        }
    return {
        "fio_b": 1.0,
        "fio_a_conexao": 0.40,
        "pde_ee_tfsee": 1.0,
        "fundamento": "Lei nº 14.300/2022, art. 27, § 1º.",
    }
