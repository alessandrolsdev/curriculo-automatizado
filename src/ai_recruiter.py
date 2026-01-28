import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from docxtpl import DocxTemplate

# Carrega as variáveis do .env (API Key)
load_dotenv()

# Configurações de Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "master_data.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "base_template.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ai_decision(job_description, master_data):
    """
    Envia a vaga para o Gemini com estratégia de Fallback Inteligente.
    Adapta a 'temperatura' conforme a geração do modelo (Gemini 3 vs 2.5).
    """
    # Ordem de tentativa baseada na sua documentação:
    # 1. Gemini 3 Pro (A Ferrari do Raciocínio)
    # 2. Gemini 3 Flash (Inteligente e Rápido)
    # 3. Gemini 2.5 Flash (O Backup Estável que sabemos que funciona)
    models_to_try = [
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
    ]

    projects_summary = [
        {"id": p["id"], "title": p["title"], "stack": p["tech_stack"]}
        for p in master_data["projects"]
    ]

    template = """
    Você é um Tech Recruiter Sênior e Especialista em ATS.
    
    SUA MISSÃO:
    Analise a DESCRIÇÃO DA VAGA abaixo e selecione os melhores dados do candidato.
    
    DADOS:
    - Resumos: {summary_keys}
    - Projetos: {projects_json}
    - Skills: {skills_keys}
    
    VAGA:
    "{job_description}"
    
    SAÍDA (JSON Puro):
    {{
        "selected_summary_key": "ex: backend",
        "selected_project_ids": ["id1", "id2", "id3"],
        "skills_order": ["cat1", "cat2"]
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
        print(f"🤖 Tentando analisar com: {model_name.upper()}...")

        try:
            # AJUSTE FINO DA DOCUMENTAÇÃO:
            # Gemini 3 exige temperatura padrão (1.0) para raciocinar bem.
            # Gemini 2.5 funciona melhor com temperatura baixa (0.2) para tarefas de extração.
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

            # Limpeza do JSON (às vezes a IA manda ```json no começo)
            json_str = (
                response.content.replace("```json", "").replace("```", "").strip()
            )

            print(f"✅ SUCESSO! Currículo gerado pelo {model_name.upper()}!")
            return json.loads(json_str)

        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                reason = "Modelo não liberado/encontrado"
            elif "429" in error_message:
                reason = "Sem cota gratuita (Limit Exceeded)"
            else:
                reason = "Erro desconhecido"

            # Loga o erro curto e tenta o próximo da lista
            print(f"⚠️  Falha no {model_name}. Motivo: {reason}...")
            continue

    raise Exception("❌ Todos os modelos falharam. Verifique sua API Key.")


def build_context_from_decision(decision, data):
    """
    Reconstrói o dicionário que o DocxTemplate precisa, baseado na decisão da IA.
    """
    context = {}

    # 1. Dados Pessoais e Educação (Fixos)
    context["name"] = data["profile"]["name"]
    context["location"] = data["profile"]["location"]
    context["phone"] = data["profile"]["phone"]
    context["email"] = data["profile"]["email"]
    context["linkedin"] = data["profile"]["linkedin"]
    context["github"] = data["profile"]["github"]
    context["education"] = data["education"]

    # 2. Resumo Escolhido pela IA
    key = decision["selected_summary_key"]
    context["role_title"] = f"Desenvolvedor {key.title()}"
    context["summary"] = data["profile"]["summaries"].get(
        key, data["profile"]["summaries"]["fullstack"]
    )

    # 3. Skills Reordenadas pela IA
    context["skills"] = []
    for skill_key in decision["skills_order"]:
        if skill_key in data["skills"]:
            context["skills"].append(
                {
                    "name": skill_key.replace("_", " & ").upper(),
                    "list": ", ".join(data["skills"][skill_key]),
                }
            )

    # 4. Projetos Selecionados pela IA
    context["selected_projects"] = []
    target_role = decision[
        "selected_summary_key"
    ]  # Usa o papel para escolher a descrição do projeto

    for proj_id in decision["selected_project_ids"]:
        # Busca o projeto completo no master_data pelo ID
        project = next((p for p in data["projects"] if p["id"] == proj_id), None)

        if project:
            # Tenta pegar a descrição focada na vaga (ex: descrição 'backend' para vaga backend)
            # Se não tiver, pega a primeira disponível
            desc_text = ""
            for desc in project["descriptions"]:
                if desc["focus"] == target_role:
                    desc_text = desc["text"]
                    break
            if not desc_text:
                desc_text = project["descriptions"][0]["text"]

            context["selected_projects"].append(
                {
                    "name": project["title"],
                    "techs": " | ".join(project["tech_stack"]),
                    "description": desc_text,
                }
            )

    # 5. Experiência (Mantemos a mais recente, filtrada por tags se quiser avançar depois)
    latest_job = data["experience"][0]
    # Filtro simples: Se a vaga é inglês, pega bullets em inglês
    bullets = []
    is_english = target_role == "english"

    for b in latest_job["description_bullets"]:
        if is_english and "text_en" in b:
            bullets.append(b["text_en"])
        elif not is_english and "text" in b:
            bullets.append(b["text"])

    context["experience"] = {
        "role": latest_job["role"],
        "company": latest_job["company"],
        "period": latest_job["period"],
        "bullets": bullets[:5],  # Top 5 bullets
    }

    return context


if __name__ == "__main__":
    # --- ÁREA DE TESTE (Konrad - Entry Level Software Developer) ---
    vaga_teste = """
    Who We Are
    Konrad is a next generation digital consultancy. We are dedicated to solving complex business problems for our global clients with creative and forward-thinking solutions. Our employees enjoy a culture built on innovation and a commitment to creating best-in-class digital products in use by hundreds of millions of consumers around the world. We hire exceptionally smart, analytical, and hard working people who are lifelong learners.

    About The Role
    As an entry level Software Developer you'll be tasked with working on both mobile and web applications. Working within the software development team, your duties will require you to assist in the development of consumer and enterprise applications. This role is ideal for entry level developers who feel confident in their technical ability and want to be a part of the highly-skilled development team at Konrad.

    What You'll Do
    Write maintainable, testable, and performant software in collaboration with our world class team 
    Participate in code review and performing extensive testing to ensure high quality software 
    Research new technology and tools and share those findings with the team
    Communicate clearly and effectively with all members of our team

    Qualifications (Implied from text above: Mobile/Web, Testing, Code Review)

    The estimated compensation for this position is $85,000 to $95,000.
    """

    data = load_data()

    # 1. IA decide
    decision = get_ai_decision(vaga_teste, data)
    print(f"🧠 Decisão da IA: {json.dumps(decision, indent=2)}")

    # 2. Python monta o contexto
    final_context = build_context_from_decision(decision, data)

    # 3. Docx gera o arquivo
    doc = DocxTemplate(TEMPLATE_PATH)
    doc.render(final_context)

    # Nome do arquivo com timestamp para não sobrescrever
    filename = f"CV_Konrad_Developer_{datetime.now().strftime('%H%M%S')}.docx"
    save_path = os.path.join(OUTPUT_DIR, filename)

    doc.save(save_path)
    print(f"🚀 Currículo gerado com sucesso: {save_path}")
