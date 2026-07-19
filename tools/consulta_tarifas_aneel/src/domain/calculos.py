"""Cálculos tarifários puros, sem dependência de Streamlit ou da API."""

POSTOS = ("Ponta", "Intermediário", "Fora ponta", "Não se aplica")
HORAS_MES_TIPICO = 720.0
HORAS_PONTA_TIPICA = 66.0
HORAS_INTERMEDIARIA_TIPICA = 44.0


def _numero(valor, nome):
    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{nome} deve ser numérico.") from exc
    if numero < 0:
        raise ValueError(f"{nome} não pode ser negativo.")
    return numero


def calcular_por_posto(tarifas_mwh, consumos_mwh):
    """Calcula TE e TUSD Energia aplicando cada tarifa ao consumo do posto."""
    linhas = []
    total_te = total_tusd = 0.0
    for posto, consumo_bruto in consumos_mwh.items():
        consumo = _numero(consumo_bruto, f"Consumo {posto}")
        if consumo == 0:
            continue
        if posto not in tarifas_mwh:
            raise ValueError(f"Tarifa de energia ausente para o posto {posto}.")
        tusd, te = tarifas_mwh[posto]
        if tusd is None or te is None:
            raise ValueError(f"TE/TUSD incompleta para o posto {posto}.")
        subtotal_te = _numero(te, f"TE {posto}") * consumo
        subtotal_tusd = _numero(tusd, f"TUSD Energia {posto}") * consumo
        total_te += subtotal_te
        total_tusd += subtotal_tusd
        linhas.extend([
            {"componente": "TE", "posto": posto, "tarifa": te, "quantidade": consumo, "unidade": "MWh", "subtotal": subtotal_te},
            {"componente": "TUSD Energia", "posto": posto, "tarifa": tusd, "quantidade": consumo, "unidade": "MWh", "subtotal": subtotal_tusd},
        ])
    return {"te": total_te, "tusd_energia": total_tusd, "total": total_te + total_tusd, "linhas": linhas}


def calcular_por_consumo_total(tarifas_mwh, consumo_total_mwh, pesos):
    """Distribui o consumo total por pesos explícitos e calcula por posto."""
    consumo_total = _numero(consumo_total_mwh, "Consumo total")
    pesos_validos = {p: _numero(v, f"Peso {p}") for p, v in pesos.items() if float(v) > 0}
    soma = sum(pesos_validos.values())
    if consumo_total and not soma:
        raise ValueError("Informe ao menos um peso para distribuir o consumo total.")
    consumos = {posto: consumo_total * peso / soma for posto, peso in pesos_validos.items()}
    resultado = calcular_por_posto(tarifas_mwh, consumos)
    resultado["consumos_estimados"] = consumos
    return resultado


def calcular_demanda(tarifas_kw, demandas_kw):
    linhas = []
    total = 0.0
    for posto, demanda_bruta in demandas_kw.items():
        demanda = _numero(demanda_bruta, f"Demanda {posto}")
        if demanda == 0:
            continue
        if posto not in tarifas_kw or tarifas_kw[posto][0] is None:
            raise ValueError(f"TUSD Demanda ausente para o posto {posto}.")
        tarifa = _numero(tarifas_kw[posto][0], f"TUSD Demanda {posto}")
        subtotal = tarifa * demanda
        total += subtotal
        linhas.append({"componente": "TUSD Demanda", "posto": posto, "tarifa": tarifa, "quantidade": demanda, "unidade": "kW", "subtotal": subtotal})
    return {"total": total, "linhas": linhas}


def calcular_fatura(tarifas_mwh, consumos_mwh, tarifas_kw=None, demandas_kw=None):
    energia = calcular_por_posto(tarifas_mwh, consumos_mwh)
    demanda = calcular_demanda(tarifas_kw or {}, demandas_kw or {})
    return {
        "energia": energia,
        "demanda": demanda,
        "total": energia["total"] + demanda["total"],
        "linhas": energia["linhas"] + demanda["linhas"],
    }


def pesos_horarios_indicativos(postos):
    """Pesos de um mês típico; servem apenas para indicadores de tarifa."""
    postos = set(postos)
    if not postos:
        return {}
    if "Não se aplica" in postos:
        return {"Não se aplica": HORAS_MES_TIPICO}
    if postos == {"Fora ponta"}:
        return {"Fora ponta": HORAS_MES_TIPICO}
    pesos = {}
    if "Ponta" in postos:
        pesos["Ponta"] = HORAS_PONTA_TIPICA
    if "Intermediário" in postos:
        pesos["Intermediário"] = HORAS_INTERMEDIARIA_TIPICA
    if "Fora ponta" in postos:
        pesos["Fora ponta"] = HORAS_MES_TIPICO - sum(pesos.values())
    return pesos


def tarifas_indicativas_ponderadas(tarifas_mwh, tarifas_kw=None):
    """TE/TUSD médias por pesos horários, sem uso no cálculo da fatura."""
    tarifas_kw = tarifas_kw or {}
    pesos_energia = pesos_horarios_indicativos(tarifas_mwh)
    pesos_demanda = pesos_horarios_indicativos(tarifas_kw)

    def ponderar(tarifas, pesos, indice):
        if not pesos or not set(pesos).issubset(tarifas):
            return None
        return sum(_numero(tarifas[p][indice], f"Tarifa {p}") * horas for p, horas in pesos.items()) / HORAS_MES_TIPICO

    return {
        "te_ponderada": ponderar(tarifas_mwh, pesos_energia, 1),
        "tusd_energia_ponderada": ponderar(tarifas_mwh, pesos_energia, 0),
        "tusd_demanda_ponderada": ponderar(tarifas_kw, pesos_demanda, 0),
        "pesos_energia": pesos_energia,
        "pesos_demanda": pesos_demanda,
    }
