"""
Nexus AI Recruiter - Interface Web Principal
============================================

Este módulo implementa a interface Streamlit para o sistema de geração
automatizada de currículos com IA.

Funcionalidades Principais:
---------------------------
- Interface web moderna com design premium (glassmorphism, gradientes, animações)
- Geração de currículos personalizados baseados em descrição de vagas
- Geração opcional de cartas de apresentação
- Suporte multilíngue (PT-BR / EN-US) com auto-detecção
- Download em ZIP (currículo + carta)
- Validações ultra-rígidas de conteúdo

Fluxo de Uso:
------------
1. Usuário preenche informações da vaga (opcional: título, empresa)
2. Seleciona idioma (auto-detectar ou forçar PT/EN)
3. Marca opção de gerar carta de apresentação
4. Cola descrição completa da vaga
5. Sistema processa com IA (Gemini 2.5 Flash)
6. Download do pacote ZIP ou currículo individual

Arquitetura:
-----------
- Frontend: Streamlit com CSS customizado (300+ linhas)
- Backend: ai_recruiter.py (engine de IA)
- Database: SQLite via database.py (perfil, projetos, skills)
- Templates: DOCX com Jinja2

Autor: Alessandro Lima
Versão: 8.2 (UI/UX Premium + Cover Letters)
"""

import streamlit as st
import os
import zipfile
from datetime import datetime
from docxtpl import DocxTemplate
from dotenv import load_dotenv
from io import BytesIO

from ai_recruiter import (
    load_data,
    get_ai_decision,
    build_context_from_decision,
    generate_cover_letter,
)
from database import get_db_stats

load_dotenv()

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(
    page_title="Nexus AI Recruiter",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Personalizado
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* ========== GLOBAL STYLES ========== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: #f1f5f9;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ========== HIDE DEFAULT ELEMENTS ========== */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* ========== TYPOGRAPHY ========== */
    h1 {
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        margin-bottom: 2rem !important;
        animation: titleGlow 3s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(96, 165, 250, 0.3)); }
        50% { filter: drop-shadow(0 0 30px rgba(167, 139, 250, 0.5)); }
    }
    
    h2, h3 {
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        letter-spacing: -0.01em;
    }
    
    /* ========== INPUT FIELDS ========== */
    .stTextArea textarea,
    .stTextInput input {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.95rem;
    }
    
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: rgba(96, 165, 250, 0.6) !important;
        box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.1),
                    0 10px 25px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* ========== BUTTONS ========== */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2.5rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.025em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2),
                    0 4px 10px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    div.stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    div.stButton > button:hover::before {
        left: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4),
                    0 8px 15px rgba(0, 0, 0, 0.4);
    }
    
    div.stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* ========== DOWNLOAD BUTTON ========== */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border-radius: 12px;
        font-weight: 700;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div.stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.5);
    }
    
    /* ========== ALERTS & MESSAGES ========== */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 4px solid #10b981;
        border-radius: 12px;
        color: #6ee7b7;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        color: #93c5fd;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        color: #fcd34d;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        color: #fca5a5;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* ========== CUSTOM CONTAINERS ========== */
    .language-selector,
    .job-info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(96, 165, 250, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .language-selector:hover,
    .job-info-box:hover {
        border-color: rgba(96, 165, 250, 0.5);
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.2);
        transform: translateY(-2px);
    }
    
    /* ========== BADGES ========== */
    .info-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
        color: #6ee7b7;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }
    
    .info-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.25);
    }
    
    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* ========== METRICS ========== */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ========== RADIO BUTTONS ========== */
    div[role="radiogroup"] label {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        margin: 0.25rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    div[role="radiogroup"] label:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(96, 165, 250, 0.4);
        transform: translateY(-2px);
    }
    
    /* ========== FORM ========== */
    .stForm {
        background: rgba(15, 23, 42, 0.3);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* ========== CHECKBOX ========== */
    .stCheckbox {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .stCheckbox:hover {
        background: rgba(59, 130, 246, 0.1);
    }
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    
    /* ========== LOADING ANIMATION ========== */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* ========== CAPTION STYLING ========== */
    .caption {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 400;
    }
</style>
""",
    unsafe_allow_html=True,
)


def process_resume_generation(
    job_desc, master_data, force_language=None, job_title=None, company_name=None
):
    """Gera currículo com contexto adicional."""
    decision = get_ai_decision(
        job_desc, master_data, force_language, job_title, company_name
    )
    context = build_context_from_decision(decision, master_data)
    template_path = context["template_path"]
    language_code = context["language_code"]

    try:
        doc = DocxTemplate(template_path)
        doc.render(context)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = (
            decision.get("adapted_role_title", "Currículo")
            .split("|")[0]
            .strip()
            .replace(" ", "_")
        )
        lang_suffix = "EN" if language_code == "en-US" else "PT"
        filename = f"CV_Alessandro_{safe_title}_{lang_suffix}_{timestamp}.docx"
        save_path = os.path.join(OUTPUT_DIR, filename)
        doc.save(save_path)

        return save_path, decision, filename, language_code

    except Exception as e:
        raise RuntimeError(f"Erro ao renderizar DOCX: {str(e)}")


def process_cover_letter_generation(
    job_desc, master_data, language_code, job_title=None, company_name=None
):
    """Gera carta de apresentação."""
    try:
        result = generate_cover_letter(
            job_desc, master_data, language_code, job_title, company_name
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        lang_suffix = "EN" if language_code == "en-US" else "PT"
        filename = f"CoverLetter_Alessandro_{lang_suffix}_{timestamp}.txt"
        save_path = os.path.join(OUTPUT_DIR, filename)

        full_letter = f"""Assunto: {result['subject_line']}

{result['email_body']}
"""

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(full_letter)

        return save_path, result, filename

    except Exception as e:
        raise RuntimeError(f"Erro ao gerar carta: {str(e)}")


def create_zip_download(cv_path, letter_path, job_title_safe):
    """Cria arquivo ZIP com currículo e carta."""
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Adiciona currículo
        zip_file.write(cv_path, os.path.basename(cv_path))
        # Adiciona carta
        zip_file.write(letter_path, os.path.basename(letter_path))

    zip_buffer.seek(0)
    zip_filename = f"Candidatura_Alessandro_{job_title_safe}_{datetime.now().strftime('%Y%m%d')}.zip"

    return zip_buffer.getvalue(), zip_filename


# === SIDEBAR ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=60)
    st.title("Nexus Control")
    st.markdown("---")

    st.markdown("### 📊 Estatísticas")
    try:
        stats = get_db_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Projetos", stats["total_projects"])
        with col2:
            st.metric("Skills", stats["total_skills"])
        st.metric("Resumos", stats["total_summaries"])
    except Exception:
        st.warning("⚠️ Erro ao carregar estatísticas")

    st.markdown("---")
    st.markdown("### ⚙️ Motor V8.2")
    st.info("🤖 Ultra-Validations Active")

    if os.getenv("GOOGLE_API_KEY"):
        st.success("API Conectada • Online")
    else:
        st.error("API Desconectada")


# === ÁREA PRINCIPAL ===
st.markdown(
    "<h1>Nexus AI Recruiter <span style='font-size:0.5em; vertical-align:top; color:#666'>v8.2</span></h1>",
    unsafe_allow_html=True,
)

col1, col_space, col2 = st.columns([1, 0.1, 1])

with col1:
    st.markdown("### 🎯 Input da Vaga")

    # 🆕 Informações da Vaga
    st.markdown('<div class="job-info-box">', unsafe_allow_html=True)
    st.markdown("**📋 Informações da Vaga (Opcional):**")

    col_title, col_company = st.columns(2)
    with col_title:
        job_title_input = st.text_input(
            "Título da Vaga",
            placeholder="Ex: Backend Developer",
            help="Ajuda a IA entender o tipo de vaga (Backend, Frontend, Suporte, etc.)",
        )

    with col_company:
        company_input = st.text_input(
            "Empresa",
            placeholder="Ex: Lenovo",
            help="Nome da empresa (aparece na carta de apresentação)",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Seletor de idioma
    st.markdown('<div class="language-selector">', unsafe_allow_html=True)
    st.markdown("**🌍 Idioma do Currículo:**")

    language_mode = st.radio(
        "Selecione o modo:",
        ["🔍 Auto-detectar", "🇧🇷 Forçar Português", "🇺🇸 Forçar Inglês"],
        horizontal=True,
        help="Auto-detectar analisa a vaga. Forçar sobrescreve.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 🆕 Checkbox para carta
    generate_letter = st.checkbox(
        "📧 Gerar carta de apresentação",
        value=True,  # Marcado por padrão
        help="Gera carta junto com currículo (download único em ZIP)",
    )

    with st.form("job_form"):
        job_description = st.text_area(
            "Cole a descrição da vaga:",
            height=350,
            placeholder="Cole aqui o texto completo da vaga...",
        )
        submitted = st.form_submit_button(
            "✨ Analisar e Gerar", use_container_width=True
        )

with col2:
    if submitted and job_description:
        if len(job_description) < 50:
            st.warning("⚠️ Descrição muito curta. Cole mais detalhes.")
        else:
            # Determina idioma forçado
            force_language = None
            if language_mode == "🇧🇷 Forçar Português":
                force_language = "pt-BR"
            elif language_mode == "🇺🇸 Forçar Inglês":
                force_language = "en-US"

            with st.status("🚀 Processando...", expanded=True) as status:
                try:
                    st.write("📂 Carregando dados mestres...")
                    master_data = load_data()

                    # 🆕 Mostra contexto adicional
                    if job_title_input or company_input:
                        context_parts = []
                        if job_title_input:
                            context_parts.append(f"Vaga: {job_title_input}")
                        if company_input:
                            context_parts.append(f"Empresa: {company_input}")
                        st.write(f"📌 Contexto: {' | '.join(context_parts)}")

                    if force_language:
                        st.write(f"🌍 Idioma FORÇADO: {force_language}")
                    else:
                        st.write("🌍 Detectando idioma...")

                    st.write("✍️ IA reescrevendo perfil...")

                    # Gera currículo
                    cv_path, decision, cv_filename, detected_lang = (
                        process_resume_generation(
                            job_description,
                            master_data,
                            force_language,
                            job_title_input or None,
                            company_input or None,
                        )
                    )

                    # Gera carta se marcado
                    letter_data = None
                    if generate_letter:
                        st.write("📧 Gerando carta...")
                        letter_path, letter_result, letter_filename = (
                            process_cover_letter_generation(
                                job_description,
                                master_data,
                                detected_lang,
                                job_title_input or None,
                                company_input or None,
                            )
                        )
                        letter_data = (letter_path, letter_result, letter_filename)

                    status.update(
                        label="✅ Geração Completa!", state="complete", expanded=False
                    )

                    # === RESULTADOS ===
                    st.balloons()

                    # Badges informativos
                    lang_flag = "🇧🇷" if detected_lang == "pt-BR" else "🇺🇸"
                    st.markdown(f"### {lang_flag} Idioma: **{detected_lang}**")

                    if job_title_input:
                        st.markdown(
                            f'<div class="info-badge">🎯 {job_title_input}</div>',
                            unsafe_allow_html=True,
                        )
                    if company_input:
                        st.markdown(
                            f'<div class="info-badge">🏢 {company_input}</div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown("### 💎 Estratégia")

                    adapted_title = decision.get(
                        "adapted_role_title", "Fullstack Developer"
                    )
                    st.success(f"**Título:** {adapted_title}")

                    skills_count = sum(
                        len(v) for v in decision.get("skills_categorized", {}).values()
                    )
                    st.info(f"**Skills:** {skills_count} competências")

                    st.markdown("**Projetos:**")
                    for proj in decision.get("custom_projects", []):
                        st.markdown(f"✅ `{proj['adapted_title']}`")

                    if "project_selection_reasoning" in decision:
                        with st.expander("🤔 Por que esses projetos?"):
                            st.write(decision["project_selection_reasoning"])

                    # 🆕 DOWNLOAD ÚNICO EM ZIP (se carta marcada)
                    st.markdown("<br>", unsafe_allow_html=True)

                    if letter_data:
                        # Download ZIP com ambos
                        letter_path, _, _ = letter_data
                        job_title_safe = (job_title_input or "Vaga").replace(" ", "_")

                        zip_data, zip_filename = create_zip_download(
                            cv_path, letter_path, job_title_safe
                        )

                        st.download_button(
                            label="📦 Baixar Pacote Completo (Currículo + Carta)",
                            data=zip_data,
                            file_name=zip_filename,
                            mime="application/zip",
                            type="primary",
                            use_container_width=True,
                            key="download_zip",
                        )

                        st.caption(f"📁 Contém: {cv_filename} + {letter_data[2]}")

                    else:
                        # Download só currículo
                        with open(cv_path, "rb") as file:
                            st.download_button(
                                label="📥 Baixar Currículo (.docx)",
                                data=file,
                                file_name=cv_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                type="primary",
                                use_container_width=True,
                                key="download_cv",
                            )

                    st.caption(f"💾 Arquivos salvos em: `{OUTPUT_DIR}`")

                except ConnectionError:
                    status.update(label="❌ Erro de Conexão", state="error")
                    st.error("Erro na API do Gemini. Verifique sua chave.")

                except ValueError as e:
                    status.update(label="❌ Erro de Validação", state="error")
                    st.error(f"Erro: {str(e)}")

                except Exception as e:
                    status.update(label="❌ Erro Inesperado", state="error")
                    st.error(f"Erro: {str(e)}")

    elif submitted and not job_description:
        st.warning("⚠️ O campo está vazio.")

    else:
        st.markdown("### 🤖 Aguardando Input")
        st.info(
            """🚀 **Sistema V8.2 Ultra-Validado**
        
**Novidades V8.2:**
✅ Campo de título da vaga (ajuda IA entender tipo)
✅ Campo de empresa (personaliza carta)
✅ Download único em ZIP (currículo + carta juntos)
✅ Validações ultra-rígidas (remove frases proibidas)
✅ Temperatura reduzida (0.15 = mais conservador)

**Como usar:**
1. [Opcional] Preencha título e empresa
2. Escolha modo de idioma
3. Marque checkbox para carta
4. Cole descrição da vaga
5. Baixe pacote ZIP completo

**Exemplo:**
- Título: "Backend Developer"
- Empresa: "Lenovo"
- Carta marcada → Download: ZIP com currículo.docx + carta.txt

Cole uma descrição para começar!"""
        )
