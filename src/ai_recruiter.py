"""
Módulo de integração com IA (Gemini 2.5 Flash)
Versão 8.2: ULTRA REFORÇADO - Validações Rígidas + i18n
"""

import os
import json
import re
import hashlib
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from database import SessionLocal, get_profile_data
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
    if isinstance(text, list):
        text = str(text[0])
    if not isinstance(text, str):
        text = str(text)

    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)

    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != 0:
        return text[start:end].strip()
    return text.strip()


def get_ai_decision(
    job_description: str,
    master_data: Dict[str, Any],
    force_language: Optional[str] = None,
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Engine V8.2: i18n + Strategic Selection + Validações ULTRA-RÍGIDAS

    Args:
        job_description: Descrição da vaga
        master_data: Dados do perfil
        force_language: Força idioma ("pt-BR" ou "en-US"). Se None, detecta.
        job_title: Título da vaga (ex: "Backend Developer", "Technical Support")
        company_name: Nome da empresa (ex: "Lenovo", "Google")
    """
    # Prepara instruções de idioma forçado
    lang_instruction = ""
    if force_language:
        lang_instruction = f"\n⚠️ IDIOMA FORÇADO: Use OBRIGATORIAMENTE language_code: '{force_language}'"
        print(f"🌍 Idioma FORÇADO: {force_language}")
    else:
        print(f"🌍 Engine V8.2 (Auto-Detect + Ultra-Validations)")

    # Prepara contexto adicional
    job_context = ""
    if job_title:
        job_context += f"\n📌 TÍTULO DA VAGA: {job_title}"
    if company_name:
        job_context += f"\n🏢 EMPRESA: {company_name}"

    # ==============================================================================
    # 🎯 PROMPT V8.2 - ULTRA REFORÇADO
    # ==============================================================================
    prompt_template = ChatPromptTemplate.from_template(
        """VOCÊ É ALESSANDRO. Escreva SEU currículo. NÃO fale SOBRE Alessandro.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ REGRAS INVIOLÁVEIS - VIOLAÇÃO = FALHA AUTOMÁTICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. NUNCA 3ª pessoa:
   ❌ "Alessandro se destaca" | "Alessandro possui" | "Alessandro Lima da Silva"
   ✅ Comece direto: "Estudante de Engenharia..."

2. FRASES 100% PROIBIDAS:
   ❌ "sólida base" | "se destaca" | "expertise" | "proficiente"
   ❌ "capacidade analítica" | "evidenciando" | "garantindo" | "otimizando"
   ❌ "solid background" | "stands out" | "extensive experience"

3. SUMÁRIO: UM parágrafo, MAX 550 chars
   Estrutura: [Formação + Experiência real] + [Skills concretas] + [Fit para vaga]

4. PROJETOS: SEMPRE honesto sobre serem de estudo
   ✅ "Projeto para aprender X: implementei Y. Domínio de Z."
   ❌ "garantindo desacoplamento" | "otimizando fundação"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 INPUTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VAGA: {job_description}{job_context}

MEU HISTÓRICO: {master_data}

🌍 IDIOMA:{force_language_instruction}
Analise idioma PREDOMINANTE da vaga:
- >70% INGLÊS → "en-US"
- >70% PORTUGUÊS → "pt-BR"
Keywords PT: "Buscamos", "requisitos", "será responsável"
Keywords EN: "We are looking", "requirements", "responsibilities"

⚠️ TODO conteúdo no MESMO idioma.
⚠️ SE FOR FORÇADO, USE O IDIOMA FORÇADO.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SUMÁRIO (ESTRUTURA OBRIGATÓRIA):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LINHA 1: Formação + Experiência real (suporte técnico Azure)
LINHA 2: Transição para desenvolvimento (Python, últimos 8 meses)
LINHA 3: Diferencial para ESSA vaga específica

❌ EXEMPLO ERRADO (3ª pessoa, corporativo):
"Engenheiro de Software com sólida base, Alessandro se destaca pela capacidade..."

✅ EXEMPLO CORRETO (direto, específico):
"Estudante de Engenharia de Software (formatura 03/2026) com 2+ anos em suporte técnico (Azure, troubleshooting, atendimento). Migrei para desenvolvimento Python nos últimos 8 meses. Esse background me deu comunicação clara, raciocínio lógico para resolver problemas e experiência com gestão de incidentes - essencial para [inserir fit com a vaga]."

TAMANHO: 400-550 chars. CONTE: ___ (preencha antes de retornar)

⚠️ Se >550 chars → DELETE adjetivos/redundâncias.
⚠️ Se múltiplos parágrafos → UNA em 1.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PROJETOS (EXATAMENTE 3):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESCOLHA baseado no TIPO de vaga:

📱 Frontend → Interactive Portfolio, Relay Flow, Pokédex
🔧 Backend → SaaS Mestre, RPG Task, NOMAD, CLUTCH
🌐 Fullstack → Arena Iron Beach, NOMAD, Banco New
🛠️ DevOps/Infra → AutoScan (automação), projetos com Docker
👨‍💼 Suporte Técnico → AutoScan (RPA), SaaS (Python), Clutch (troubleshooting)

FORMATO OBRIGATÓRIO:
"Projeto para [aprender X]: implementei [Y] com [techs]. Resultado: domínio de [skill]. Stack: A, B, C."

❌ PROIBIDO:
"garantindo desacoplamento" | "otimizando fundação" | "evidenciando habilidade"

✅ EXEMPLOS:
"Projeto para aprender automação: criei bot RPA com Python, OCR e Regex. Resultado: domínio de troubleshooting de pipelines. Stack: Python, Tesseract, Pandas."

"Projeto para praticar Clean Architecture: implementei API FastAPI com OAuth2. Resultado: domínio de arquitetura escalável. Stack: FastAPI, SQLAlchemy, Docker."

TAMANHO: 250-350 chars/projeto.
ANTES DE RETORNAR: CONTE projetos. Se >3 → DELETE até sobrar 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 SKILLS (CATEGORIAS CORRETAS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use ESTAS categorias (não invente):

Para vaga de DESENVOLVEDOR:
- "Linguagens": Python, JavaScript, TypeScript, Bash
- "Backend": FastAPI, NestJS, Django
- "Frontend": React, Next.js, Vue.js
- "Bancos de Dados": PostgreSQL, MongoDB, Redis
- "DevOps & Cloud": Docker, Git, CI/CD, Azure

Para vaga de SUPORTE/HELP DESK:
- "Suporte & Comunicação": Atendimento ao Cliente, Chat/Telefone, Troubleshooting
- "Conhecimento Técnico": Python (Básico), Bash, Linux, Azure
- "Ferramentas": Jira, Confluence, Ticketing Systems

⚠️ PRIORIZE skills da vaga (coloque primeiro).
❌ NÃO invente skills fora do histórico.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT JSON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "language_code": "pt-BR",
  "adapted_role_title": "Cargo | Stack + Diferencial",
  "custom_summary": "Texto 400-550 chars, 1 parágrafo...",
  "skills_categorized": {{
    "Categoria1": ["skill1", "skill2"],
    "Categoria2": ["skill3", "skill4"]
  }},
  "custom_projects": [
    {{
      "original_id": "project-id",
      "adapted_title": "Título do Projeto",
      "adapted_description": "Projeto para aprender X...",
      "tech_display": "Tech1 | Tech2 | Tech3"
    }}
    // EXATAMENTE 3 projetos
  ],
  "highlighted_techs": ["Tech1", "Tech2"],
  "project_selection_reasoning": "Escolhi esses 3 porque..."
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 CHECKLIST OBRIGATÓRIO (preencha ANTES de retornar):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Sumário NÃO tem "Alessandro" no meio do texto?
[ ] Sumário NÃO tem "sólida base", "se destaca", "expertise"?
[ ] Sumário tem 400-550 chars? (conte: ___ chars)
[ ] Sumário é UM parágrafo (sem múltiplas quebras)?
[ ] Projetos começam com "Projeto para..." ou "Construí para..."?
[ ] Projetos NÃO têm "garantindo", "otimizando", "evidenciando"?
[ ] Tenho EXATAMENTE 3 projetos (não 2, não 4)?
[ ] Skills são do histórico real (não inventadas)?
[ ] Idioma está correto?

Se QUALQUER = NÃO → REESCREVA até todos = SIM.

Agora crie o currículo autêntico.
"""
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=0.20,  # 🆕 Reduzido de 0.25 para 0.20 (mais conservador)
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=MAX_RETRIES,
            request_timeout=60,
        )

        chain = prompt_template | llm

        response = chain.invoke(
            {
                "job_description": job_description,
                "master_data": json.dumps(master_data, ensure_ascii=False),
                "force_language_instruction": lang_instruction,
                "job_context": job_context,
            }
        )

        content = response.content
        cleaned_json = clean_json_output(content)
        decision = json.loads(cleaned_json)

        # ========== VALIDAÇÃO V8.2 ULTRA-RÍGIDA ==========

        # Validação 1: Idioma obrigatório
        if "language_code" not in decision:
            print("⚠️ language_code ausente, assumindo pt-BR")
            decision["language_code"] = "pt-BR"

        # Se forçou, sobrescreve
        if force_language:
            decision["language_code"] = force_language
            print(f"✅ Idioma forçado: {force_language}")

        # Validação 2: Remover 3ª pessoa e frases proibidas do sumário
        if "custom_summary" in decision:
            summary = decision["custom_summary"]
            original_len = len(summary)

            # Remove nome completo
            summary = re.sub(
                r"Alessandro Lima da Silva\s+", "", summary, flags=re.IGNORECASE
            )
            summary = re.sub(
                r"Alessandro\s+(se |possui |tem |é |stands out|has )",
                "",
                summary,
                flags=re.IGNORECASE,
            )

            # Remove frases proibidas
            forbidden_replacements = {
                "sólida base": "base",
                "solid background": "background",
                "se destaca": "",
                "stands out": "",
                "expertise em": "experiência em",
                "expertise in": "experience in",
                "proficiente em": "conhecimento em",
                "proficient in": "knowledge in",
                "capacidade analítica": "raciocínio lógico",
                "analytical capacity": "logical reasoning",
                "evidenciando": "mostrando",
                "evidencing": "showing",
                "garantindo": "com",
                "ensuring": "with",
                "otimizando": "melhorando",
                "optimizing": "improving",
            }

            for forbidden, replacement in forbidden_replacements.items():
                if forbidden in summary.lower():
                    print(f"⚠️ Removendo: '{forbidden}'")
                    pattern = re.compile(re.escape(forbidden), re.IGNORECASE)
                    summary = pattern.sub(replacement, summary)

            # Remove espaços duplos
            summary = re.sub(r"\s+", " ", summary).strip()
            decision["custom_summary"] = summary

            if len(summary) != original_len:
                print(f"✅ Sumário corrigido: {original_len} → {len(summary)} chars")

        # Validação 3: Limitar a EXATAMENTE 3 projetos
        if "custom_projects" in decision:
            proj_count = len(decision["custom_projects"])
            if proj_count > 3:
                print(f"⚠️ Limitando {proj_count} → 3 projetos")
                decision["custom_projects"] = decision["custom_projects"][:3]
            elif proj_count < 3:
                print(f"⚠️ Apenas {proj_count} projetos (esperado: 3)")
        else:
            raise ValueError("IA falhou em gerar projetos.")

        # Validação 4: Unificar múltiplos parágrafos
        if "custom_summary" in decision:
            summary = decision["custom_summary"]
            if "\n\n" in summary:
                print(f"⚠️ Unificando múltiplos parágrafos...")
                summary = summary.replace("\n\n", " ").replace("\n", " ").strip()
                decision["custom_summary"] = summary

        # Validação 5: Verificar linguagem corporativa em projetos
        if "custom_projects" in decision:
            corporate_words = [
                "garantindo",
                "otimizando",
                "evidenciando",
                "capacitando",
                "ensuring",
                "optimizing",
                "evidencing",
            ]
            for i, proj in enumerate(decision["custom_projects"]):
                desc = proj.get("adapted_description", "").lower()
                found = [w for w in corporate_words if w in desc]
                if found:
                    print(f"⚠️ Projeto {i+1} tem linguagem corporativa: {found}")

        # Avisos finais
        summary_len = len(decision.get("custom_summary", ""))
        if summary_len > 600:
            print(f"⚠️ Sumário longo ({summary_len} chars). Ideal: 400-550.")

        lang_flag = "🇧🇷" if decision["language_code"] == "pt-BR" else "🇺🇸"
        print(
            f"✅ V8.2 {lang_flag} | {len(decision.get('custom_projects', []))} projetos | {summary_len} chars"
        )

        return decision

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        raise e


def build_context_from_decision(
    decision: Dict[str, Any], master_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Monta contexto com traduções i18n."""

    language_code = decision.get("language_code", "pt-BR")

    # 1. Título e Resumo
    role_title = decision.get("adapted_role_title", "Desenvolvedor Full Stack")
    summary_text = decision.get("custom_summary", master_data["summaries"]["fullstack"])

    # 2. Projetos
    selected_projects = []
    if "custom_projects" in decision:
        for proj in decision["custom_projects"]:
            selected_projects.append(
                {
                    "name": proj["adapted_title"],
                    "techs": proj["tech_display"],
                    "description": proj["adapted_description"],
                }
            )

    # 3. Skills
    skills_formatted = []
    if "skills_categorized" in decision:
        for cat_name, skills_list in decision["skills_categorized"].items():
            if skills_list:
                skills_formatted.append(
                    {"name": cat_name, "list": " • ".join(skills_list)}
                )

    # 4. Experiência TRADUZIDA
    experience_translated = translate_experience(language_code)

    # 5. Template dinâmico
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
        "languages": master_data["profile"]["languages"],
        "experience": experience_translated,
        "language_code": language_code,
        "template_path": template_path,
    }


def generate_cover_letter(
    job_description: str,
    master_data: Dict[str, Any],
    language_code: str = "pt-BR",
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Gera carta de apresentação humanizada."""

    projects_list = "\n".join(
        [
            f"- {p['id']}: {p['title']} ({', '.join(p['tech_stack'][:5])})"
            for p in master_data["projects"]
        ]
    )

    is_english = language_code == "en-US"
    greeting = "Hi!" if is_english else "Oi!"
    closing = "Best regards,\nAlessandro" if is_english else "Abraço,\nAlessandro"
    language = "ENGLISH" if is_english else "PORTUGUÊS"

    # Contexto adicional
    extra_context = ""
    if job_title:
        extra_context += f"\nTÍTULO DA VAGA: {job_title}"
    if company_name:
        extra_context += f"\nEMPRESA: {company_name}"

    prompt_template = ChatPromptTemplate.from_template(
        """Carta CURTA (180-250 palavras) para vaga.{extra_context}

VAGA: {job_description}
PROJETOS: {projects_list}

🚫 PROIBIDO:
"Venho por meio desta", "apaixonado", "vasta experiência", "seria uma honra"

✅ ESTRUTURA:
1. Gancho: "Vi a vaga e faz sentido candidatar. Vocês precisam de X..."
2. Contexto: "Comecei em suporte Azure, migrei para Python..."
3. Prova: "• **Projeto A** – Skill X"
4. Diferencial: "Background suporte = troubleshooting eficiente"
5. CTA: "Disponibilidade total. Fico à disposição."

SAUDAÇÃO: {greeting}
FECHAMENTO: {closing}
IDIOMA: {language}

OUTPUT JSON:
{{
  "subject_line": "Cargo - Alessandro (Diferencial)",
  "email_body": "Texto 180-250 palavras...",
  "word_count": 200
}}
"""
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=MAX_RETRIES,
            request_timeout=60,
        )

        chain = prompt_template | llm

        response = chain.invoke(
            {
                "job_description": job_description,
                "projects_list": projects_list,
                "greeting": greeting,
                "closing": closing,
                "language": language,
                "extra_context": extra_context,
            }
        )

        content = response.content
        cleaned_json = clean_json_output(content)
        result = json.loads(cleaned_json)

        if "email_body" not in result:
            raise ValueError("IA falhou em gerar corpo do email.")

        print(f"✅ Cover Letter: {result.get('word_count', 0)} palavras")

        return result

    except Exception as e:
        print(f"❌ Erro cover letter: {str(e)}")
        raise e
