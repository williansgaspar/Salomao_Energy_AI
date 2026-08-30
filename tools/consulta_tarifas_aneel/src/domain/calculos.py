"""Cálculos tarifários puros, sem dependência de Streamlit ou da API."""

POSTOS = ("Ponta", "Intermediário", "Fora ponta", "Não se aplica")
HORAS_MES_TIPICO = 720.0
HORAS_PONTA_TIPICA = 66.0
HORAS_INTERMEDIARIA_TIPICA = 44.0

from .scee import parametros_regulatorios_scee


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


def comparar_acr_acl(te_acr, tusd_energia, tusd_demanda, consumo_total_mwh, te_acl, bandeira_r_mwh=0):
    """Compara ambientes alterando TE e adicionando bandeira somente no ACR."""
    te_acl = _numero(te_acl, "TE ACL")
    consumo = _numero(consumo_total_mwh, "Consumo total")
    te_acr = _numero(te_acr, "TE ACR")
    tusd_energia = _numero(tusd_energia, "TUSD Energia")
    tusd_demanda = _numero(tusd_demanda, "TUSD Demanda")
    bandeira_r_mwh = _numero(bandeira_r_mwh, "Adicional de bandeira")
    custo_bandeira_acr = round(bandeira_r_mwh * consumo, 4)
    total_acr = te_acr + tusd_energia + tusd_demanda + custo_bandeira_acr
    custo_te_acl = te_acl * consumo
    total_acl = custo_te_acl + tusd_energia + tusd_demanda
    economia = total_acr - total_acl
    return {
        "consumo_total_mwh": consumo,
        "te_acr_efetiva": te_acr / consumo if consumo else None,
        "te_acl": te_acl,
        "custo_te_acr": te_acr,
        "custo_te_acl": custo_te_acl,
        "bandeira_r_mwh": bandeira_r_mwh,
        "custo_bandeira_acr": custo_bandeira_acr,
        "tusd_energia": tusd_energia,
        "tusd_demanda": tusd_demanda,
        "total_acr": total_acr,
        "total_acl": total_acl,
        "economia": economia,
        "economia_percentual": economia / total_acr * 100 if total_acr else None,
    }


def comparar_acr_scee_bt(total_acr_sem_bandeira, consumo_total_mwh, desconto_scee_percentual, bandeira_r_mwh=0):
    """Compara a conta ACR de referência com o cenário SCEE/GD para uma UC BT.

    O desconto é uma premissa comercial aplicada sobre a conta ACR já acrescida
    da bandeira. O detalhamento regulatório da fatura permanece fora deste
    comparativo resumido.
    """
    total_acr_sem_bandeira = _numero(total_acr_sem_bandeira, "Conta ACR sem bandeira")
    consumo = _numero(consumo_total_mwh, "Consumo total")
    desconto = _numero(desconto_scee_percentual, "Desconto SCEE/GD")
    bandeira_r_mwh = _numero(bandeira_r_mwh, "Adicional de bandeira")
    if desconto > 100:
        raise ValueError("Desconto SCEE/GD não pode ser superior a 100%.")

    custo_bandeira_acr = round(bandeira_r_mwh * consumo, 4)
    conta_acr = total_acr_sem_bandeira + custo_bandeira_acr
    conta_scee_com_desconto = round(conta_acr * (1 - desconto / 100), 4)
    economia = conta_acr - conta_scee_com_desconto
    return {
        "consumo_total_mwh": consumo,
        "conta_acr_sem_bandeira": total_acr_sem_bandeira,
        "bandeira_r_mwh": bandeira_r_mwh,
        "custo_bandeira_acr": custo_bandeira_acr,
        "conta_acr": conta_acr,
        "desconto_scee_percentual": desconto,
        "conta_scee_com_desconto": conta_scee_com_desconto,
        "economia": economia,
        "economia_percentual": economia / conta_acr * 100 if conta_acr else None,
    }


def simular_scee_bt(
    total_acr_sem_bandeira,
    consumo_total_mwh,
    percentual_alocacao,
    desconto_comercial_percentual,
    enquadramento,
    custo_disponibilidade_kwh=100,
    fio_b_r_mwh=0,
    componentes_adicionais_gdiii_r_mwh=0,
    bandeira_r_mwh=0,
    ano_referencia=2026,
    fio_a_conexao_r_mwh=0,
    pde_ee_tfsee_r_mwh=0,
    ajustes_financeiros_acr=0,
    ajustes_financeiros_scee=0,
):
    """Simula SCEE para UC do grupo B pelos cenários GD I, GD II e GD III.

    A tarifa-base é formada por TE + TUSD Energia da consulta. A bandeira é
    cobrada pela distribuidora apenas sobre a energia não compensada (Lei
    14.300/2022, art. 19), mas integra o preço comercial do crédito quando o
    contrato estabelece desconto linear sobre a tarifa vigente da distribuidora.
    Para GD II e GD III, as parcelas residuais incidentes sobre a energia
    compensada são entradas explícitas, pois a API não abre o Fio B por UC.
    """
    total_acr = _numero(total_acr_sem_bandeira, "Conta ACR sem bandeira")
    consumo = _numero(consumo_total_mwh, "Consumo total")
    alocacao = _numero(percentual_alocacao, "Alocação de créditos")
    desconto = _numero(desconto_comercial_percentual, "Desconto comercial")
    disponibilidade = _numero(custo_disponibilidade_kwh, "Custo de disponibilidade")
    fio_b = _numero(fio_b_r_mwh, "Fio B")
    adicionais_gdiii = _numero(componentes_adicionais_gdiii_r_mwh, "Componentes adicionais GD III")
    fio_a_conexao = _numero(fio_a_conexao_r_mwh, "Fio A, conexão e demais sistemas")
    pde_ee_tfsee = _numero(pde_ee_tfsee_r_mwh, "P&D, eficiência energética e TFSEE")
    bandeira = _numero(bandeira_r_mwh, "Adicional de bandeira")
    ajustes_acr = _numero(ajustes_financeiros_acr, "Ajustes financeiros ACR")
    ajustes_scee = _numero(ajustes_financeiros_scee, "Ajustes financeiros SCEE")
    if alocacao > 100:
        raise ValueError("Alocação de créditos não pode ser superior a 100%.")
    if desconto > 100:
        raise ValueError("Desconto comercial não pode ser superior a 100%.")
    fatores_regulatorios = parametros_regulatorios_scee(enquadramento, int(ano_referencia))

    tarifa_base_r_mwh = total_acr / consumo if consumo else 0.0
    tarifa_comercial_r_mwh = tarifa_base_r_mwh + bandeira
    energia_compensada_mwh = consumo * alocacao / 100
    energia_faturada_mwh = consumo - energia_compensada_mwh
    residual_scee_r_mwh = (
        fatores_regulatorios["fio_b"] * fio_b
        + fatores_regulatorios["fio_a_conexao"] * fio_a_conexao
        + fatores_regulatorios["pde_ee_tfsee"] * pde_ee_tfsee
        + adicionais_gdiii
    )

    fatura_light_sem_piso = (
        energia_faturada_mwh * (tarifa_base_r_mwh + bandeira)
        + energia_compensada_mwh * residual_scee_r_mwh
    )
    piso_disponibilidade = disponibilidade / 1000 * tarifa_base_r_mwh
    fatura_light = max(fatura_light_sem_piso, piso_disponibilidade)
    pagamento_fornecedor = energia_compensada_mwh * tarifa_comercial_r_mwh * (1 - desconto / 100)
    conta_scee = fatura_light + pagamento_fornecedor
    conta_acr = total_acr + consumo * bandeira
    conta_acr_financeira = conta_acr + ajustes_acr
    conta_scee_financeira = conta_scee + ajustes_scee
    economia = conta_acr_financeira - conta_scee_financeira
    return {
        "enquadramento": enquadramento,
        "ano_referencia": int(ano_referencia),
        "fatores_regulatorios": fatores_regulatorios,
        "consumo_total_mwh": consumo,
        "energia_compensada_mwh": energia_compensada_mwh,
        "energia_faturada_mwh": energia_faturada_mwh,
        "tarifa_base_r_mwh": tarifa_base_r_mwh,
        "tarifa_comercial_r_mwh": tarifa_comercial_r_mwh,
        "residual_scee_r_mwh": residual_scee_r_mwh,
        "fio_b_r_mwh": fio_b,
        "fio_a_conexao_r_mwh": fio_a_conexao,
        "pde_ee_tfsee_r_mwh": pde_ee_tfsee,
        "bandeira_r_mwh": bandeira,
        "piso_disponibilidade": piso_disponibilidade,
        "fatura_light_sem_piso": fatura_light_sem_piso,
        "fatura_light": fatura_light,
        "pagamento_fornecedor": pagamento_fornecedor,
        "conta_acr": conta_acr,
        "conta_scee": conta_scee,
        "ajustes_financeiros_acr": ajustes_acr,
        "ajustes_financeiros_scee": ajustes_scee,
        "conta_acr_financeira": conta_acr_financeira,
        "conta_scee_financeira": conta_scee_financeira,
        "economia": economia,
        "economia_percentual": economia / conta_acr_financeira * 100 if conta_acr_financeira else None,
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
