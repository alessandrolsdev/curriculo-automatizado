"""
Nexus AI Recruiter — Interface Principal
=========================================
Versão 9.0: Awwwwwwards-level UI + Cover Letters + LangGraph Engine

Design System:
  • Tema escuro com fundo "deep space" (preto azulado)
  • Tipografia: Syne (títulos) + DM Sans (corpo)
  • Glassmorphism cards com bordas luminosas
  • Micro-animações CSS (glow, pulse, slide-in)
  • Layout 2 colunas: input | output
  • Status real-time durante geração

Fluxo:
  1. Usuário preenche: título, empresa, idioma, tipo de template
  2. Cola a descrição completa da vaga
  3. Escolhe: só currículo | só carta | ambos
  4. Download: .docx individual ou .zip combinado
"""

import json
import os
import zipfile
import time
from datetime import datetime
from io import BytesIO

import streamlit as st
from docxtpl import DocxTemplate
from dotenv import load_dotenv

from ai_recruiter import (
    load_data,
    get_ai_decision,
    build_context_from_decision,
    generate_cover_letter,
)
from database import get_db_stats

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus AI Recruiter",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: Awwwwwwards-level Design System ────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ═══ RESET & BASE ═══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

:root {
  --bg-void:       #050810;
  --bg-deep:       #080d1a;
  --bg-surface:    #0d1526;
  --bg-elevated:   #111d35;
  --bg-glass:      rgba(13, 21, 38, 0.72);

  --accent-blue:   #3b7bff;
  --accent-violet: #8b5cf6;
  --accent-cyan:   #06b6d4;
  --accent-green:  #10d98f;
  --accent-amber:  #f59e0b;
  --accent-rose:   #f43f5e;

  --text-primary:  #e8edf5;
  --text-secondary:#8fa3c0;
  --text-muted:    #4a6080;

  --glow-blue:    0 0 30px rgba(59,123,255,0.25);
  --glow-violet:  0 0 30px rgba(139,92,246,0.25);
  --glow-green:   0 0 30px rgba(16,217,143,0.25);

  --radius-sm:  8px;
  --radius-md:  14px;
  --radius-lg:  20px;
  --radius-xl:  28px;

  --font-display: 'Syne', sans-serif;
  --font-body:    'DM Sans', sans-serif;
}

/* ═══ APP ROOT ═══════════════════════════════════════════════════════════════ */
.stApp {
  background: var(--bg-void);
  background-image:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(59,123,255,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 110%, rgba(139,92,246,0.10) 0%, transparent 60%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Ccircle cx='1' cy='1' r='0.6' fill='rgba(255,255,255,0.03)'/%3E%3C/svg%3E");
  font-family: var(--font-body);
  color: var(--text-primary);
  min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px; }

/* ═══ SCROLLBAR ══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--accent-blue), var(--accent-violet));
  border-radius: 3px;
}

/* ═══ HERO HEADER ════════════════════════════════════════════════════════════ */
.nexus-hero {
  text-align: center;
  padding: 3rem 0 2rem;
  position: relative;
  overflow: hidden;
}
.nexus-hero::before {
  content: '';
  position: absolute;
  top: 0; left: 50%;
  transform: translateX(-50%);
  width: 600px; height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-blue), var(--accent-violet), transparent);
}
.nexus-hero h1 {
  font-family: var(--font-display) !important;
  font-size: 3.8rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em !important;
  line-height: 1.1 !important;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 40%, #06b6d4 100%);
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  margin-bottom: 0.5rem !important;
  animation: heroGlow 4s ease-in-out infinite;
}
@keyframes heroGlow {
  0%,100% { filter: drop-shadow(0 0 20px rgba(96,165,250,0.4)); }
  50%      { filter: drop-shadow(0 0 35px rgba(167,139,250,0.6)); }
}
.nexus-badge {
  display: inline-block;
  background: rgba(59,123,255,0.15);
  border: 1px solid rgba(59,123,255,0.35);
  color: #93c5fd;
  font-family: var(--font-display);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  margin-bottom: 1.5rem;
}

/* ═══ GLASS CARD ═════════════════════════════════════════════════════════════ */
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  margin-bottom: 1.25rem;
  position: relative;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
  border-color: rgba(59,123,255,0.25);
  box-shadow: var(--glow-blue);
}
.glass-card-title {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.glass-card-title::before {
  content: '';
  display: inline-block;
  width: 18px; height: 2px;
  background: var(--accent-blue);
  border-radius: 1px;
}

/* ═══ SECTION LABELS ═════════════════════════════════════════════════════════ */
.section-label {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 1.5rem 0 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.section-label .dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--accent-blue);
  box-shadow: 0 0 10px var(--accent-blue);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.5; transform: scale(0.8); }
}

/* ═══ INPUT FIELDS ═══════════════════════════════════════════════════════════ */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  background: rgba(8, 13, 26, 0.8) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body) !important;
  font-size: 0.92rem !important;
  transition: border-color 0.25s, box-shadow 0.25s;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(59,123,255,0.5) !important;
  box-shadow: 0 0 0 3px rgba(59,123,255,0.1) !important;
  outline: none !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {
  color: var(--text-secondary) !important;
  font-family: var(--font-body) !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
}

/* ═══ RADIO BUTTONS ══════════════════════════════════════════════════════════ */
div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
div[role="radiogroup"] label {
  background: rgba(13,21,38,0.8) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.5rem 1rem !important;
  font-size: 0.85rem !important;
  color: var(--text-secondary) !important;
  cursor: pointer;
  transition: all 0.2s ease;
}
div[role="radiogroup"] label:hover {
  border-color: rgba(59,123,255,0.4) !important;
  color: var(--text-primary) !important;
  background: rgba(59,123,255,0.08) !important;
}

/* ═══ SELECT BOX ══════════════════════════════════════════════════════════════ */
div[data-testid="stSelectbox"] > div > div {
  background: rgba(8,13,26,0.8) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
}

/* ═══ CHECKBOX ════════════════════════════════════════════════════════════════ */
div[data-testid="stCheckbox"] {
  background: rgba(13,21,38,0.6);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.9rem;
  margin: 0.3rem 0;
  transition: all 0.2s ease;
}
div[data-testid="stCheckbox"]:hover {
  border-color: rgba(59,123,255,0.25);
  background: rgba(59,123,255,0.05);
}
div[data-testid="stCheckbox"] label {
  color: var(--text-primary) !important;
  font-size: 0.9rem !important;
}

/* ═══ BUTTONS ════════════════════════════════════════════════════════════════ */
div.stButton > button {
  width: 100%;
  background: linear-gradient(135deg, #3b7bff 0%, #6d28d9 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  padding: 0.9rem 2rem;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.04em;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 24px rgba(59,123,255,0.28), 0 4px 8px rgba(0,0,0,0.4);
}
div.stButton > button::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, transparent 100%);
  pointer-events: none;
}
div.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 32px rgba(59,123,255,0.4), 0 6px 12px rgba(0,0,0,0.5);
}
div.stButton > button:active { transform: translateY(0); }

div.stDownloadButton > button {
  background: linear-gradient(135deg, #059669 0%, #0284c7 100%) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 24px rgba(5,150,105,0.3) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div.stDownloadButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 14px 32px rgba(5,150,105,0.45) !important;
}

/* ═══ FORM SUBMIT ════════════════════════════════════════════════════════════ */
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
div[data-testid="stForm"] button[kind="formSubmit"] {
  background: linear-gradient(135deg, #3b7bff 0%, #6d28d9 100%) !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  padding: 0.9rem 2rem !important;
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  letter-spacing: 0.04em !important;
  color: #fff !important;
  box-shadow: 0 8px 24px rgba(59,123,255,0.28) !important;
  transition: all 0.2s ease !important;
}

/* ═══ ALERTS ════════════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  border: none !important;
}
.stSuccess { background: rgba(16,185,129,0.1) !important; border-left: 3px solid #10b981 !important; }
.stInfo    { background: rgba(59,130,246,0.1) !important; border-left: 3px solid #3b82f6 !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border-left: 3px solid #f59e0b !important; }
.stError   { background: rgba(239,68,68,0.1)  !important; border-left: 3px solid #ef4444 !important; }

/* ═══ STATUS WIDGET ══════════════════════════════════════════════════════════ */
div[data-testid="stStatusWidget"] {
  background: var(--bg-elevated) !important;
  border: 1px solid rgba(59,123,255,0.2) !important;
  border-radius: var(--radius-md) !important;
}

/* ═══ METRICS ════════════════════════════════════════════════════════════════ */
div[data-testid="stMetricValue"] {
  font-family: var(--font-display) !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
}

/* ═══ SIDEBAR ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(5,8,16,0.98) 0%, rgba(8,13,26,0.98) 100%) !important;
  border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stMarkdown {
  color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .sidebar-logo {
  text-align: center;
  padding: 1.5rem 0 0.5rem;
}

/* ═══ RESULT CARDS ═══════════════════════════════════════════════════════════ */
.result-card {
  background: linear-gradient(135deg, rgba(13,21,38,0.9) 0%, rgba(8,13,26,0.9) 100%);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1rem;
  animation: slideIn 0.4s ease-out;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.result-title {
  font-family: var(--font-display);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}
.result-value {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
}

/* ═══ TECH TAG ════════════════════════════════════════════════════════════════ */
.tech-tag {
  display: inline-block;
  background: rgba(59,123,255,0.12);
  border: 1px solid rgba(59,123,255,0.25);
  color: #93c5fd;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  margin: 0.2rem 0.15rem;
  letter-spacing: 0.02em;
}

/* ═══ PROJECT ITEM ════════════════════════════════════════════════════════════ */
.project-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.project-item:last-child { border-bottom: none; }
.project-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--accent-green);
  flex-shrink: 0;
}
.project-name {
  font-family: var(--font-body);
  font-size: 0.88rem;
  color: var(--text-primary);
  font-weight: 500;
}

/* ═══ DIVIDER ════════════════════════════════════════════════════════════════ */
.nexus-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59,123,255,0.3), rgba(139,92,246,0.3), transparent);
  margin: 1.5rem 0;
  border: none;
}

/* ═══ EXPANDER ═══════════════════════════════════════════════════════════════ */
div[data-testid="stExpander"] > summary {
  background: rgba(13,21,38,0.6) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-body) !important;
  font-size: 0.88rem !important;
  color: var(--text-secondary) !important;
}

/* ═══ CAPTION ════════════════════════════════════════════════════════════════ */
.stCaption { color: var(--text-muted) !important; font-size: 0.78rem !important; }

/* ═══ SPINNER ════════════════════════════════════════════════════════════════ */
div[data-testid="stSpinner"] { color: var(--accent-blue) !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ── Helper Functions ─────────────────────────────────────────────────────────


def process_resume(
    job_desc: str,
    master_data: dict,
    force_language=None,
    job_title=None,
    company_name=None,
    template_type="dev",
):
    """Gera o currículo e salva o .docx."""
    decision = get_ai_decision(
        job_desc, master_data, force_language, job_title, company_name, template_type
    )
    ctx = build_context_from_decision(decision, master_data, template_type)
    template_path = ctx["template_path"]
    language_code = ctx["language_code"]

    doc = DocxTemplate(template_path)
    doc.render(ctx)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = (
        decision.get("adapted_role_title", "Curriculo")
        .split("|")[0]
        .strip()
        .replace(" ", "_")[:40]
    )
    lang_suffix = "EN" if language_code == "en-US" else "PT"
    tmpl_suffix = "Support" if template_type == "support" else "Dev"
    filename = f"CV_Alessandro_{safe_title}_{tmpl_suffix}_{lang_suffix}_{ts}.docx"
    save_path = os.path.join(OUTPUT_DIR, filename)
    doc.save(save_path)

    return save_path, decision, filename, language_code


def process_letter(
    job_desc: str,
    master_data: dict,
    language_code: str,
    job_title=None,
    company_name=None,
):
    """Gera a carta de apresentação e salva em .txt."""
    result = generate_cover_letter(
        job_desc, master_data, language_code, job_title, company_name
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    lang_suffix = "EN" if language_code == "en-US" else "PT"
    filename = f"CoverLetter_Alessandro_{lang_suffix}_{ts}.txt"
    save_path = os.path.join(OUTPUT_DIR, filename)

    body = f"Subject: {result['subject_line']}\n\n{result['email_body']}"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(body)

    return save_path, result, filename


def make_zip(cv_path: str, letter_path: str, job_title_safe: str) -> tuple:
    """Compacta currículo + carta em um único ZIP."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(cv_path, os.path.basename(cv_path))
        z.write(letter_path, os.path.basename(letter_path))
    buf.seek(0)
    fname = f"Nexus_Alessandro_{job_title_safe}_{datetime.now().strftime('%Y%m%d')}.zip"
    return buf.getvalue(), fname


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
    <div class="sidebar-logo">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="48" height="48" rx="14" fill="rgba(59,123,255,0.15)"/>
        <path d="M14 24L24 14L34 24L24 34L14 24Z" stroke="#3b7bff" stroke-width="2" fill="none"/>
        <path d="M20 24L24 20L28 24L24 28L20 24Z" fill="#8b5cf6"/>
        <circle cx="24" cy="24" r="3" fill="#3b7bff"/>
      </svg>
    </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### ⚡ Nexus Control")
    st.markdown(
        "<hr style='border:1px solid rgba(255,255,255,0.05);margin:0.5rem 0 1rem'>",
        unsafe_allow_html=True,
    )

    # Stats
    try:
        stats = get_db_stats()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Projetos", stats["total_projects"])
        with c2:
            st.metric("Skills", stats["total_skills"])
        st.metric("Resumos", stats["total_summaries"])
    except Exception:
        st.warning("⚠️ DB error")

    st.markdown(
        "<hr style='border:1px solid rgba(255,255,255,0.05);margin:1rem 0'>",
        unsafe_allow_html=True,
    )

    # Engine status
    st.markdown("**🔧 Engine V9.0**")
    features = [
        "LangGraph + auto-retry",
        "Markdown cleanup",
        "Dual-language detect",
        "Ultra-validations",
        "Cover letters (TI)",
    ]
    for f in features:
        st.markdown(
            f"<small style='color:#4a90e2'>✓</small> <small style='color:#8fa3c0'>{f}</small>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<hr style='border:1px solid rgba(255,255,255,0.05);margin:1rem 0'>",
        unsafe_allow_html=True,
    )

    api_ok = bool(os.getenv("GOOGLE_API_KEY"))
    if api_ok:
        st.success("🟢 Gemini 2.5 Flash — Online")
    else:
        st.error("🔴 GOOGLE_API_KEY not set")


# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="nexus-hero">
  <div class="nexus-badge">AI-Powered Resume Engine</div>
  <h1>Nexus AI Recruiter</h1>
  <p style="color:#8fa3c0;font-family:'DM Sans',sans-serif;font-size:1.05rem;margin-top:0.25rem">
    Currículo adaptado com IA · Gemini 2.5 Flash · LangGraph
  </p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='nexus-divider'></div>", unsafe_allow_html=True)

# ── Layout: 2 colunas ────────────────────────────────────────────────────────
col_input, col_gap, col_output = st.columns([1, 0.06, 1])

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA — INPUT
# ══════════════════════════════════════════════════════════════════════════════
with col_input:
    st.markdown(
        '<div class="section-label"><span class="dot"></span> Configuração da Vaga</div>',
        unsafe_allow_html=True,
    )

    # — Informações da vaga ——————————————————————————————————————————————————
    st.markdown(
        '<div class="glass-card"><div class="glass-card-title">📋 Informações da Vaga</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        job_title_input = st.text_input(
            "Título da Vaga",
            placeholder="ex: Backend Developer",
            help="Melhora a seleção de projetos e skills pela IA",
            key="job_title",
        )
    with c2:
        company_input = st.text_input(
            "Empresa",
            placeholder="ex: Nubank",
            help="Personaliza a carta de apresentação",
            key="company",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # — Idioma ————————————————————————————————————————————————————————————————
    st.markdown(
        '<div class="glass-card"><div class="glass-card-title">🌍 Idioma</div>',
        unsafe_allow_html=True,
    )
    language_mode = st.radio(
        "Modo de idioma:",
        [
            "🔍 Auto-detectar (recomendado)",
            "🇧🇷 Forçar Português (PT-BR)",
            "🇺🇸 Forçar Inglês (EN-US)",
        ],
        horizontal=False,
        key="language_mode",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # — Template Type ————————————————————————————————————————————————————————
    st.markdown(
        '<div class="glass-card"><div class="glass-card-title">📄 Tipo de Template</div>',
        unsafe_allow_html=True,
    )
    template_type_choice = st.radio(
        "Foco do currículo:",
        ["💻 Desenvolvedor (Dev)", "🛠️ Suporte / Help Desk"],
        help="Dev: foca em projetos e stack técnica. Suporte: inclui soft skills e experiência Azure.",
        key="template_type",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # — O que gerar ——————————————————————————————————————————————————————————
    st.markdown(
        '<div class="glass-card"><div class="glass-card-title">⚙️ O que Gerar</div>',
        unsafe_allow_html=True,
    )
    gen_resume = st.checkbox("📄 Currículo (.docx)", value=True, key="gen_resume")
    gen_letter = st.checkbox(
        "📧 Carta de Apresentação (.txt)", value=True, key="gen_letter"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # — Descrição da vaga ————————————————————————————————————————————————————
    st.markdown(
        '<div class="section-label"><span class="dot"></span> Descrição da Vaga</div>',
        unsafe_allow_html=True,
    )

    with st.form("job_form", clear_on_submit=False):
        job_description = st.text_area(
            "Cole aqui a descrição completa da vaga:",
            height=320,
            placeholder="Cole o texto completo da vaga. Quanto mais detalhado, melhor o resultado.\n\nExemplo:\nWe are looking for a Backend Developer with experience in Python and FastAPI...",
            key="job_desc",
        )
        submitted = st.form_submit_button(
            "⚡ Analisar e Gerar",
            use_container_width=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# COLUNA DIREITA — OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
with col_output:
    if not submitted:
        # Estado inicial: onboarding
        st.markdown(
            '<div class="section-label"><span class="dot"></span> Aguardando Input</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="glass-card">
          <div class="glass-card-title">🚀 Como usar</div>
          <ol style="color:#8fa3c0;font-size:0.9rem;line-height:1.9;padding-left:1.2rem;margin:0">
            <li>Preencha título e empresa <span style="color:#4a6080">(opcional mas recomendado)</span></li>
            <li>Escolha o idioma</li>
            <li>Selecione: Dev ou Suporte</li>
            <li>Marque o que deseja gerar</li>
            <li>Cole a descrição completa da vaga</li>
            <li>Clique em <strong style="color:#3b7bff">⚡ Analisar e Gerar</strong></li>
          </ol>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="glass-card">
          <div class="glass-card-title">✨ Novidades V9.0</div>
          <div style="color:#8fa3c0;font-size:0.88rem;line-height:2">
            <span style="color:#10d98f">✓</span> LangGraph state-machine com auto-retry<br>
            <span style="color:#10d98f">✓</span> Limpeza de **markdown** e ""artefatos""<br>
            <span style="color:#10d98f">✓</span> Detecção de idioma em 2 etapas<br>
            <span style="color:#10d98f">✓</span> Template Suporte com Soft Skills<br>
            <span style="color:#10d98f">✓</span> Cartas otimizadas para vagas TI<br>
            <span style="color:#10d98f">✓</span> Download ZIP (currículo + carta)
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    elif submitted and not job_description.strip():
        st.warning("⚠️ Cole a descrição da vaga antes de gerar.")

    elif submitted and len(job_description.strip()) < 50:
        st.warning("⚠️ Descrição muito curta. Cole o texto completo da vaga.")

    else:
        # ── Processamento ─────────────────────────────────────────────────
        force_language = None
        if "Português" in language_mode:
            force_language = "pt-BR"
        elif "Inglês" in language_mode:
            force_language = "en-US"

        template_type = "support" if "Suporte" in template_type_choice else "dev"

        with st.status(
            "⚡ Processando com Gemini 2.5 Flash...", expanded=True
        ) as status:
            try:
                t0 = time.time()
                st.write("📂 Carregando perfil...")
                master_data = load_data()

                # Context info
                if job_title_input or company_input:
                    parts = []
                    if job_title_input:
                        parts.append(f"Vaga: {job_title_input}")
                    if company_input:
                        parts.append(f"Empresa: {company_input}")
                    st.write(f"📌 {' • '.join(parts)}")

                lang_display = force_language or "auto"
                st.write(f"🌍 Idioma: {lang_display} | Template: {template_type}")

                # ── Gerar currículo ──────────────────────────────────────
                cv_path = cv_filename = decision = detected_lang = None
                if gen_resume:
                    st.write("🧠 IA reescrevendo perfil (LangGraph)...")
                    cv_path, decision, cv_filename, detected_lang = process_resume(
                        job_description,
                        master_data,
                        force_language,
                        job_title_input or None,
                        company_input or None,
                        template_type,
                    )
                    st.write(f"✅ Currículo gerado: {cv_filename}")

                # ── Gerar carta ──────────────────────────────────────────
                letter_path = letter_result = letter_filename = None
                if gen_letter:
                    lang_for_letter = detected_lang or force_language or "pt-BR"
                    st.write(f"📧 Gerando carta ({lang_for_letter})...")
                    letter_path, letter_result, letter_filename = process_letter(
                        job_description,
                        master_data,
                        lang_for_letter,
                        job_title_input or None,
                        company_input or None,
                    )
                    st.write(f"✅ Carta gerada: {letter_filename}")

                elapsed = time.time() - t0
                status.update(
                    label=f"✅ Concluído em {elapsed:.1f}s",
                    state="complete",
                    expanded=False,
                )

                # ════════════════════════════════════════════════════════
                # RESULTADOS
                # ════════════════════════════════════════════════════════
                st.balloons()
                st.markdown(
                    '<div class="section-label"><span class="dot"></span> Resultado</div>',
                    unsafe_allow_html=True,
                )

                # — Idioma detectado ——————————————————————————————————
                final_lang = detected_lang or lang_for_letter if gen_letter else "pt-BR"
                lang_flag = "🇧🇷" if final_lang == "pt-BR" else "🇺🇸"
                st.markdown(
                    f"""
                <div class="result-card" style="border-left:3px solid {'#3b7bff' if final_lang=='pt-BR' else '#06b6d4'}">
                  <div class="result-title">Idioma Detectado</div>
                  <div class="result-value">{lang_flag} {final_lang}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # — Info da vaga ————————————————————————————————————————
                if job_title_input or company_input:
                    badges = ""
                    if job_title_input:
                        badges += f'<span class="tech-tag">🎯 {job_title_input}</span>'
                    if company_input:
                        badges += f'<span class="tech-tag">🏢 {company_input}</span>'
                    st.markdown(
                        f'<div style="margin:0.5rem 0">{badges}</div>',
                        unsafe_allow_html=True,
                    )

                # — Currículo details ——————————————————————————————————
                if decision:
                    adapted_title = decision.get("adapted_role_title", "—")
                    st.markdown(
                        f"""
                    <div class="result-card">
                      <div class="result-title">Título Adaptado</div>
                      <div class="result-value">{adapted_title}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Skills count
                    skills_count = sum(
                        len(v) for v in decision.get("skills_categorized", {}).values()
                    )
                    proj_count = len(decision.get("custom_projects", []))

                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Skills", skills_count)
                    with c2:
                        st.metric("Projetos", proj_count)

                    # Projects list
                    projects_html = "".join(
                        [
                            f'<div class="project-item"><div class="project-dot"></div>'
                            f'<div class="project-name">{p["adapted_title"]}</div></div>'
                            for p in decision.get("custom_projects", [])
                        ]
                    )
                    st.markdown(
                        f"""
                    <div class="glass-card" style="padding:1rem 1.25rem">
                      <div class="glass-card-title">Projetos Selecionados</div>
                      {projects_html}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Techs highlighted
                    techs = decision.get("highlighted_techs", [])
                    if techs:
                        tags = "".join(
                            [f'<span class="tech-tag">{t}</span>' for t in techs]
                        )
                        st.markdown(
                            f"""
                        <div class="glass-card" style="padding:1rem 1.25rem">
                          <div class="glass-card-title">Techs em Destaque</div>
                          <div>{tags}</div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    # Reasoning expander
                    if decision.get("project_selection_reasoning"):
                        with st.expander("🤔 Por que esses projetos?"):
                            st.write(decision["project_selection_reasoning"])

                # — Carta preview ——————————————————————————————————————
                if letter_result:
                    with st.expander(f"📧 Preview da Carta ({final_lang})"):
                        st.markdown(f"**Assunto:** {letter_result['subject_line']}")
                        st.text(letter_result["email_body"])
                        wc = letter_result.get("word_count", "?")
                        st.caption(f"~{wc} palavras")

                # ════════════════════════════════════════════════════════
                # DOWNLOADS
                # ════════════════════════════════════════════════════════
                st.markdown("<div class='nexus-divider'></div>", unsafe_allow_html=True)
                st.markdown(
                    '<div class="section-label"><span class="dot"></span> Downloads</div>',
                    unsafe_allow_html=True,
                )

                if cv_path and letter_path:
                    # ZIP bundle
                    job_safe = (job_title_input or "Vaga").replace(" ", "_")[:30]
                    zip_data, zip_fname = make_zip(cv_path, letter_path, job_safe)
                    st.download_button(
                        label="📦 Baixar Pacote Completo (ZIP)",
                        data=zip_data,
                        file_name=zip_fname,
                        mime="application/zip",
                        use_container_width=True,
                        type="primary",
                        key="dl_zip",
                    )
                    st.caption(f"Contém: {cv_filename} + {letter_filename}")

                elif cv_path:
                    with open(cv_path, "rb") as f:
                        st.download_button(
                            label="📄 Baixar Currículo (.docx)",
                            data=f,
                            file_name=cv_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            type="primary",
                            key="dl_cv",
                        )

                elif letter_path:
                    with open(letter_path, "rb") as f:
                        st.download_button(
                            label="📧 Baixar Carta (.txt)",
                            data=f,
                            file_name=letter_filename,
                            mime="text/plain",
                            use_container_width=True,
                            type="primary",
                            key="dl_letter",
                        )

                st.caption(f"💾 Salvos em: `{OUTPUT_DIR}`")

            except FileNotFoundError as e:
                status.update(label="❌ Template não encontrado", state="error")
                st.error(
                    f"Template DOCX ausente: {e}\n\nVerifique a pasta `templates/`."
                )

            except RuntimeError as e:
                status.update(label="❌ Erro na Engine", state="error")
                st.error(f"Erro: {e}")
                if "API" in str(e) or "quota" in str(e).lower():
                    st.info("Verifique sua GOOGLE_API_KEY e os limites de quota.")

            except json.JSONDecodeError as e:
                status.update(label="❌ Erro de parsing JSON", state="error")
                st.error(f"A IA retornou JSON inválido após 3 tentativas: {e}")

            except Exception as e:
                status.update(label="❌ Erro inesperado", state="error")
                st.error(f"Erro inesperado: {type(e).__name__}: {e}")
