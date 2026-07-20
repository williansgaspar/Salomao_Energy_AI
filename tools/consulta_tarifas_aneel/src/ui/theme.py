"""Identidade visual institucional, temas e componentes comuns."""

import base64
from pathlib import Path

import streamlit as st


def fmt_brl(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _data_uri(caminho: Path):
    if not caminho.exists():
        return None
    return "data:image/png;base64," + base64.b64encode(caminho.read_bytes()).decode("ascii")


def aplicar_tema(escuro=False):
    p = ({
        "bg": "#0B1118", "surface": "#121B25", "surface2": "#172331", "text": "#ECF3F8",
        "muted": "#9FB0BE", "border": "#273849", "primary": "#45B8F2", "primary2": "#0B5C91",
        "green": "#2ED79B", "shadow": "rgba(0,0,0,.34)", "input": "#101923",
    } if escuro else {
        "bg": "#F3F6F8", "surface": "#FFFFFF", "surface2": "#F7F9FB", "text": "#17212B",
        "muted": "#647381", "border": "#DDE5EA", "primary": "#075C91", "primary2": "#00AEEF",
        "green": "#078B62", "shadow": "rgba(25,58,82,.10)", "input": "#FFFFFF",
    })
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {{--app-bg:{p['bg']};--surface:{p['surface']};--surface-2:{p['surface2']};--text:{p['text']};--muted:{p['muted']};--border:{p['border']};--primary:{p['primary']};--green:{p['green']};}}
    html, body, [class*="css"] {{font-family:Inter,'Segoe UI',sans-serif;}}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{background:{p['bg']};color:{p['text']};}}
    .stAppDeployButton,[data-testid="stToolbar"],#MainMenu,footer {{display:none!important;}}
    .block-container {{max-width:1380px;padding:1rem 2rem 3rem;}}
    h1,h2,h3,h4,h5,h6,p,label,[data-testid="stWidgetLabel"] {{color:{p['text']}!important;}}
    [data-testid="stCaptionContainer"],small {{color:{p['muted']}!important;}}
    [data-testid="stVerticalBlockBorderWrapper"],.st-key-panel-consulta,.st-key-panel-simulacao {{background:{p['surface']};border:1px solid {p['border']}!important;border-radius:14px!important;box-shadow:0 8px 28px {p['shadow']};}}
    [data-baseweb="select"]>div,[data-baseweb="input"]>div,input,textarea {{background:{p['input']}!important;color:{p['text']}!important;border-color:{p['border']}!important;}}
    [data-testid="stExpander"] {{background:{p['surface']};border:1px solid {p['border']};border-radius:10px;}}
    [data-testid="stDataFrame"] {{border:1px solid {p['border']};border-radius:10px;overflow:hidden;}}
    [data-testid="stMetric"] {{background:{p['surface2']};border:1px solid {p['border']};border-radius:12px;padding:14px 16px;}}
    [data-testid="stMetricValue"] {{color:{p['primary']}!important;font-weight:800;letter-spacing:-.03em;}}
    [data-testid="stMetricLabel"] {{color:{p['muted']}!important;}}
    .stButton>button[kind="primary"],.stDownloadButton>button {{background:linear-gradient(135deg,{p['primary']},{p['primary2']});color:white;border:0;border-radius:9px;font-weight:700;box-shadow:0 5px 14px {p['shadow']};}}
    .stButton>button {{border-radius:9px;}}
    [data-baseweb="tab-list"] {{gap:8px;background:{p['surface']};padding:6px;border:1px solid {p['border']};border-radius:12px;}}
    [data-baseweb="tab"] {{border-radius:8px;padding:.65rem 1rem;}}
    .theme-row {{display:flex;justify-content:flex-end;align-items:center;min-height:8px;}}
    .brand-shell {{background:{p['surface']};border:1px solid {p['border']};border-radius:16px;box-shadow:0 10px 32px {p['shadow']};overflow:hidden;margin:.15rem 0 1.15rem;}}
    .brand-accent {{height:5px;background:linear-gradient(90deg,#00AEEF 0%,#075C91 52%,#0BB975 100%);}}
    .brand-main {{display:grid;grid-template-columns:190px 1fr 190px;align-items:center;gap:26px;padding:18px 24px;}}
    .brand-main .logo-pref,.brand-main .logo-project {{height:66px;max-width:180px;object-fit:contain;justify-self:center;background:#FFFFFF;padding:8px 12px;border-radius:11px;box-shadow:0 3px 12px rgba(0,0,0,.10);}}
    .brand-copy {{text-align:center;border-left:1px solid {p['border']};border-right:1px solid {p['border']};padding:3px 20px;}}
    .brand-copy .eyebrow {{font-size:.72rem;color:{p['primary']};font-weight:800;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px;}}
    .brand-copy h1 {{font-size:1.65rem;line-height:1.15;margin:0;color:{p['text']}!important;letter-spacing:-.025em;}}
    .brand-copy p {{font-size:.82rem;color:{p['muted']}!important;margin:7px 0 0;}}
    .section-kicker {{color:{p['primary']};font-size:.75rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin-bottom:-.4rem;}}
    .total-card {{background:linear-gradient(135deg,{p['surface2']},rgba(11,185,117,.10));border:1px solid {p['border']};border-left:5px solid {p['green']};padding:16px 20px;border-radius:12px;margin:.7rem 0 1rem;color:{p['muted']};}}
    .total-card strong {{display:block;font-size:1.9rem;color:{p['green']};letter-spacing:-.035em;margin-top:2px;}}
    .stale-box {{background:rgba(232,157,46,.10);border:1px solid rgba(232,157,46,.45);border-radius:10px;padding:11px 14px;color:{p['text']};margin:.7rem 0;}}
    @media(max-width:900px){{.block-container{{padding:.7rem .8rem 2rem}}.brand-main{{grid-template-columns:1fr;gap:10px}}.brand-copy{{border:0;border-top:1px solid {p['border']};border-bottom:1px solid {p['border']};padding:13px}}.brand-main .logo-pref,.brand-main .logo-project{{height:52px}}}}
    </style>
    """, unsafe_allow_html=True)


def cabecalho(base_dir: Path):
    prefeitura = _data_uri(base_dir / "assets" / "logo_prefeitura_rio_oficial.png")
    projeto = _data_uri(base_dir / "assets" / "logo_rio_energia_verde.png")
    logo_pref = f'<img class="logo-pref" src="{prefeitura}" alt="Prefeitura do Rio">' if prefeitura else ""
    logo_projeto = f'<img class="logo-project" src="{projeto}" alt="Projeto Rio de Energia Verde">' if projeto else ""
    st.markdown(f"""
    <div class="brand-shell">
      <div class="brand-accent"></div>
      <div class="brand-main">
        {logo_pref}
        <div class="brand-copy">
          <div class="eyebrow">Inteligência tarifária</div>
          <h1>Consulta de Tarifas ANEEL</h1>
          <p>Programa de Eficiência, Transição e Governança Energética · Revisão 17</p>
        </div>
        {logo_projeto}
      </div>
    </div>
    """, unsafe_allow_html=True)
