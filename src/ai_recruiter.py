"""
Nexus AI Recruiter — Engine V9.0
=================================
Melhorias sobre V8.2:
  • LangGraph state-machine com retry automático por nó
  • Limpeza agressiva de artefatos Markdown (**bold**, ""quotes"", etc.)
  • Detecção de idioma em dois passos (heurística + LLM fallback)
  • Suporte a template_type: "dev" | "support"
  • Carta de apresentação com estrutura comprovada para TI
  • Validações ultra-rígidas encapsuladas em helpers reutilizáveis
"""

import os
import json
import re
from typing import Any, Dict, List, Optional, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from database import SessionLocal, get_profile_data
from translations import translate_experience, get_template_path, get_soft_skills, get_labels

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 3
TEMPERATURE = 0.18


# ── Helpers ─────────────────────────────────────────────────────────────────

def _llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_retries=MAX_RETRIES,
        request_timeout=90,
    )


def load_data() -> Dict[str, Any]:
    with SessionLocal() as db:
        return get_profile_data(db)


def clean_json_output(text: str) -> str:
    """Remove wrappers Markdown do output da LLM antes de parsear JSON."""
    if isinstance(text, list):
        text = str(text[0])
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > 0:
        return text[start:end].strip()
    return text.strip()


# ── Text sanitisation ───────────────────────────────────────────────────────

_FORBIDDEN_PAIRS: List[tuple] = [
    # corporativês PT
    ("sólida base",           "base"),
    ("sólido conhecimento",   "conhecimento"),
    ("se destaca",            ""),
    ("se destaca pela",       ""),
    ("expertise em",          "experiência em"),
    ("expertise in",          "experience in"),
    ("proficiente em",        "com conhecimento em"),
    ("proficient in",         "with knowledge of"),
    ("capacidade analítica",  "raciocínio lógico"),
    ("analytical capacity",   "logical reasoning"),
    ("evidenciando",          "demonstrando"),
    ("evidencing",            "demonstrating"),
    ("garantindo",            "com"),
    ("ensuring",              "with"),
    ("otimizando",            "melhorando"),
    ("optimizing",            "improving"),
    ("habilidades sólidas",   "habilidades"),
    ("solid background",      "background"),
    ("stands out",            ""),
    ("extensive experience",  "experience"),
    ("vasta experiência",     "experiência"),
    ("apaixonado por",        "focado em"),
    ("passionate about",      "focused on"),
    ("seria uma honra",       ""),
    ("would be an honor",     ""),
    ("venho por meio desta",  ""),
    ("through this message",  ""),
]

_MARKDOWN_ARTIFACTS = [
    # bold/italic markdown que vaza no texto
    (r"\*\*(.+?)\*\*", r"\1"),
    (r"\*(.+?)\*",     r"\1"),
    (r"__(.+?)__",     r"\1"),
    (r"_(.+?)_",       r"\1"),
    # aspas tipográficas mal formadas consecutivas
    (r'"{2,}',         '"'),
    (r"'{2,}",         "'"),
    # traços extras
    (r"—{2,}",         "—"),
    # espaços duplos
    (r" {2,}",         " "),
    # newlines múltiplas dentro de strings JSON
    (r"\n{3,}",        "\n\n"),
]


def sanitise_text(text: str) -> str:
    """Remove artefatos Markdown e linguagem corporativa proibida."""
    if not text:
        return text

    # 1. Markdown artifacts
    for pattern, replacement in _MARKDOWN_ARTIFACTS:
        text = re.sub(pattern, replacement, text)

    # 2. Frases proibidas (case-insensitive)
    for forbidden, replacement in _FORBIDDEN_PAIRS:
        if forbidden.lower() in text.lower():
            pattern = re.compile(re.escape(forbidden), re.IGNORECASE)
            text = pattern.sub(replacement, text)

    # 3. Espaços antes de pontuação
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def sanitise_decision(decision: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica sanitise_text em todos os campos textuais do decision dict."""
    if "custom_summary" in decision:
        decision["custom_summary"] = sanitise_text(decision["custom_summary"])

    if "adapted_role_title" in decision:
        decision["adapted_role_title"] = sanitise_text(decision["adapted_role_title"])

    if "custom_projects" in decision:
        for proj in decision["custom_projects"]:
            for field in ("adapted_title", "adapted_description", "tech_display"):
                if field in proj:
                    proj[field] = sanitise_text(proj[field])

    if "skills_categorized" in decision:
        cleaned = {}
        for cat, skills in decision["skills_categorized"].items():
            cleaned[sanitise_text(cat)] = [sanitise_text(s) for s in skills]
        decision["skills_categorized"] = cleaned

    return decision


# ── Language detection ───────────────────────────────────────────────────────

_PT_KEYWORDS = [
    "buscamos", "requisitos", "será responsável", "empresa", "empresa de",
    "candidato", "vaga", "cargo", "benefícios", "contratação", "salário",
    "estágio", "ensino", "formação", "obrigatório", "desejável",
]
_EN_KEYWORDS = [
    "we are looking", "requirements", "responsibilities", "you will",
    "experience with", "must have", "nice to have", "salary", "benefits",
    "apply", "qualifications", "role", "position", "team", "join us",
]


def detect_language_heuristic(text: str) -> Optional[str]:
    """
    Detecção de idioma por contagem de keywords.
    Retorna 'pt-BR', 'en-US' ou None se inconclusivo.
    """
    lower = text.lower()
    pt_score = sum(1 for kw in _PT_KEYWORDS if kw in lower)
    en_score = sum(1 for kw in _EN_KEYWORDS if kw in lower)

    total = pt_score + en_score
    if total == 0:
        return None
    ratio = max(pt_score, en_score) / total
    if ratio >= 0.65:
        return "pt-BR" if pt_score >= en_score else "en-US"
    return None


# ── LangGraph State ─────────────────────────────────────────────────────────

class ResumeState(TypedDict):
    job_description: str
    master_data: Dict[str, Any]
    force_language: Optional[str]
    template_type: str                   # "dev" | "support"
    job_title: Optional[str]
    company_name: Optional[str]
    detected_language: Optional[str]
    raw_decision: Optional[Dict[str, Any]]
    final_decision: Optional[Dict[str, Any]]
    error: Optional[str]
    retry_count: int


# ── Graph Nodes ──────────────────────────────────────────────────────────────

def node_detect_language(state: ResumeState) -> ResumeState:
    lang = state.get("force_language")
    if lang:
        print(f"🌍 Idioma FORÇADO: {lang}")
        return {**state, "detected_language": lang}

    heuristic = detect_language_heuristic(state["job_description"])
    if heuristic:
        print(f"🌍 Idioma detectado (heurística): {heuristic}")
        return {**state, "detected_language": heuristic}

    # Fallback LLM
    llm = _llm()
    prompt = ChatPromptTemplate.from_template(
        "Analyze the dominant language of this job description.\n"
        "Reply ONLY with 'pt-BR' or 'en-US'.\n\n{text}"
    )
    chain = prompt | llm
    result = chain.invoke({"text": state["job_description"][:800]})
    lang = result.content.strip().replace('"', "").replace("'", "")
    if "en" in lang.lower():
        lang = "en-US"
    else:
        lang = "pt-BR"
    print(f"🌍 Idioma detectado (LLM fallback): {lang}")
    return {**state, "detected_language": lang}


def node_call_ai(state: ResumeState) -> ResumeState:
    """Chama a LLM e retorna o decision dict bruto."""
    lang = state["detected_language"] or "pt-BR"
    template_type = state.get("template_type", "dev")
    is_en = lang == "en-US"

    # Instruções de idioma
    lang_instr = f"⚠️ MANDATORY LANGUAGE: {lang}. ALL text must be in {'English' if is_en else 'Portuguese (Brazil)'}."

    # Contexto da vaga
    ctx_parts = []
    if state.get("job_title"):
        ctx_parts.append(f"JOB TITLE: {state['job_title']}")
    if state.get("company_name"):
        ctx_parts.append(f"COMPANY: {state['company_name']}")
    job_ctx = "\n".join(ctx_parts)

    # Instruções de tipo de template
    if template_type == "support":
        type_instr = (
            "This is a SUPPORT / HELP DESK / IT role.\n"
            "PRIORITIZE: communication, troubleshooting, ITSM, Azure, customer service.\n"
            "PROJECTS: choose AutoScan (RPA), Nexus AI Recruiter (automation), Clutch (troubleshooting).\n"
            "SKILLS: include a 'Suporte & Comunicação' / 'Support & Communication' category.\n"
        )
    else:
        type_instr = (
            "This is a DEVELOPER role.\n"
            "PRIORITIZE: technical stack, architecture, backend/frontend based on job description.\n"
            "Select the 3 most relevant projects from the portfolio.\n"
        )

    prompt_template = ChatPromptTemplate.from_template(
        """YOU ARE WRITING ABOUT YOURSELF. You ARE Alessandro. Write YOUR resume.
NEVER use 3rd person. NEVER say "Alessandro" mid-sentence.

═══════════════════════════════════════════════════════
INVIOLABLE RULES — VIOLATION = AUTOMATIC FAILURE
═══════════════════════════════════════════════════════

1. NO 3RD PERSON:
   ❌ "Alessandro stands out" | "Alessandro has" | "Alessandro Lima da Silva"
   ✅ Start directly: "Software Engineering student..."

2. BANNED PHRASES (auto-replaced post-generation, so avoid them):
   ❌ "sólida base" | "se destaca" | "expertise" | "proficiente"
   ❌ "capacidade analítica" | "evidenciando" | "garantindo" | "otimizando"
   ❌ "solid background" | "stands out" | "extensive experience" | "passionate about"

3. NO MARKDOWN in output text values:
   ❌ **bold** | *italic* | __underline__ | ""double quotes"" stacked
   ✅ Plain text only in all string values

4. SUMMARY: ONE paragraph, 400–550 characters
   Structure: [Degree + real experience] + [concrete skills] + [fit for THIS role]

5. PROJECTS: ALWAYS honest — these are learning/study projects
   ✅ "Project to learn X: implemented Y with Z. Gained: skill. Stack: A, B, C."
   ❌ "ensuring decoupling" | "optimizing foundation" | "evidencing ability"

═══════════════════════════════════════════════════════
INPUTS
═══════════════════════════════════════════════════════

JOB DESCRIPTION:
{job_description}

{job_context}

PROFILE DATA:
{master_data}

LANGUAGE INSTRUCTION:
{lang_instruction}

TEMPLATE TYPE INSTRUCTIONS:
{type_instruction}

═══════════════════════════════════════════════════════
SUMMARY STRUCTURE (MANDATORY):
═══════════════════════════════════════════════════════

LINE 1: Degree + real experience (Azure tech support)
LINE 2: Transition to dev/skill focus (Python, last 8 months)
LINE 3: Specific fit for THIS job

❌ WRONG: "Alessandro possui sólida base em..."
✅ CORRECT: "Software Engineering student (graduation 03/2026) with 2+ years in technical support (Azure, troubleshooting, ITSM). Transitioned to Python development 8 months ago. This background gives me clear communication, logical reasoning, and incident management — valuable for [specific fit]."

SIZE: 400–550 chars. COUNT before returning.

═══════════════════════════════════════════════════════
PROJECTS (EXACTLY 3):
═══════════════════════════════════════════════════════

{type_instruction}

FORMAT:
"Project to [learn X]: implemented [Y] using [techs]. Result: mastery of [skill]. Stack: A, B, C."

═══════════════════════════════════════════════════════
OUTPUT JSON (strict):
═══════════════════════════════════════════════════════

{{
  "language_code": "{lang_code}",
  "adapted_role_title": "Title | Stack + Differentiator",
  "custom_summary": "One paragraph, 400-550 chars, no markdown...",
  "skills_categorized": {{
    "Category1": ["skill1", "skill2"],
    "Category2": ["skill3", "skill4"]
  }},
  "custom_projects": [
    {{
      "original_id": "project-id",
      "adapted_title": "Project Title",
      "adapted_description": "Project to learn X: implemented Y...",
      "tech_display": "Tech1 | Tech2 | Tech3"
    }}
  ],
  "highlighted_techs": ["Tech1", "Tech2"],
  "project_selection_reasoning": "I chose these 3 because..."
}}

CHECKLIST before returning:
[ ] No "Alessandro" in summary mid-sentence?
[ ] No banned phrases?
[ ] Summary is ONE paragraph, 400-550 chars?
[ ] No **markdown** in text values?
[ ] Exactly 3 projects?
[ ] All in correct language: {lang_code}?

If ANY = NO → REWRITE until all = YES.
"""
    )

    llm = _llm()
    chain = prompt_template | llm

    response = chain.invoke({
        "job_description": state["job_description"],
        "job_context": job_ctx,
        "master_data": json.dumps(state["master_data"], ensure_ascii=False, indent=2),
        "lang_instruction": lang_instr,
        "type_instruction": type_instr,
        "lang_code": lang,
    })

    try:
        cleaned = clean_json_output(response.content)
        decision = json.loads(cleaned)
        return {**state, "raw_decision": decision, "error": None}
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return {**state, "raw_decision": None, "error": str(e), "retry_count": state.get("retry_count", 0) + 1}


def node_validate(state: ResumeState) -> ResumeState:
    """Valida e corrige o decision dict."""
    decision = state.get("raw_decision")
    lang = state.get("detected_language", "pt-BR")

    if not decision:
        return {**state, "error": "raw_decision is None after LLM call."}

    # Force language
    decision["language_code"] = lang

    # ── Sanitise all text fields ──────────────────────────────────────────
    decision = sanitise_decision(decision)

    # ── Summary validation ────────────────────────────────────────────────
    summary = decision.get("custom_summary", "")

    # Remove multiple paragraphs → join into one
    if "\n\n" in summary or "\n" in summary:
        summary = re.sub(r"\s*\n+\s*", " ", summary).strip()

    # Remove "Alessandro" at start
    summary = re.sub(r"^Alessandro\s+Lima\s+da\s+Silva[,.]?\s*", "", summary, flags=re.IGNORECASE)
    summary = re.sub(r"^Alessandro[,.]?\s+", "", summary, flags=re.IGNORECASE)

    # Length warning
    if len(summary) > 600:
        print(f"⚠️  Summary long ({len(summary)} chars). Truncating at last full sentence ≤600.")
        # Truncate at last sentence boundary
        truncated = summary[:600]
        last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
        if last_period > 400:
            summary = truncated[:last_period + 1].strip()
        else:
            summary = truncated.strip()

    decision["custom_summary"] = summary

    # ── Projects validation ────────────────────────────────────────────────
    projects = decision.get("custom_projects", [])
    if not projects:
        return {**state, "error": "AI failed to generate projects.", "retry_count": state.get("retry_count", 0) + 1}

    if len(projects) > 3:
        print(f"⚠️  Limiting {len(projects)} → 3 projects")
        projects = projects[:3]
    elif len(projects) < 3:
        print(f"⚠️  Only {len(projects)} project(s) returned (expected 3)")

    decision["custom_projects"] = projects

    # ── Ensure skills dict has at least one category ───────────────────────
    if not decision.get("skills_categorized"):
        decision["skills_categorized"] = {
            "Tecnologias": state["master_data"]["profile"].get("hard_skills", [])[:8]
        }

    summary_len = len(decision.get("custom_summary", ""))
    proj_count = len(decision.get("custom_projects", []))
    print(f"✅ V9 {lang} | {proj_count} projects | {summary_len} chars summary")

    return {**state, "final_decision": decision, "error": None}


def node_retry_check(state: ResumeState) -> str:
    """Decide se deve retry ou encerrar com erro."""
    if state.get("error") and state.get("retry_count", 0) < 2:
        print(f"🔄 Retrying... ({state['retry_count']}/2)")
        return "retry"
    if state.get("error"):
        return "fail"
    return "done"


# ── Build LangGraph ──────────────────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(ResumeState)

    graph.add_node("detect_language", node_detect_language)
    graph.add_node("call_ai", node_call_ai)
    graph.add_node("validate", node_validate)

    graph.set_entry_point("detect_language")
    graph.add_edge("detect_language", "call_ai")
    graph.add_edge("call_ai", "validate")
    graph.add_conditional_edges(
        "validate",
        node_retry_check,
        {
            "retry": "call_ai",
            "done": END,
            "fail": END,
        },
    )

    return graph.compile()


_RESUME_GRAPH = None


def get_resume_graph():
    global _RESUME_GRAPH
    if _RESUME_GRAPH is None:
        _RESUME_GRAPH = _build_graph()
    return _RESUME_GRAPH


# ── Public API ───────────────────────────────────────────────────────────────

def get_ai_decision(
    job_description: str,
    master_data: Dict[str, Any],
    force_language: Optional[str] = None,
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
    template_type: str = "dev",
) -> Dict[str, Any]:
    """
    Engine V9: LangGraph + Ultra-Validations + i18n.

    Args:
        job_description : Texto completo da vaga.
        master_data     : Dados do perfil (do banco).
        force_language  : 'pt-BR' | 'en-US' | None (auto-detect).
        job_title       : Título da vaga (opcional, melhora precisão).
        company_name    : Nome da empresa (opcional).
        template_type   : 'dev' | 'support'.

    Returns:
        Dict com campos: language_code, adapted_role_title, custom_summary,
                         skills_categorized, custom_projects, highlighted_techs,
                         project_selection_reasoning.
    """
    graph = get_resume_graph()

    initial_state: ResumeState = {
        "job_description": job_description,
        "master_data": master_data,
        "force_language": force_language,
        "template_type": template_type,
        "job_title": job_title,
        "company_name": company_name,
        "detected_language": None,
        "raw_decision": None,
        "final_decision": None,
        "error": None,
        "retry_count": 0,
    }

    result = graph.invoke(initial_state)

    if result.get("error") or not result.get("final_decision"):
        raise RuntimeError(f"AI Engine V9 failed: {result.get('error', 'Unknown error')}")

    return result["final_decision"]


def build_context_from_decision(
    decision: Dict[str, Any],
    master_data: Dict[str, Any],
    template_type: str = "dev",
) -> Dict[str, Any]:
    """Monta o contexto Jinja2 completo para renderização do template."""
    language_code = decision.get("language_code", "pt-BR")
    labels = get_labels(language_code)

    # Projetos
    selected_projects = [
        {
            "name": p["adapted_title"],
            "techs": p["tech_display"],
            "description": p["adapted_description"],
        }
        for p in decision.get("custom_projects", [])
    ]

    # Skills
    skills_formatted = [
        {"name": cat, "list": " • ".join(skills)}
        for cat, skills in decision.get("skills_categorized", {}).items()
        if skills
    ]

    # Soft skills (apenas para templates de suporte)
    soft_skills = get_soft_skills(language_code) if template_type == "support" else []

    # Experiência traduzida
    experience = translate_experience(language_code)

    # Template path
    template_path = get_template_path(language_code, template_type)

    return {
        # Perfil
        "name": master_data["profile"]["name"],
        "role_title": decision.get("adapted_role_title", "Desenvolvedor Full Stack"),
        "location": master_data["profile"]["contact"]["location"],
        "phone": master_data["profile"]["contact"]["phone"],
        "email": master_data["profile"]["contact"]["email"],
        "linkedin": master_data["profile"]["contact"]["linkedin"],
        "github": master_data["profile"]["contact"]["github"],
        # Conteúdo adaptado
        "summary": decision.get("custom_summary", ""),
        "skills": skills_formatted,
        "soft_skills": soft_skills,
        "selected_projects": selected_projects,
        "highlighted_techs": decision.get("highlighted_techs", []),
        # Dados fixos
        "education": master_data["profile"]["education"],
        "languages": master_data["profile"]["languages"],
        "experience": experience,
        # Meta
        "language_code": language_code,
        "template_path": template_path,
        "template_type": template_type,
        # Labels i18n
        "labels": labels,
    }


# ── Cover Letter Engine ─────────────────────────────────────────────────────

def generate_cover_letter(
    job_description: str,
    master_data: Dict[str, Any],
    language_code: str = "pt-BR",
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Gera carta de apresentação humanizada e otimizada para vagas de TI.

    Estrutura comprovada (Nação):
      1. Hook   — conexão imediata com a vaga
      2. Contexto — trajetória (suporte → dev)
      3. Prova  — 2–3 projetos relevantes com resultado
      4. Fit    — por que eu + empresa
      5. CTA    — objetivo e disponibilidade

    Returns: { subject_line, email_body, word_count }
    """
    is_en = language_code == "en-US"

    # Top 5 projects for context
    projects_list = "\n".join([
        f"- {p['id']}: {p['title']} ({', '.join(p['tech_stack'][:4])})"
        for p in master_data["projects"][:10]
    ])

    company_clause = f" at {company_name}" if company_name else ""
    role_clause = f"for the {job_title} role{company_clause}" if job_title else f"for this role{company_clause}"

    if is_en:
        lang_instruction = "Write 100% in English. Professional but conversational tone."
        structure_hint = f"""STRUCTURE (apply {role_clause}):
1. HOOK (1-2 sentences): "I came across this opening — it makes sense to apply. You need someone who [X]..."
2. CONTEXT (2-3 sentences): Journey from Azure support → Python dev. Be specific about timeline.
3. PROOF (2-3 bullets with **bold project names**):
   • **Project Name** — What I built + concrete skill gained
4. FIT (1-2 sentences): Why support background + dev skills = unique value for THIS company/role.
5. CTA (1 sentence): Clear availability + call to action.

CLOSING: "Best,\\nAlessandro"
GREETING: "Hi{' ' + company_name if company_name else ''},"
"""
        banned = "BANNED: 'passionate about', 'it would be an honor', 'vast experience', 'through this message', 'highly motivated'"
    else:
        lang_instruction = "Escreva 100% em Português Brasileiro. Tom profissional mas conversacional."
        structure_hint = f"""ESTRUTURA (aplique {role_clause}):
1. GANCHO (1-2 frases): "Vi a vaga e faz sentido candidatar. Vocês precisam de alguém que [X]..."
2. CONTEXTO (2-3 frases): Trajetória suporte Azure → Python dev. Seja específico com tempo.
3. PROVA (2-3 bullets com **nomes em negrito**):
   • **Nome do Projeto** — O que construí + skill concreta adquirida
4. FIT (1-2 frases): Por que background em suporte + skills dev = valor único para ESTA empresa/vaga.
5. CTA (1 frase): Disponibilidade clara + call to action.

FECHAMENTO: "Abraço,\\nAlessandro"
SAUDAÇÃO: "Oi{' ' + company_name if company_name else ''},"
"""
        banned = "PROIBIDO: 'apaixonado por', 'seria uma honra', 'vasta experiência', 'venho por meio desta', 'altamente motivado'"

    prompt_template = ChatPromptTemplate.from_template(
        """{lang_instruction}

{structure_hint}

{banned}

LENGTH: 180-250 words (count before returning).

JOB DESCRIPTION:
{job_description}

AVAILABLE PROJECTS (select 2-3 most relevant):
{projects_list}

PROFILE CONTEXT:
- Software Engineering student, graduation 03/2026
- 3 years Azure IT support at Aegea Saneamento  
- 8 months focused Python/AI development
- Skills: Python, FastAPI, LangChain, Gemini API, React, Docker

OUTPUT JSON (only JSON, no markdown wrapper):
{{
  "subject_line": "Role Title — Alessandro (Key Differentiator)",
  "email_body": "Greeting\\n\\nBody text 180-250 words...\\n\\nClosing",
  "word_count": 200
}}
"""
    )

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.28,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_retries=MAX_RETRIES,
        request_timeout=90,
    )

    chain = prompt_template | llm
    response = chain.invoke({
        "lang_instruction": lang_instruction,
        "structure_hint": structure_hint,
        "banned": banned,
        "job_description": job_description[:3000],
        "projects_list": projects_list,
    })

    cleaned = clean_json_output(response.content)
    result = json.loads(cleaned)

    if "email_body" not in result:
        raise ValueError("AI failed to generate cover letter body.")

    # Sanitise the letter body too
    result["email_body"] = sanitise_text(result["email_body"])
    result["subject_line"] = sanitise_text(result.get("subject_line", ""))

    print(f"✅ Cover Letter: {result.get('word_count', '?')} words | {language_code}")
    return result