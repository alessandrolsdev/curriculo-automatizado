"""
Módulo de Internacionalização (i18n) - Nexus AI Recruiter
==========================================================
Versão 9.0: Templates PT-BR / EN-US para currículos e cartas de apresentação.

Tipos de template:
  - dev_pt     → Desenvolvedor (PT-BR)
  - dev_en     → Developer (EN-US)
  - support_pt → Suporte N1 (PT-BR)
  - support_en → Support N1 (EN-US)
  - letter_pt  → Carta de apresentação (PT-BR)
  - letter_en  → Cover letter (EN-US)
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


# ── Experiência profissional traduzida ──────────────────────────────────────

_EXPERIENCE_PT = {
    "role": "Estagiário de Tecnologia da Informação",
    "company": "Aegea Saneamento",
    "period": "Setembro 2022 – Setembro 2025 (3 anos)",
    "bullets": [
        "Gerenciamento e configuração de notebooks via Microsoft Azure, assegurando segurança e conformidade dos ativos.",
        "Diagnóstico e resolução de falhas de rede e sistemas, mantendo estabilidade do ambiente corporativo.",
        "Atendimento a chamados técnicos com registro e documentação de soluções em plataformas de gestão (ITSM).",
        "Suporte remoto a usuários, coletando informações de forma clara e reduzindo tempo médio de resolução.",
    ],
    "soft_bullets": [
        "Comunicação clara com usuários técnicos e não-técnicos.",
        "Raciocínio lógico aplicado a troubleshooting de incidentes.",
        "Organização e documentação de processos e soluções.",
        "Trabalho em equipe em ambiente multidisciplinar.",
    ],
}

_EXPERIENCE_EN = {
    "role": "IT Support Intern",
    "company": "Aegea Saneamento",
    "period": "September 2022 – September 2025 (3 years)",
    "bullets": [
        "Managed and configured laptops via Microsoft Azure, ensuring asset security and compliance.",
        "Diagnosed and resolved network and system failures, maintaining corporate environment stability.",
        "Handled technical tickets with full documentation of solutions in ITSM platforms.",
        "Provided remote user support with clear communication, reducing average resolution time.",
    ],
    "soft_bullets": [
        "Clear communication with both technical and non-technical stakeholders.",
        "Logical reasoning applied to incident troubleshooting.",
        "Organization and documentation of processes and solutions.",
        "Teamwork in a multidisciplinary environment.",
    ],
}


def translate_experience(language_code: str) -> dict:
    """Retorna experiência no idioma solicitado."""
    if language_code == "en-US":
        return _EXPERIENCE_EN
    return _EXPERIENCE_PT


# ── Mapeamento de template path ─────────────────────────────────────────────

_TEMPLATE_MAP = {
    "dev_pt": "base_template.docx",
    "dev_en": "base_template_en.docx",
    "support_pt": "support_template.docx",
    "support_en": "support_template_en.docx",
}


def get_template_path(language_code: str, template_type: str = "dev") -> str:
    """
    Retorna o caminho absoluto do template DOCX.

    Args:
        language_code: 'pt-BR' ou 'en-US'
        template_type: 'dev' ou 'support'

    Returns:
        Caminho absoluto para o template .docx
    """
    lang_key = "en" if language_code == "en-US" else "pt"
    key = f"{template_type}_{lang_key}"
    filename = _TEMPLATE_MAP.get(key, "curriculo_dev_pt.docx")
    path = os.path.join(TEMPLATES_DIR, filename)

    if not os.path.exists(path):
        # fallback: qualquer template disponível
        for fallback_key in ["dev_pt", "dev_en", "support_pt", "support_en"]:
            fallback_path = os.path.join(TEMPLATES_DIR, _TEMPLATE_MAP[fallback_key])
            if os.path.exists(fallback_path):
                print(
                    f"⚠️  Template '{filename}' não encontrado. Usando fallback: {_TEMPLATE_MAP[fallback_key]}"
                )
                return fallback_path
        raise FileNotFoundError(f"Nenhum template DOCX encontrado em: {TEMPLATES_DIR}")

    return path


# ── Soft skills padrão (para templates de suporte) ──────────────────────────

_SOFT_SKILLS_PT = [
    {
        "name": "Comunicação",
        "list": "Atendimento ao Cliente • Escrita Técnica • Empatia",
    },
    {
        "name": "Resolução de Problemas",
        "list": "Troubleshooting • Raciocínio Lógico • Gestão de Incidentes",
    },
    {"name": "Organização", "list": "Documentação • Priorização • ITSM"},
]

_SOFT_SKILLS_EN = [
    {"name": "Communication", "list": "Customer Service • Technical Writing • Empathy"},
    {
        "name": "Problem Solving",
        "list": "Troubleshooting • Logical Reasoning • Incident Management",
    },
    {"name": "Organization", "list": "Documentation • Prioritization • ITSM"},
]


def get_soft_skills(language_code: str) -> list:
    """Retorna soft skills formatadas no idioma solicitado."""
    if language_code == "en-US":
        return _SOFT_SKILLS_EN
    return _SOFT_SKILLS_PT


# ── Labels de seção por idioma ───────────────────────────────────────────────

_LABELS_PT = {
    "summary_title": "Resumo Profissional",
    "skills_title": "Competências Técnicas",
    "soft_skills_title": "Competências Comportamentais",
    "experience_title": "Experiência Profissional",
    "projects_title": "Projetos em Destaque",
    "education_title": "Formação Acadêmica",
}

_LABELS_EN = {
    "summary_title": "Professional Summary",
    "skills_title": "Technical Skills",
    "soft_skills_title": "Soft Skills",
    "experience_title": "Professional Experience",
    "projects_title": "Featured Projects",
    "education_title": "Education",
}


def get_labels(language_code: str) -> dict:
    """Retorna labels de seção no idioma solicitado."""
    if language_code == "en-US":
        return _LABELS_EN
    return _LABELS_PT
