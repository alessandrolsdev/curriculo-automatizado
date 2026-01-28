"""
Módulo AI Recruiter
===================

Este módulo gerencia a interação com a Google Gemini AI para análise de vagas
e geração de currículos otimizados.

Responsabilidades:
    - Carregar dados mestre (Master Data).
    - Decidir a melhor estratégia de currículo baseada na descrição da vaga.
    - Construir o contexto para renderização do template DOCX.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Union

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from docxtpl import DocxTemplate

# Carrega variáveis de ambiente
load_dotenv()

# --- Configurações e Constantes ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "master_data.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "base_template.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_data() -> Dict[str, Any]:
    """
    Carrega o arquivo JSON contendo os dados mestre do candidato.

    Returns:
        Dict[str, Any]: Dicionário com os dados carregados do arquivo master_data.json.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        json.JSONDecodeError: Se o arquivo não for um JSON válido.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ai_decision(
    job_description: str, master_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analisa a descrição da vaga utilizando IA (Gemini) para selecionar
    os projetos, skills e resumo mais adequados.

    Implementa estratégia de fallback tentando diferentes modelos em ordem de capacidade.

    Args:
        job_description (str): Texto completo da descrição da vaga.
        master_data (Dict[str, Any]): Dados mestre do candidato.

    Returns:
        Dict[str, Any]: Dicionário contendo a decisão da IA com as seguintes chaves:
            - selected_summary_key (str): Chave do resumo escolhido (ex: 'backend').
            - selected_project_ids (List[str]): Lista de IDs dos projetos selecionados.
            - skills_order (List[str]): Lista ordenada de categorias de skills.

    Raises:
        Exception: Se todos os modelos falharem na análise.
    """
    # Ordem de prioridade dos modelos
    models_to_try = [
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
    ]

    projects_summary = [
        {"id": p["id"], "title": p["title"], "stack": p["tech_stack"]}
        for p in master_data["projects"]
    ]

    # Template do Prompt
    template = """
    Você é um Tech Recruiter Sênior e Especialista em ATS.
    
    OBJETIVO:
    Analise a DESCRIÇÃO DA VAGA abaixo e selecione os dados mais relevantes do candidato para otimizar o currículo.
    
    DADOS DO CANDIDATO:
    - Perfis Disponíveis: {summary_keys}
    - Projetos: {projects_json}
    - Categorias de Skills: {skills_keys}
    
    DESCRIÇÃO DA VAGA:
    "{job_description}"
    
    OUTPUT ESPERADO (JSON):
    {{
        "selected_summary_key": "string (ex: backend, fullstack)",
        "selected_project_ids": ["string", "string", ...],
        "skills_order": ["string", "string", ...]
    }}
    """

    prompt = PromptTemplate(
        input_variables=[
            "summary_keys",
            "projects_json",
            "skills_keys",
            "job_description",
        ],
        template=template,
    )

    for model_name in models_to_try:
        print(f"🤖 Tentando análise com: {model_name}...")

        try:
            # Ajuste de temperatura conforme modelo
            # Modelos mais 'raciocinadores' (Pro) funcionam bem com temp padrão.
            # Modelos menores (Flash) podem precisar de menor temperatura para consistência JSON.
            current_temp = 1.0 if "gemini-3" in model_name else 0.2

            llm = ChatGoogleGenerativeAI(model=model_name, temperature=current_temp)
            chain = prompt | llm

            response = chain.invoke(
                {
                    "summary_keys": list(master_data["profile"]["summaries"].keys()),
                    "projects_json": json.dumps(projects_summary),
                    "skills_keys": list(master_data["skills"].keys()),
                    "job_description": job_description,
                }
            )

            # Limpeza do Markdown JSON, se presente
            json_str = (
                response.content.replace("```json", "").replace("```", "").strip()
            )

            print(f"✅ Análise concluída com sucesso via {model_name}!")
            return json.loads(json_str)

        except Exception as e:
            error_message = str(e)
            reason = "Erro desconhecido"
            if "404" in error_message:
                reason = "Modelo não encontrado/disponível"
            elif "429" in error_message:
                reason = "Limite de requisições excedido"

            print(f"⚠️ Falha no modelo {model_name}: {reason}")
            continue

    raise Exception("Falha crítica: Todos os modelos disponíveis falharam na análise.")


def build_context_from_decision(
    decision: Dict[str, Any], data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Constrói o contexto final para o template Jinja2 (DocxTemplate) baseado na decisão da IA.

    Args:
        decision (Dict[str, Any]): Saída da função get_ai_decision.
        data (Dict[str, Any]): Dados mestre.

    Returns:
        Dict[str, Any]: Contexto pronto para renderização.
    """
    context = {}

    # 1. Dados Pessoais (Fixos)
    profile = data["profile"]
    context.update(
        {
            "name": profile["name"],
            "location": profile["location"],
            "phone": profile["phone"],
            "email": profile["email"],
            "linkedin": profile["linkedin"],
            "github": profile["github"],
            "education": data["education"],
        }
    )

    # 2. Resumo Profissional
    key = decision["selected_summary_key"]
    # Fallback para 'fullstack' se a chave alucinada não existir
    context["role_title"] = f"Desenvolvedor {key.title()}"
    context["summary"] = profile["summaries"].get(
        key, profile["summaries"]["fullstack"]
    )

    # 3. Skills (Ordenadas pela IA)
    context["skills"] = []
    for skill_key in decision["skills_order"]:
        if skill_key in data["skills"]:
            context["skills"].append(
                {
                    "name": skill_key.replace("_", " & ").upper(),
                    "list": ", ".join(data["skills"][skill_key]),
                }
            )

    # 4. Projetos Selecionados
    context["selected_projects"] = []
    target_role = key  # Usa o perfil escolhido para filtrar descrições do projeto

    for proj_id in decision["selected_project_ids"]:
        project = next((p for p in data["projects"] if p["id"] == proj_id), None)

        if project:
            # Seleciona a descrição mais adequada ao perfil
            desc_text = ""
            for desc in project["descriptions"]:
                if desc["focus"] == target_role:
                    desc_text = desc["text"]
                    break

            # Fallback para a primeira descrição
            if not desc_text and project["descriptions"]:
                desc_text = project["descriptions"][0]["text"]

            context["selected_projects"].append(
                {
                    "name": project["title"],
                    "techs": " | ".join(project["tech_stack"]),
                    "description": desc_text,
                }
            )

    # 5. Experiência Profissional
    # Lógica atual: Pega apenas a mais recente.
    # TODO: Expandir para selecionar experiências baseadas na relevância.
    latest_job = data["experience"][0]

    bullets = []
    is_english = target_role == "english" or "english" in target_role.lower()

    for b in latest_job["description_bullets"]:
        if is_english and "text_en" in b:
            bullets.append(b["text_en"])
        elif not is_english and "text" in b:
            bullets.append(b["text"])

    context["experience"] = {
        "role": latest_job["role"],
        "company": latest_job["company"],
        "period": latest_job["period"],
        "bullets": bullets[:5],  # Limita as top 5 bullets
    }

    return context


if __name__ == "__main__":
    # --- Exemplo de Uso (Teste Isolado) ---
    print("--- Iniciando Teste Isolado do Recrutador IA ---")

    # Exemplo de Vaga
    VAGA_TESTE = """
    Vaga: Python Backend Developer
    Requisitos: Experiência com APIs REST, Django/FastAPI, Docker e Cloud AWS.
    Desejável: Conhecimento em IA e LLMs.
    """

    try:
        master_data = load_data()

        # 1. Simula Decisão da IA
        decision = get_ai_decision(VAGA_TESTE, master_data)
        print(f"\n🧠 Decisão da IA:\n{json.dumps(decision, indent=2)}")

        # 2. Constrói Contexto
        final_context = build_context_from_decision(decision, master_data)

        # 3. Gera Arquivo
        doc = DocxTemplate(TEMPLATE_PATH)
        doc.render(final_context)

        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"CV_TESTE_{timestamp}.docx"
        save_path = os.path.join(OUTPUT_DIR, filename)

        # Garante que o diretório de saída existe
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc.save(save_path)
        print(f"\n🚀 Currículo de teste gerado: {save_path}")

    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
