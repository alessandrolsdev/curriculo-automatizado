"""
Módulo de Traduções Estáticas para i18n
Versão 1.0: Suporte PT-BR e EN-US
"""

from typing import Dict, Any

# ============================================================================
# 📚 TRADUÇÕES DE DADOS ESTÁTICOS
# ============================================================================

STATIC_TRANSLATIONS = {
    "pt-BR": {
        # Experiência profissional
        "experience": {
            "role": "Estagiário de Tecnologia da Informação",
            "company": "Aegea Saneamento",
            "period": "Setembro 2022 - Setembro 2025 (2 anos)",
            "bullets": [
                "Gerenciamento e configuração de notebooks utilizando Microsoft Azure, garantindo a segurança e conformidade dos ativos.",
                "Suporte na resolução de falhas de rede e sistemas, colaborando para a manutenção da estabilidade do ambiente.",
                "Atendimento a chamados técnicos e documentação de soluções em plataformas de gestão."
            ]
        },
        
        # Educação
        "education": {
            "degree_prefix": "Bacharelado em",
            "period_label": "Previsão",
            "date_format": "%m/%Y"  # 03/2022
        },
        
        # Idiomas
        "languages": {
            "native": "Nativo",
            "technical": "Técnico",
            "intermediate": "Intermediário",
            "advanced": "Avançado",
            "fluent": "Fluente"
        },
        
        # Metadados de seções (para templates)
        "section_headers": {
            "summary": "Resumo Profissional",
            "skills": "Competências Técnicas",
            "projects": "Projetos em Destaque",
            "experience": "Experiência Profissional",
            "education": "Educação",
            "languages": "Idiomas"
        }
    },
    
    "en-US": {
        # Professional experience
        "experience": {
            "role": "IT Intern",
            "company": "Aegea Saneamento",
            "period": "Sep 2022 - Sep 2025 (2 years)",
            "bullets": [
                "Managed and configured notebooks using Microsoft Azure, ensuring asset security and compliance.",
                "Provided support in resolving network and system failures, collaborating to maintain environment stability.",
                "Handled technical support tickets and documented solutions on management platforms."
            ]
        },
        
        # Education
        "education": {
            "degree_prefix": "Bachelor's Degree in",
            "period_label": "Expected",
            "date_format": "%m/%Y"  # 03/2022 (mesmo formato)
        },
        
        # Languages
        "languages": {
            "native": "Native",
            "technical": "Technical",
            "intermediate": "Intermediate",
            "advanced": "Advanced",
            "fluent": "Fluent"
        },
        
        # Section headers metadata (for templates)
        "section_headers": {
            "summary": "Professional Summary",
            "skills": "Technical Skills",
            "projects": "Featured Projects",
            "experience": "Professional Experience",
            "education": "Education",
            "languages": "Languages"
        }
    }
}

# ============================================================================
# 🌍 FUNÇÕES DE TRADUÇÃO
# ============================================================================

def get_translation(language_code: str, key_path: str) -> Any:
    """
    Recupera tradução baseada no idioma e caminho da chave.
    
    Args:
        language_code: "pt-BR" ou "en-US"
        key_path: Caminho da chave (ex: "experience.role")
    
    Returns:
        Valor traduzido ou None se não encontrado
    
    Example:
        >>> get_translation("en-US", "experience.role")
        "IT Intern"
    """
    if language_code not in STATIC_TRANSLATIONS:
        language_code = "pt-BR"  # Fallback
    
    keys = key_path.split(".")
    value = STATIC_TRANSLATIONS[language_code]
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    
    return value


def translate_experience(language_code: str) -> Dict[str, Any]:
    """
    Retorna experiência profissional traduzida.
    
    Args:
        language_code: "pt-BR" ou "en-US"
    
    Returns:
        Dict com role, company, period, bullets
    """
    return get_translation(language_code, "experience")


def translate_language_level(level: str, language_code: str) -> str:
    """
    Traduz nível de proficiência de idioma.
    
    Args:
        level: "Nativo", "Técnico", "Intermediário", etc.
        language_code: "pt-BR" ou "en-US"
    
    Returns:
        Nível traduzido
    
    Example:
        >>> translate_language_level("Nativo", "en-US")
        "Native"
    """
    level_map = {
        "pt-BR": {
            "Nativo": "native",
            "Técnico": "technical",
            "Intermediário": "intermediate",
            "Avançado": "advanced",
            "Fluente": "fluent"
        },
        "en-US": {
            "Native": "native",
            "Technical": "technical",
            "Intermediate": "intermediate",
            "Advanced": "advanced",
            "Fluent": "fluent"
        }
    }
    
    # Normaliza input
    level_key = level_map.get("pt-BR", {}).get(level, level.lower())
    
    # Retorna tradução
    return get_translation(language_code, f"languages.{level_key}") or level


def get_template_path(language_code: str) -> str:
    """
    Retorna caminho do template Word baseado no idioma.
    
    Args:
        language_code: "pt-BR" ou "en-US"
    
    Returns:
        Caminho relativo do template
    """
    template_map = {
        "pt-BR": "templates/base_template.docx",
        "en-US": "templates/base_template_en.docx"
    }
    
    return template_map.get(language_code, template_map["pt-BR"])


# ============================================================================
# 🧪 TESTES (Para validação)
# ============================================================================

if __name__ == "__main__":
    # Teste 1: Tradução de experiência
    exp_pt = translate_experience("pt-BR")
    exp_en = translate_experience("en-US")
    
    print("=== TESTE 1: Experiência ===")
    print(f"PT: {exp_pt['role']}")
    print(f"EN: {exp_en['role']}")
    print()
    
    # Teste 2: Tradução de níveis de idioma
    print("=== TESTE 2: Níveis de Idioma ===")
    print(f"'Nativo' em EN: {translate_language_level('Nativo', 'en-US')}")
    print(f"'Técnico' em EN: {translate_language_level('Técnico', 'en-US')}")
    print()
    
    # Teste 3: Templates
    print("=== TESTE 3: Templates ===")
    print(f"Template PT: {get_template_path('pt-BR')}")
    print(f"Template EN: {get_template_path('en-US')}")
    print()
    
    # Teste 4: Headers de seção
    print("=== TESTE 4: Section Headers ===")
    print(f"'Resumo' em EN: {get_translation('en-US', 'section_headers.summary')}")
    print(f"'Projetos' em EN: {get_translation('en-US', 'section_headers.projects')}")
