"""Exportações auditáveis da consulta e da simulação."""

from datetime import datetime
from io import BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def metadados_fonte(contexto):
    return {
        "Fonte": "API de Dados Abertos da ANEEL — Tarifas de aplicação das distribuidoras",
        "Resource ID": "fcf2906c-7c32-4b9b-a637-054e7a5234f4",
        "Extração": datetime.now().astimezone().isoformat(timespec="seconds"),
        "Contexto": contexto,
        "Versão do app": "Revisão 5",
    }


def gerar_excel(dados: pd.DataFrame, memoria: pd.DataFrame, contexto: str):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dados.to_excel(writer, sheet_name="Dados ANEEL", index=False)
        memoria.to_excel(writer, sheet_name="Memória de cálculo", index=False)
        pd.DataFrame(metadados_fonte(contexto).items(), columns=["Campo", "Valor"]).to_excel(
            writer, sheet_name="Metadados", index=False
        )
    return buffer.getvalue()


def gerar_pdf(memoria: pd.DataFrame, contexto: str, total: float):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    estilos = getSampleStyleSheet()
    elementos = [Paragraph("Consulta de Tarifas ANEEL — memória de cálculo", estilos["Title"]), Spacer(1, 8)]
    elementos.append(Paragraph(contexto, estilos["BodyText"]))
    elementos.append(Paragraph(f"Total estimado: R$ {total:,.2f}", estilos["Heading2"]))
    if not memoria.empty:
        tabela = Table([list(memoria.columns)] + memoria.round(4).astype(str).values.tolist(), repeatRows=1)
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004A80")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elementos.extend([Spacer(1, 8), tabela])
    elementos.extend([Spacer(1, 10), Paragraph("Fonte: API pública de Dados Abertos da ANEEL. Estimativa não substitui faturamento da distribuidora.", estilos["BodyText"])])
    doc.build(elementos)
    return buffer.getvalue()
