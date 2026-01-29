"""
Script de Teste: Geração Completa de Documento

Testa a geração completa do documento Word usando o contexto.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from docxtpl import DocxTemplate
from ai_recruiter import (
    load_data,
    build_context_from_decision,
    BASE_DIR,
    TEMPLATE_PATH,
    OUTPUT_DIR,
)

print("=" * 60)
print("TESTANDO GERAÇÃO COMPLETA DE DOCUMENTO WORD")
print("=" * 60)

# Simula decisão da IA
fake_decision = {
    "selected_summary_key": "frontend",
    "skills_order": [
        "React.js",
        "TypeScript",
        "Next.js",
        "Tailwind",
        "Vue.js 3",
        "Angular 18",
    ],
    "selected_project_ids": [
        "arena_iron_beach",
        "interactive_portfolio",
        "landing_page_matias",
    ],
}

# Carrega dados
print("\n📂 Carregando dados do banco...")
master_data = load_data()
print(f"✅ {len(master_data['projects'])} projetos carregados")

# Cria contexto
print("\n🔧 Construindo contexto...")
context = build_context_from_decision(fake_decision, master_data)

# Debug do contexto
print(f"\n📊 CONTEXTO:")
print(f"   Nome: {context['name']}")
print(f"   Skills: {context['skills']}")
print(f"   Projetos: {len(context['projects'])}")
print(f"   Educação: {context['education']['degree']}")

# Gerar documento
try:
    print(f"\n📄 Carregando template: {TEMPLATE_PATH}")
    doc = DocxTemplate(TEMPLATE_PATH)

    print(f"\n🔧 Renderizando template com contexto...")
    print(f"   Context keys: {list(context.keys())}")

    # Adiciona debugging extra
    print(f"\n🔍 DETALHES DAS SKILLS:")
    print(f"   skills (list): {context['skills']}")
    print(f"   skills_str (str): {context['skills_str']}")
    print(f"   skills_list (list of dicts): {context['skills_list']}")

    print(f"\n🔍 DETALHES DOS PROJETOS:")
    for i, proj in enumerate(context["projects"], 1):
        print(f"   {i}. {proj['title']}")
        print(f"      Tech: {proj['tech']}")
        print(f"      Desc: {proj['description'][:60]}...")

    doc.render(context)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"CV_Alessandro_TEST_{timestamp}.docx"
    save_path = os.path.join(OUTPUT_DIR, filename)

    print(f"\n💾 Salvando documento: {save_path}")
    doc.save(save_path)

    print(f"\n✅ SUCESSO! Documento gerado:")
    print(f"   📁 {save_path}")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERRO ao gerar documento:")
    print(f"   {str(e)}")
    import traceback

    print(traceback.format_exc())
