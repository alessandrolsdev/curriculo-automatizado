import os
import json
import re
import hashlib
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from database import SessionLocal, get_profile_data, get_ai_cache, save_ai_cache

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configurações de Caminho
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "base_template.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Configuração do Modelo de IA (GEMINI 2.5 FLASH EXCLUSIVAMENTE)
MODEL_NAME = "gemini-2.5-flash"

# Garante que a pasta de output existe
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data() -> Dict[str, Any]:
    """
    Carrega dados do perfil do banco SQLite.
    Retorna estrutura compatível com o formato JSON antigo.

    Returns:
        Dicionário com dados do perfil, projetos e resumos
    """
    with SessionLocal() as db:
        return get_profile_data(db)


def clean_json_output(text):
    """
    Função cirúrgica para extrair JSON de respostas sujas da IA.
    Remove markdown, quebras de linha extras e acha o primeiro '{' e último '}'.
    """
    # Se por algum motivo o texto for uma lista, pega o primeiro item
    if isinstance(text, list):
        text = str(text[0]) if text else ""

    if not isinstance(text, str):
        text = str(text)

    # Remove blocos de código markdown
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)

    # Encontra o início e fim do objeto JSON
    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != 0:
        text = text[start:end]

    return text.strip()


def get_job_hash(job_description: str) -> str:
    """
    Gera hash MD5 da descrição da vaga para uso em cache.

    Args:
        job_description: Texto da descrição da vaga

    Returns:
        Hash MD5 em formato hexadecimal
    """
    return hashlib.md5(job_description.encode("utf-8")).hexdigest()


def get_ai_decision(
    job_description: str, master_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analisa a vaga usando o modelo Gemini 2.5 Flash.
    Implementa cache de decisões para evitar chamadas redundantes à API.

    Args:
        job_description: Descrição da vaga de emprego
        master_data: Dados do perfil e projetos

    Returns:
        Dicionário com decisão da IA (summary_key, skills_order, project_ids)
    """

    # Verifica cache primeiro
    job_hash = get_job_hash(job_description)

    with SessionLocal() as db:
        cached_decision = get_ai_cache(db, job_hash)

        if cached_decision:
            print("⚡ Cache HIT: Usando decisão anterior")
            return cached_decision

    print(f"🤖 Consultando modelo {MODEL_NAME}...")

    prompt_template = PromptTemplate(
        input_variables=["job_description", "master_data"],
        template="""
        ATUE COMO UM ENGENHEIRO DE CURRÍCULOS SÊNIOR.
        
        SEU OBJETIVO:
        Analisar a vaga abaixo e selecionar os 3 MELHORES projetos do meu portfólio para criar um currículo imbatível.

        VAGA:
        {job_description}

        MEU PORTFÓLIO (MASTER DATA):
        {master_data}

        REGRAS RÍGIDAS DE SAÍDA:
        1. Responda APENAS um JSON válido. 
        2. NÃO escreva nada antes ou depois do JSON.
        3. Estrutura do JSON:
        {{
            "selected_summary_key": "frontend" | "backend" | "fullstack" | "mobile" | "ai_engineer",
            "skills_order": ["Skill A", "Skill B", "Skill C", "Skill D", "Skill E"],
            "selected_project_ids": ["id_projeto_1", "id_projeto_2", "id_projeto_3"]
        }}

        JSON DE RESPOSTA:
        """,
    )

    try:
        # Configuração do Modelo (EXCLUSIVAMENTE GEMINI 2.5 FLASH)
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=0.0,  # Zero criatividade, máxima precisão
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=3,
            request_timeout=30,
        )

        # Invoca a IA
        chain = prompt_template | llm
        response = chain.invoke(
            {
                "job_description": job_description,
                "master_data": json.dumps(master_data, ensure_ascii=False),
            }
        )

        content = response.content
        cleaned_json = clean_json_output(content)
        decision = json.loads(cleaned_json)

        # Validação
        if "selected_project_ids" not in decision:
            raise ValueError("JSON incompleto recebido da IA")

        # Salva no cache
        with SessionLocal() as db:
            save_ai_cache(db, job_hash, decision)
            print("💾 Decisão salva no cache")

        return decision

    except Exception as e:
        error_msg = f"Erro ao consultar modelo de IA: {str(e)}"
        print(f"❌ {error_msg}")
        raise ConnectionError(error_msg)


def build_context_from_decision(decision, master_data):
    """
    Monta o dicionário final para o Jinja2 (DocxTemplate) usar.
    Versão CORRIGIDA para bater com o template Word.
    """
    # 1. Seleciona o Resumo
    summary_key = decision.get("selected_summary_key", "fullstack")
    summary_text = master_data["summaries"].get(
        summary_key, master_data["summaries"]["fullstack"]
    )

    # 2. Seleciona os Projetos (CORRIGIDO: proj.name e proj.techs)
    selected_projects = []
    all_projects = {p["id"].lower(): p for p in master_data["projects"]}

    for pid in decision["selected_project_ids"]:
        clean_id = pid.strip().lower()
        if clean_id in all_projects:
            proj = all_projects[clean_id]

            # Escolhe a melhor descrição
            best_desc = next(
                (d["text"] for d in proj["descriptions"] if d["focus"] == summary_key),
                None,
            )
            if not best_desc:
                best_desc = next(
                    (
                        d["text"]
                        for d in proj["descriptions"]
                        if d["focus"] == "fullstack"
                    ),
                    proj["descriptions"][0]["text"],
                )

            # CORRIGIDO: Usar 'name' e 'techs' ao invés de 'title' e 'tech'
            selected_projects.append(
                {
                    "name": proj["title"],  # Template espera 'name'
                    "techs": " | ".join(
                        proj["tech_stack"][:6]
                    ),  # Template espera 'techs'
                    "description": best_desc,
                }
            )

    # Fallback de segurança
    if not selected_projects:
        print("⚠️ AVISO: IDs da IA não encontrados. Usando projetos padrão de backup.")
        for proj in master_data["projects"][:3]:
            selected_projects.append(
                {
                    "name": proj["title"],
                    "techs": " | ".join(proj["tech_stack"][:6]),
                    "description": proj["descriptions"][0]["text"],
                }
            )

    # 3. Skills (CORRIGIDO: formato compatível com template)
    raw_skills = decision["skills_order"]

    # O template espera uma lista de categorias, vamos criar uma categoria única
    # com todas as skills (ou podemos categorizar futuramente)
    skills_formatted = [
        {"name": "Principais Competências", "list": " • ".join(raw_skills)}
    ]

    # 4. Education (CORRIGIDO: deve ser uma LISTA, não objeto único)
    education_list = master_data["profile"]["education"]  # Já é lista do banco

    # 5. Contexto Final (CORRIGIDO)
    context = {
        "name": master_data["profile"]["name"],
        "role_title": f"Desenvolvedor {summary_key.title().replace('Ai_', 'AI ').replace('_', ' ')}",
        # Dados de Contato
        "linkedin": master_data["profile"]["contact"]["linkedin"],
        "github": master_data["profile"]["contact"]["github"],
        "email": master_data["profile"]["contact"]["email"],
        "phone": master_data["profile"]["contact"]["phone"],
        "location": master_data["profile"]["contact"]["location"],
        "summary": summary_text,
        # CORRIGIDO: Skills no formato que o template espera
        "skills": skills_formatted,
        # CORRIGIDO: Education como lista
        "education": education_list,
        # CORRIGIDO: Projects com 'name' e 'techs'
        "selected_projects": selected_projects,
        "experience": {
            "role": "Estagiário de Tecnologia da Informação",
            "company": "Aegea Saneamento",
            "period": "Set 2022 - Set 2025",
            "bullets": [
                "Gerenciamento e configuração de ativos corporativos utilizando Microsoft Azure.",
                "Suporte na resolução de falhas de rede e sistemas em ambiente de grande escala.",
                "Atuação com metodologias ágeis no atendimento a chamados técnicos.",
            ],
        },
    }

    return context
