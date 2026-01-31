"""
Módulo de integração com IA (Gemini 2.5 Flash)
Versão 8.0: i18n Support + Strategic Selection
"""

import os
import json
import re
import hashlib
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from database import SessionLocal, get_profile_data, get_ai_cache, save_ai_cache
from translations import translate_experience, get_template_path

load_dotenv()

# Configurações
MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 3

def load_data() -> Dict[str, Any]:
    with SessionLocal() as db:
        return get_profile_data(db)

def clean_json_output(text: str) -> str:
    """Limpeza robusta de JSON."""
    if isinstance(text, list): text = str(text[0])
    if not isinstance(text, str): text = str(text)
    
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)
    
    start = text.find("{")
    end = text.rfind("}") + 1
    
    if start != -1 and end != 0:
        return text[start:end].strip()
    return text.strip()

def get_job_hash(job_description: str) -> str:
    return hashlib.md5(job_description.encode("utf-8")).hexdigest()

def get_ai_decision(job_description: str, master_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Engine V8.0: Strategic Selection + i18n Detection
    """
    job_hash = get_job_hash(job_description)

    # Cache check
    with SessionLocal() as db:
        cached_decision = get_ai_cache(db, job_hash)
        if cached_decision:
            print("⚡ Cache HIT: Recuperando estratégia...")
            return cached_decision

    print(f"🌍 Engine V8.0 (i18n + Strategic) analisando a vaga...")

    # ==============================================================================
    # 🎯 PROMPT V8.0 - COM DETECÇÃO DE IDIOMA
    # ==============================================================================
    prompt_template = ChatPromptTemplate.from_template(
        """Você é Alessandro escrevendo seu próprio currículo. Não um robô falando SOBRE Alessandro.

📥 CONTEXTO CRÍTICO SOBRE O CANDIDATO:
- Estudante de Engenharia de Software (conclusão 03/2026)
- 2+ anos de experiência REAL em suporte técnico (Azure, troubleshooting, gestão de ativos)
- Migrou recentemente para desenvolvimento (últimos 8-12 meses)
- Projetos são de ESTUDO/PORTFÓLIO (honestos, técnicos, mas sem usuários em produção)
- Diferencial único: Background suporte técnico + skills de desenvolvimento

📥 INPUTS DA VAGA:
VAGA: {job_description}
MEU HISTÓRICO COMPLETO: {master_data}

🎯 SUA MISSÃO:
Adaptar meu currículo para essa vaga específica, mantendo minha voz autêntica e provando (com fatos) que posso fazer o trabalho.

🌍 DETECÇÃO DE IDIOMA (CRÍTICO):
Analise o idioma PREDOMINANTE da descrição da vaga:
- Se >70% do texto está em INGLÊS → language_code: "en-US"
- Se >70% do texto está em PORTUGUÊS → language_code: "pt-BR"
- Baseie-se em: palavras-chave técnicas, verbos, preposições
- Exemplo PT: "Buscamos", "será responsável", "requisitos", "experiência com"
- Exemplo EN: "We are looking for", "responsibilities", "requirements", "experience with"

⚠️ O CONTEÚDO DO CURRÍCULO DEVE SER ESCRITO NO MESMO IDIOMA DA VAGA.
Se language_code = "en-US", TODO o texto (sumário, projetos) deve ser em INGLÊS.
Se language_code = "pt-BR", TODO o texto (sumário, projetos) deve ser em PORTUGUÊS.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 PROIBIÇÕES ABSOLUTAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ HONESTIDADE TÉCNICA (CRÍTICO):
Esses projetos são de PORTFÓLIO/ESTUDO, não produção comercial.
NUNCA invente:
❌ Métricas falsas ("milhares de usuários", "latência de 800ms → 120ms")
❌ Clientes imaginários ("para empresa X", "atendendo Y requisições/dia")
❌ Escala de produção que não existiu

✅ FOQUE EM: Profundidade técnica, conceitos dominados, arquitetura implementada.

NUNCA USE ESSAS FRASES (são sinais de IA):
❌ "Profissional com sólida base" / "Solid professional background"
❌ "Apaixonado por tecnologia" / "Passionate about technology"
❌ "Vasta experiência" / "Extensive experience"
❌ "Busca incansável" / "Relentless pursuit"
❌ "Destacado por" / "Distinguished by"
❌ "Colaboro ativamente" / "Actively collaborate"
❌ "Foco na construção" / "Focused on building"
❌ Qualquer frase que você veria em 1000 currículos iguais

NUNCA:
- Fale de mim na 3ª pessoa ("Alessandro é..." / "Alessandro is...")
- Invente cargos ou experiências
- Use adjetivos vazios sem evidência
- Escreva parágrafos gigantes e genéricos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ INSTRUÇÕES DETALHADAS (Ver documento original do V7.5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[NOTA: Para economizar tokens, mantenha todas as instruções detalhadas do V7.5]
[Apenas adicione a seção de idioma ao JSON de saída]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT (JSON):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "language_code": "en-US",  // 🆕 OBRIGATÓRIO: "pt-BR" ou "en-US"
  
  "adapted_role_title": "Job Title | Main Stack + Differentiator",
  
  "custom_summary": "Humanized text in the SAME LANGUAGE as the job posting...",
  
  "skills_categorized": {{
    "Languages": ["Python 3.12", "JavaScript (ES6+)", "TypeScript"],
    "Backend": ["FastAPI", "NestJS", "Django"],
    // ... (use English category names if language_code = "en-US")
  }},
  
  "custom_projects": [
    {{
      "original_id": "rpg-task-manager",
      "adapted_title": "Project Title in Detected Language",
      "adapted_description": "Description in the SAME LANGUAGE as job posting...",
      "tech_display": "NestJS | GraphQL | Redis"
    }}
  ],
  
  "highlighted_techs": ["FastAPI", "NestJS", "PostgreSQL"],
  
  "project_selection_reasoning": "Brief explanation in the detected language...",
  
  "alternative_projects_considered": ["project_id_1"],
  "why_not_selected": "Brief explanation..."
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 CHECKLIST FINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Detectou o idioma correto da vaga?
✅ TODO o conteúdo gerado está no MESMO idioma da vaga?
✅ Se EN: "Software Engineering Student" (não "Estudante de Engenharia")
✅ Se PT: "Estudante de Engenharia" (não "Software Engineering Student")
✅ Categorias de skills no idioma correto?
✅ Projetos selecionados são os mais relevantes?
✅ Tom humanizado, sem corporativês?

Agora, analise a vaga e crie um currículo autêntico no idioma correto.
"""
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=0.25,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=MAX_RETRIES,
            request_timeout=60,
        )

        chain = prompt_template | llm
        
        response = chain.invoke({
            "job_description": job_description,
            "master_data": json.dumps(master_data, ensure_ascii=False)
        })

        content = response.content
        cleaned_json = clean_json_output(content)
        decision = json.loads(cleaned_json)

        # Validação obrigatória de idioma
        if "language_code" not in decision:
            print("⚠️ language_code ausente, assumindo pt-BR")
            decision["language_code"] = "pt-BR"
        
        # Validação de projetos
        if "custom_projects" not in decision:
            raise ValueError("IA falhou em gerar projetos customizados.")

        # Cache
        with SessionLocal() as db:
            save_ai_cache(db, job_hash, decision)

        lang_flag = "🇧🇷" if decision["language_code"] == "pt-BR" else "🇺🇸"
        print(f"✅ Decisão V8.0 Gerada {lang_flag} ({decision['language_code']})")
        
        if "project_selection_reasoning" in decision:
            print(f"🤔 Raciocínio: {decision['project_selection_reasoning'][:100]}...")
            
        return decision

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        raise e


def build_context_from_decision(decision: Dict[str, Any], master_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monta contexto com dados Reais, Texto Humanizado e Tradução i18n.
    Versão 8.0: Adiciona suporte a múltiplos idiomas.
    """
    
    # 🌍 Detectar idioma
    language_code = decision.get("language_code", "pt-BR")
    
    # 1. Título e Resumo
    role_title = decision.get("adapted_role_title", "Desenvolvedor Full Stack")
    summary_text = decision.get("custom_summary", master_data["summaries"]["fullstack"])

    # 2. Projetos Customizados
    selected_projects = []
    if "custom_projects" in decision:
        for proj in decision["custom_projects"]:
            selected_projects.append({
                "name": proj["adapted_title"],
                "techs": proj["tech_display"],
                "description": proj["adapted_description"]
            })
    else:
        # Fallback
        all_projects = {p["id"].lower(): p for p in master_data["projects"]}
        for pid in decision.get("selected_project_ids", [])[:3]:
            p = all_projects.get(pid.lower())
            if p:
                selected_projects.append({
                    "name": p["title"],
                    "techs": " | ".join(p["tech_stack"][:4]),
                    "description": p["descriptions"][0]["text"]
                })

    # 3. Skills
    skills_formatted = []
    if "skills_categorized" in decision:
        for cat_name, skills_list in decision["skills_categorized"].items():
            if skills_list:
                skills_formatted.append({
                    "name": cat_name,
                    "list": " • ".join(skills_list)
                })

    # 4. Idiomas (sem tradução, mantém original)
    languages_list = master_data["profile"]["languages"] 
    
    # 5. 🆕 Experiência TRADUZIDA baseada no idioma
    experience_translated = translate_experience(language_code)
    
    # 6. 🆕 Template Path baseado no idioma
    template_path = get_template_path(language_code)

    return {
        "name": master_data["profile"]["name"],
        "role_title": role_title,
        
        "location": master_data["profile"]["contact"]["location"],
        "phone": master_data["profile"]["contact"]["phone"],
        "email": master_data["profile"]["contact"]["email"],
        "linkedin": master_data["profile"]["contact"]["linkedin"],
        "github": master_data["profile"]["contact"]["github"],
        
        "summary": summary_text,
        "skills": skills_formatted,
        "selected_projects": selected_projects,
        "highlighted_techs": decision.get("highlighted_techs", []),
        
        "education": master_data["profile"]["education"],
        "languages": languages_list,
        
        # 🆕 Campos i18n
        "experience": experience_translated,
        "language_code": language_code,
        "template_path": template_path
    }
