import streamlit as st
import os
import time
from datetime import datetime
from docxtpl import DocxTemplate
from dotenv import load_dotenv

# 🆕 Importa da versão V8 com i18n
from ai_service import (  # ou ai_service_v8 se não renomeou
    get_ai_decision,
    build_context_from_decision,
    load_data,
)
from database import get_db_stats

# Carrega variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 🆕 REMOVIDO: Template fixo (agora é dinâmico)
# TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "base_template.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Garante que a pasta de output existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Nexus AI Recruiter",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS PERSONALIZADO ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    .stApp { background: radial-gradient(circle at 10% 20%, rgb(15, 23, 42) 0%, rgb(10, 10, 10) 90%); font-family: 'Inter', sans-serif; color: #e2e8f0; }
    #MainMenu, footer, header {visibility: hidden;}
    h1 { font-weight: 800 !important; background: linear-gradient(to right, #4ade80, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stTextArea textarea { background-color: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #334155 !important; }
    div.stButton > button { background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; padding: 0.6rem 2rem; font-weight: 600; transition: all 0.3s ease; }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4); }
    .stSuccess { background-color: rgba(20, 83, 45, 0.2); border: 1px solid #22c55e; color: #4ade80; }
</style>
""",
    unsafe_allow_html=True,
)


# --- 🧠 FUNÇÃO DE GERAÇÃO (Atualizada V8) ---
@st.cache_data(show_spinner=False, ttl=3600)
def process_resume_generation(job_desc, _master_data):
    # 1. 🆕 IA Decide + Detecta Idioma
    decision = get_ai_decision(job_desc, _master_data)
    
    # 2. 🆕 Monta Contexto com Traduções
    context = build_context_from_decision(decision, _master_data)

    # 3. 🆕 Usa Template Dinâmico (PT ou EN)
    template_path = context["template_path"]
    language_code = context["language_code"]
    
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)

        # Gera nome de arquivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = decision.get("adapted_role_title", "Currículo").split("|")[0].strip().replace(" ", "_")
        
        # 🆕 Adiciona idioma no nome do arquivo
        lang_suffix = "EN" if language_code == "en-US" else "PT"
        filename = f"CV_Alessandro_{safe_title}_{lang_suffix}_{timestamp}.docx"
        
        save_path = os.path.join(OUTPUT_DIR, filename)
        doc.save(save_path)
        
        return save_path, decision, filename, language_code
        
    except Exception as e:
        raise RuntimeError(f"Erro ao renderizar/salvar DOCX: {str(e)}")


# --- SIDEBAR ---
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
    except Exception as e:
        st.warning("⚠️ Erro ao carregar estatísticas")

    st.markdown("---")
    # 🆕 Atualizado para V8
    st.markdown("### ⚙️ Motor V8")
    st.info("🤖 Ghostwriter + i18n Active")

    if os.getenv("GOOGLE_API_KEY"):
        st.success("API Conectada • Online")
    else:
        st.error("API Desconectada")

# --- ÁREA PRINCIPAL ---
st.markdown(
    # 🆕 Versão atualizada
    "<h1>Nexus AI Recruiter <span style='font-size:0.5em; vertical-align:top; color:#666'>v8.0</span></h1>",
    unsafe_allow_html=True,
)

col1, col_space, col2 = st.columns([1, 0.1, 1])

with col1:
    st.markdown("### 🎯 Input da Vaga")
    with st.form("job_form"):
        job_description = st.text_area(
            "Cole a descrição da vaga:",
            height=450,
            placeholder="Cole aqui o texto da vaga (PT ou EN)...",
        )
        submitted = st.form_submit_button("✨ Analisar e Gerar Currículo")

with col2:
    if submitted and job_description:
        if len(job_description) < 50:
            st.warning("⚠️ Descrição muito curta. Cole mais detalhes.")
        else:
            with st.status("🚀 Ghostwriter trabalhando...", expanded=True) as status:
                try:
                    st.write("📂 Carregando dados mestres...")
                    master_data = load_data()

                    st.write("🌍 Detectando idioma da vaga...")
                    st.write("✍️ IA Reescrevendo Perfil (Ghostwriting)...")
                    
                    # 🆕 Agora retorna language_code também
                    save_path, decision, filename, language_code = process_resume_generation(
                        job_description, master_data
                    )

                    status.update(
                        label="✅ Currículo Gerado com Sucesso!",
                        state="complete",
                        expanded=False,
                    )

                    # --- RESULTADOS ---
                    st.balloons()

                    # 🆕 Mostra idioma detectado
                    lang_flag = "🇧🇷" if language_code == "pt-BR" else "🇺🇸"
                    st.markdown(f"### {lang_flag} Idioma Detectado: **{language_code}**")

                    st.markdown("### 💎 Estratégia de Adaptação")
                    
                    # Exibe o Título Adaptado pela IA
                    adapted_title = decision.get('adapted_role_title', 'Fullstack Developer')
                    st.success(f"**Título Gerado:** {adapted_title}")

                    # Contagem de Skills
                    skills_count = 0
                    if 'skills_categorized' in decision:
                        skills_count = sum(len(v) for v in decision['skills_categorized'].values())
                    st.info(f"**Skills Injetadas:** {skills_count} competências")

                    st.markdown("**Projetos Reescritos:**")
                    if "custom_projects" in decision:
                        for proj in decision["custom_projects"]:
                            st.markdown(f"✅ `{proj['adapted_title']}`")
                    else:
                        for proj_id in decision.get("selected_project_ids", []):
                            st.markdown(f"✅ `ID: {proj_id}`")

                    # 🆕 Mostra raciocínio da seleção de projetos
                    if "project_selection_reasoning" in decision:
                        with st.expander("🤔 Por que esses projetos?"):
                            st.write(decision["project_selection_reasoning"])

                    # Botão de Download
                    with open(save_path, "rb") as file:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 BAIXAR CURRÍCULO (.DOCX)",
                            data=file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                        )
                        st.caption(f"Salvo em: `{save_path}`")

                except ConnectionError:
                    status.update(label="❌ Erro de Conexão", state="error")
                    st.error("Erro na API do Gemini. Verifique sua chave.")

                except ValueError as e:
                    status.update(label="❌ Erro de Validação", state="error")
                    st.error(f"Erro de validação: {str(e)}")

                except Exception as e:
                    status.update(label="❌ Erro Inesperado", state="error")
                    st.error(f"Erro inesperado: {str(e)}")

    elif submitted and not job_description:
        st.warning("⚠️ O campo de descrição está vazio.")

    else:
        st.markdown("### 🤖 Aguardando Comando")
        st.info(
            """🚀 **Sistema V8 Ghostwriter + i18n Pronto**
        
A IA irá:
1. 🌍 Detectar automaticamente o idioma da vaga (PT ou EN)
2. ✍️ Reescrever seu título profissional no idioma correto
3. 📝 Adaptar as descrições dos projetos
4. 🎯 Usar o template correto (PT-BR ou EN-US)
5. 💾 Gerar arquivo .docx na pasta `output/`
        
Cole uma descrição de vaga em **qualquer idioma** para começar."""
        )