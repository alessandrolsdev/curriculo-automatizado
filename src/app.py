import streamlit as st
import os
import json
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
    DATA_PATH,
    TEMPLATE_PATH,
    OUTPUT_DIR,
)

# Carrega variáveis de ambiente
load_dotenv()

# --- Configuração Inicial da Página ---
# Deve ser a primeira instrução Streamlit no script.
st.set_page_config(
    page_title="Nexus AI Recruiter",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Estilização (CSS) ---
# Aplica estilos personalizados para interface moderna (Glassmorphism, Gradientes).
st.markdown(
    """
<style>
    /* Importando Fonte Google (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Reset Geral */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(15, 23, 42) 0%, rgb(10, 10, 10) 90%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }

    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Títulos Estilizados */
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(to right, #4ade80, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        padding-bottom: 1rem;
    }
    
    h2, h3 {
        color: #f8fafc !important;
        font-weight: 600;
    }

    /* Cards com efeito Glassmorphism */
    .css-1r6slb0, .css-12oz5g7 { 
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Input Text Area Customizado */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
        font-family: 'Consolas', 'Courier New', monospace; 
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5) !important;
    }

    /* Botão Principal (Gradiente) */
    div.stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    }

    /* Sidebar Customizada */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Saída JSON formatada */
    .stJson {
        background-color: #020617;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #1e293b;
    }
    
    /* Mensagem de Sucesso */
    .stSuccess {
        background-color: rgba(20, 83, 45, 0.2);
        border: 1px solid #22c55e;
        color: #4ade80;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=60)
    st.title("Nexus Control")
    st.markdown("---")

    st.markdown("### ⚙️ Seleção de Modelo")
    model_choice = st.radio(
        "Selecione o Modelo:",
        ["Auto-Pilot (Recomendado)", "Gemini 3 Pro", "Gemini 2.5 Flash"],
        index=0,
        help="O Auto-Pilot seleciona automaticamente o modelo mais adequado com fallback.",
    )

    st.markdown("---")
    st.markdown("### 📁 Status do Sistema")
    if os.getenv("GOOGLE_API_KEY"):
        st.success("API Conectada • Online")
    else:
        st.error("API Desconectada")

    st.markdown(
        f"<div style='font-size: 12px; color: #64748b; margin-top: 20px;'>Template: {os.path.basename(TEMPLATE_PATH)}</div>",
        unsafe_allow_html=True,
    )

# --- Interface Principal ---
st.markdown(
    "<h1>Nexus AI Recruiter <span style='font-size: 20px; vertical-align: middle; background-color: #3b82f6; color: white; padding: 5px 10px; border-radius: 20px;'>BETA</span></h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;'>Geração de currículos de alta performance powered by <b>Google Gemini</b>.</p>",
    unsafe_allow_html=True,
)

# Layout de Colunas
col1, col_space, col2 = st.columns([1, 0.1, 1])

with col1:
    st.markdown("### 🎯 Descrição da Vaga")
    st.markdown("Cole a descrição completa abaixo para análise.")

    job_description = st.text_area(
        label="Job Description",
        label_visibility="collapsed",
        height=450,
        placeholder="Ex: Senior Software Engineer @ Google...\n\nResponsibilities:\n- Build scalable systems...\n- Python & React experience...",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Analisar e Gerar Currículo", type="primary")

with col2:
    if generate_btn and job_description:
        # --- Processamento ---
        with st.status("🚀 Processando...", expanded=True) as status:
            try:
                # 1. Carregamento de Dados
                st.write("📂 Lendo Master Data...")
                master_data = load_data()
                time.sleep(0.5)

                # 2. Análise via IA
                st.write(f"🧠 Consultando {model_choice}...")

                # A lógica de seleção de modelo pode ser refinada no backend.
                # Atualmente, o Auto-Pilot gerencia o fallback.
                decision = get_ai_decision(job_description, master_data)

                st.write("💡 Definindo estratégia de conteúdo...")
                time.sleep(0.5)

                # 3. Geração do Documento
                st.write("📝 Gerando documento Word...")
                context = build_context_from_decision(decision, master_data)

                doc = DocxTemplate(TEMPLATE_PATH)
                doc.render(context)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"CV_Alessandro_{decision['selected_summary_key'].upper()}_{timestamp}.docx"
                save_path = os.path.join(OUTPUT_DIR, filename)
                doc.save(save_path)

                status.update(
                    label="✅ Processo Concluído!", state="complete", expanded=False
                )

                # --- Resultados ---
                st.balloons()

                st.markdown("### 💎 Estratégia Adotada")

                # Resumo da Decisão
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"**Perfil:** {decision['selected_summary_key'].title()}")
                with c2:
                    st.success(
                        f"**Skills:** {len(decision['skills_order'])} categorias priorizadas"
                    )

                st.markdown("**Projetos Selecionados:**")
                for proj_id in decision["selected_project_ids"]:
                    # Recupera título do projeto
                    proj_title = next(
                        (
                            p["title"]
                            for p in master_data["projects"]
                            if p["id"] == proj_id
                        ),
                        proj_id,
                    )
                    st.markdown(f"✅ `{proj_title}`")

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

            except Exception as e:
                status.update(label="❌ Erro no Processamento", state="error")
                st.error(f"Detalhes do erro: {str(e)}")

    elif generate_btn and not job_description:
        st.warning("⚠️ Por favor, insira a descrição da vaga.")

    else:
        # Estado Inicial
        st.markdown("### 🤖 Aguardando Entrada")
        st.info("Insira a descrição da vaga para iniciar a análise.")

        # Placeholder decorativo
        st.code(
            """
{
  "status": "ready",
  "system": "online"
}
        """,
            language="json",
        )
