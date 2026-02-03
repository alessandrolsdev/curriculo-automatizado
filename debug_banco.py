"""
Script de Debug: Verificar Dados do Banco

Testa se os dados estão sendo carregados corretamente do banco SQLite.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ai_recruiter import load_data
import json

print("=" * 60)
print("DEBUG: Verificando dados do banco SQLite")
print("=" * 60)

# Carrega dados
data = load_data()

# Verifica estrutura
print(f"\n📊 ESTATÍSTICAS:")
print(f"   - Projetos: {len(data.get('projects', []))}")
print(f"   - Hard Skills: {len(data['profile'].get('hard_skills', []))}")
print(f"   - Summaries: {len(data.get('summaries', {}))}")
print(f"   - Education: {len(data['profile'].get('education', []))}")

# Mostra primeiros 3 projetos
print(f"\n🎯 PRIMEIROS 3 PROJETOS:")
for proj in data.get("projects", [])[:3]:
    print(f"\n   ID: {proj.get('id')}")
    print(f"   Título: {proj.get('title')}")
    print(f"   Tech Stack: {len(proj.get('tech_stack', []))} tecnologias")
    print(f"   Descrições: {len(proj.get('descriptions', []))} versões")

# Mostra skills
print(f"\n💪 HARD SKILLS (primeiras 10):")
for skill in data["profile"].get("hard_skills", [])[:10]:
    print(f"   - {skill}")

# Mostra summaries disponíveis
print(f"\n📝 SUMMARIES DISPONÍVEIS:")
for key in data.get("summaries", {}).keys():
    print(f"   - {key}")

# Salva JSON para inspeção
output_file = "debug_loaded_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Dados completos salvos em: {output_file}")
print("=" * 60)
