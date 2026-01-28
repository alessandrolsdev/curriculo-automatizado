"""
Módulo de Geração Manual de Currículos (Legacy)
===============================================

Este script fornece uma alternativa manual à geração baseada em IA,
permitindo a criação de currículos baseados em regras predefinidas
de filtro de conteúdo (Role-Based Filtering).

Uso:
    Pode ser executado diretamente para gerar versões padrão de currículos
    (RPA, Frontend, Backend) sem inferência de IA.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

from docxtpl import DocxTemplate

# --- Configurações e Constantes ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "master_data.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "base_template.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_data() -> Dict[str, Any]:
    """
    Carrega o arquivo JSON com os dados mestres.

    Returns:
        Dict[str, Any]: Dados carregados.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_content(
    data: Dict[str, Any], target_role: str = "fullstack"
) -> Dict[str, Any]:
    """
    Filtra o conteúdo do currículo baseado no papel (role) alvo.

    Aplica regras de negócio para priorizar skills e projetos relevantes
    para a vaga específica, garantindo um currículo conciso ("One-Page").

    Args:
        data (Dict[str, Any]): Dados mestre.
        target_role (str): Papel alvo (ex: 'rpa', 'frontend', 'backend').

    Returns:
        Dict[str, Any]: Contexto formatado para o template Docx.
    """
    context = {}

    # 1. Dados Pessoais
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

    # 2. Resumo e Título Profissional
    context["role_title"] = f"Desenvolvedor {target_role.title()}"
    context["summary"] = profile["summaries"].get(
        target_role, profile["summaries"]["fullstack"]
    )

    # 3. Ordenação de Skills por Relevância
    context["skills"] = []

    if target_role == "rpa":
        order = ["rpa_ai", "backend", "database", "devops"]
    elif target_role == "frontend":
        order = ["frontend", "devops"]
    else:
        # Default Fullstack
        order = ["backend", "frontend", "database", "devops", "rpa_ai"]

    for key in order:
        if key in data["skills"]:
            context["skills"].append(
                {
                    "name": key.replace("_", " & ").upper(),
                    "list": ", ".join(data["skills"][key]),
                }
            )

    # 4. Seleção de Projetos (Limite: 3)
    context["selected_projects"] = []
    project_limit = 3
    count = 0

    for proj in data["projects"]:
        if count >= project_limit:
            break

        # Lógica de seleção por palavra-chave no tipo do projeto
        is_relevant = False
        if target_role in proj["type"].lower() or "fullstack" in proj["type"].lower():
            is_relevant = True

        # Regra específica para RPA
        if target_role == "rpa" and "rpa" in proj["id"]:
            is_relevant = True

        if is_relevant:
            # Seleciona descrição focada
            desc_text = ""
            for desc in proj["descriptions"]:
                if desc["focus"] == target_role:
                    desc_text = desc["text"]
                    break

            # Fallback
            if not desc_text and proj["descriptions"]:
                desc_text = proj["descriptions"][0]["text"]

            context["selected_projects"].append(
                {
                    "name": proj["title"],
                    "techs": " | ".join(proj["tech_stack"]),
                    "description": desc_text,
                }
            )
            count += 1

    # 5. Experiência Profissional
    latest_job = data["experience"][0]

    selected_bullets = []
    is_english = target_role == "english"

    for bullet in latest_job["description_bullets"]:
        if is_english and "text_en" in bullet:
            selected_bullets.append(bullet["text_en"])
        elif "text" in bullet:
            selected_bullets.append(bullet["text"])

    context["experience"] = {
        "role": latest_job["role"],
        "company": latest_job["company"],
        "period": latest_job["period"],
        "bullets": selected_bullets[:4],
    }

    return context


def generate_cv(target_role: str = "fullstack") -> None:
    """
    Gera um arquivo de currículo (.docx) para o perfil especificado.

    Args:
        target_role (str): O perfil desejado (ex: backend, rpa).
    """
    print(f"🤖 Iniciando geração manual para perfil: {target_role.upper()}...")

    try:
        data = load_data()
        context = filter_content(data, target_role)

        doc = DocxTemplate(TEMPLATE_PATH)
        doc.render(context)

        # Cria diretório de output se não existir
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        filename = f"Currículo_Alessandro_{target_role.upper()}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
        file_path = os.path.join(OUTPUT_DIR, filename)

        doc.save(file_path)
        print(f"✅ Sucesso! Arquivo salvo em: {file_path}")

    except Exception as e:
        print(f"❌ Erro ao gerar currículo: {e}")


if __name__ == "__main__":
    # Testes de geração manual
    generate_cv("rpa")
    generate_cv("frontend")
    generate_cv("backend")
