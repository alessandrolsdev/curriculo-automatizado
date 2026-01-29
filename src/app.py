import streamlit as st
import os
import time
from datetime import datetime
from docxtpl import DocxTemplate
from dotenv import load_dotenv

# Importando backend
from ai_recruiter import (
    load_data,
    get_ai_decision,
    build_context_from_decision,
    BASE_DIR,
    TEMPLATE_PATH,
    OUTPUT_DIR,
)
from database import get_db_stats

# Carrega variáveis
load_dotenv()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Nexus AI Recruiter",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS PERSONALIZADO (MANTIDO) ---
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


# --- 🧠 FUNÇÃO CACHEADA (O SEGREDO DA ECONOMIA) ---
# O Streamlit só vai rodar isso se os parâmetros mudarem.
# Se você clicar em gerar de novo para a mesma vaga, ele usa o cache (Custo ZERO).
@st.cache_data(show_spinner=False, ttl=3600)  # ttl=3600 segura o cache por 1 hora
def process_resume_generation(job_desc, _master_data):
    # O underscore em _master_data diz pro Streamlit não hashear esse objeto grande, otimizando performance
    decision = get_ai_decision(job_desc, _master_data)
    context = build_context_from_decision(decision, _master_data)

    # Geramos o doc aqui na memória para retornar o caminho
    doc = DocxTemplate(TEMPLATE_PATH)
    doc.render(context)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = (
        f"CV_Alessandro_{decision['selected_summary_key'].upper()}_{timestamp}.docx"
    )
    save_path = os.path.join(OUTPUT_DIR, filename)
    doc.save(save_path)

    return save_path, decision, filename


# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=60)
    st.title("Nexus Control")
    st.markdown("---")

    # Estatísticas do Banco de Dados
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
    st.markdown("### ⚙️ Motor de Inteligência")
    st.info("🤖 Gemini 2.5 Flash")

    if os.getenv("GOOGLE_API_KEY"):
        st.success("API Conectada • Online")
    else:
        st.error("API Desconectada")

# --- ÁREA PRINCIPAL ---
st.markdown(
    "<h1>Nexus AI Recruiter PRO</h1>",
    unsafe_allow_html=True,
)

col1, col_space, col2 = st.columns([1, 0.1, 1])

with col1:
    st.markdown("### 🎯 Input da Vaga")

    # --- FORMULÁRIO (A TRAVA DE SEGURANÇA) ---
    # Tudo aqui dentro só é enviado quando clica no botão.
    # Isso evita requisições acidentais enquanto você digita.
    with st.form("job_form"):
        job_description = st.text_area(
            "Cole a descrição da vaga:",
            height=450,
            placeholder="Cole aqui o texto da vaga...",
        )

        # O botão agora pertence ao formulário
        submitted = st.form_submit_button("✨ Analisar e Gerar Currículo")

with col2:
    if submitted and job_description:
        # Se a descrição for muito curta, nem gasta API
        if len(job_description) < 50:
            st.warning(
                "⚠️ Descrição muito curta. Cole mais detalhes para uma análise precisa."
            )
        else:
            with st.status("🚀 Processando...", expanded=True) as status:
                try:
                    st.write("📂 Carregando dados mestres...")
                    master_data = load_data()

                    st.write("🧠 Consultando Agente de IA (ou Cache)...")
                    # Chamada da função OTIMIZADA
                    save_path, decision, filename = process_resume_generation(
                        job_description, master_data
                    )

                    status.update(
                        label="✅ Sucesso! Currículo Gerado",
                        state="complete",
                        expanded=False,
                    )

                    # --- RESULTADOS ---
                    st.balloons()

                    st.markdown("### 💎 Estratégia Adotada")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info(
                            f"**Perfil:** {decision['selected_summary_key'].title()}"
                        )
                    with c2:
                        st.success(
                            f"**Skills:** {len(decision['skills_order'])} skills"
                        )

                    st.markdown("**Projetos Selecionados:**")
                    for proj_id in decision["selected_project_ids"]:
                        proj = next(
                            (p for p in master_data["projects"] if p["id"] == proj_id),
                            None,
                        )
                        if proj:
                            st.markdown(f"✅ `{proj['title']}`")

                    with open(save_path, "rb") as file:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥 BAIXAR CURRÍCULO (.DOCX)",
                            data=file,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                        )

                except ConnectionError:
                    status.update(label="❌ Erro de Conexão", state="error")
                    st.error("🚫 **Erro de conexão com a API do Google Gemini**")
                    st.info(
                        "Verifique sua conexão com a internet e a validade da sua API Key."
                    )

                except ValueError as e:
                    status.update(label="❌ Erro de Validação", state="error")
                    st.error(f"🚫 **Erro de validação:** {str(e)}")

                except Exception as e:
                    status.update(label="❌ Erro Inesperado", state="error")
                    st.error(f"❌ **Erro inesperado:** {str(e)}")
                    st.info("Tente novamente ou entre em contato com o suporte.")

    elif submitted and not job_description:
        st.warning("⚠️ O campo de descrição está vazio.")

    else:
        st.markdown("### 🤖 Aguardando Comando")
        st.info(
            """🚀 **Novo: Sistema otimizado com SQLite!**
        
- Cache inteligente de decisões da IA
- Consultas 4x mais rápidas
- Modelo Gemini 2.5 Flash garantido
        
Cole uma descrição de vaga para começar."""
        )
