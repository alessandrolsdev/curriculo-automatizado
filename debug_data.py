"""Debug script para testar carregamento de dados"""

import json

try:
    with open("data/master_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("✅ JSON carregado com sucesso!")
    print(f"\nKeys principais: {list(data.keys())}")

    # Testar acesso a summaries
    if "summaries" in data:
        print(f"\n✅ 'summaries' encontrado no root")
        print(f"   Keys disponíveis: {list(data['summaries'].keys())}")
    else:
        print("\n❌ 'summaries' NÃO encontrado no root")

    # Testar acesso a hard_skills
    if "hard_skills" in data:
        print(f"\n✅ 'hard_skills' encontrado")
        print(f"   Tipo: {type(data['hard_skills'])}")
        if isinstance(data["hard_skills"], list):
            print(f"   Total de skills: {len(data['hard_skills'])}")
    else:
        print("\n❌ 'hard_skills' NÃO encontrado")

    # Testar profile
    if "profile" in data:
        print(f"\n✅ 'profile' encontrado")
        print(f"   Keys em profile: {list(data['profile'].keys())}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback

    traceback.print_exc()
