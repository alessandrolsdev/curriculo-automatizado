"""
Script de Teste: Build Context from Decision

Simula o processo completo de decisão e criação do contexto para o template.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ai_recruiter import load_data, build_context_from_decision

print("=" * 60)
print("TESTANDO BUILD_CONTEXT_FROM_DECISION")
print("=" * 60)

# Simula decisão da IA
fake_decision = {
    "selected_summary_key": "frontend",
    "skills_order": ["React.js", "TypeScript", "Next.js", "Tailwind", "Vue.js 3"],
    "selected_project_ids": [
        "arena_iron_beach",
        "interactive_portfolio",
        "landing_page_matias",
    ],
}

print("\n📥 Decisão simulada:")
print(json.dumps(fake_decision, indent=2, ensure_ascii=False))

# Carrega dados
print("\n📂 Carregando dados...")
master_data = load_data()

# Cria contexto
print("\n🔧 Construindo contexto...")
context = build_context_from_decision(fake_decision, master_data)

# Verifica contexto
print("\n📊 CONTEXTO GERADO:")
print(f"   Nome: {context.get('name')}")
print(f"   Role: {context.get('role')}")
print(f"   Email: {context.get('email')}")
print(f"   Summary: {context.get('summary')[:50]}...")

print(f"\n💪 SKILLS:")
print(f"   Tipo 'skills': {type(context.get('skills'))}")
print(f"   Conteúdo: {context.get('skills')}")

print(f"\n🎯 PROJETOS:")
print(f"   Quantidade: {len(context.get('projects', []))}")
for proj in context.get("projects", []):
    print(f"\n   Projeto: {proj.get('title')}")
    print(f"   Tech: {proj.get('tech')}")
    print(f"   Description: {proj.get('description')[:60]}...")

print(f"\n🎓 EDUCAÇÃO:")
edu = context.get("education", {})
print(f"   Degree: {edu.get('degree')}")
print(f"   Institution: {edu.get('institution')}")

# Salva contexto para inspeção
output_file = "debug_context.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(context, f, ensure_ascii=False, indent=2)

print(f"\n✅ Contexto completo salvo em: {output_file}")
print("=" * 60)
