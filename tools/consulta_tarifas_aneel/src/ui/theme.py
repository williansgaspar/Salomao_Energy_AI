"""Identidade visual institucional e componentes comuns."""

import base64
from pathlib import Path

import streamlit as st


def fmt_brl(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def aplicar_tema():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: Inter, 'Segoe UI', sans-serif;}
    [data-testid="stHeader"] {background: transparent;}
    .stAppDeployButton, [data-testid="stToolbar"] {display:none !important;}
    .block-container {max-width: 1440px; padding-top: 1rem;}
    .pref-top {background:#343A40;color:white;padding:.45rem 1rem;border-radius:8px 8px 0 0;display:flex;justify-content:space-between;font-size:.82rem;}
    .pref-top b {color:#12BBEF}.pref-band {background:linear-gradient(120deg,#004A80,#08689E);color:white;padding:1rem 1.25rem;border-radius:0 0 8px 8px;display:flex;align-items:center;gap:1rem;margin-bottom:1rem}
    .pref-band h1 {font-size:1.55rem;margin:0;color:white}.pref-band small{opacity:.86}
    .pref-band img {height:50px;background:white;padding:6px 10px;border-radius:7px}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius:8px;}
    .total-card {border-left:5px solid #0BB975;background:rgba(11,185,117,.08);padding:12px 16px;border-radius:7px;margin:.5rem 0}
    .total-card strong {font-size:1.7rem;color:#07885a}
    @media (max-width: 900px) {.pref-top span:last-child{display:none}.pref-band h1{font-size:1.2rem}.block-container{padding-left:.75rem;padding-right:.75rem}}
    </style>
    """, unsafe_allow_html=True)


def cabecalho(base_dir: Path):
    logo = base_dir / "assets" / "logo_rio_energia_verde.png"
    logo_html = ""
    if logo.exists():
        uri = base64.b64encode(logo.read_bytes()).decode("ascii")
        logo_html = f'<img src="data:image/png;base64,{uri}" alt="Projeto Rio de Energia Verde">'
    st.markdown(f"""
    <div class="pref-top"><span><b>PREFEITURA</b>.RIO</span><span>Secretaria Municipal de Administração · A/NMI</span></div>
    <div class="pref-band">{logo_html}<div><h1>Consulta de Tarifas ANEEL</h1><small>Programa de Eficiência, Transição e Governança Energética · Revisão 4</small></div></div>
    """, unsafe_allow_html=True)
