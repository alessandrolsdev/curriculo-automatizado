"""
Script de Teste: Modelo Gemini 2.5 Flash

Verifica a conectividade com a API do Google Gemini e testa o modelo 2.5 Flash.

Autor: Alessandro Lima
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Carrega variáveis de ambiente
load_dotenv()

# Modelo a ser testado
MODEL_NAME = "gemini-2.5-flash-latest"


def test_gemini_connection():
    """
    Testa a conexão com o modelo Gemini 2.5 Flash.
    Retorna True se bem-sucedido, False caso contrário.
    """
    print("=" * 60)
    print(f"TESTANDO MODELO: {MODEL_NAME}")
    print("=" * 60)

    # Verifica se a API Key está configurada
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERRO: GOOGLE_API_KEY não encontrada no arquivo .env")
        return False

    print("✅ API Key encontrada")
    print(f"🔑 Primeiros caracteres: {api_key[:10]}...")

    try:
        print(f"\n🤖 Inicializando modelo {MODEL_NAME}...")

        # Cria instância do modelo
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=0.0,
            google_api_key=api_key,
            max_retries=2,
            request_timeout=15,
        )

        print("✅ Modelo inicializado com sucesso")

        # Teste simples
        print("\n💬 Enviando mensagem de teste...")
        response = llm.invoke("Responda apenas com 'OK' se você está funcionando.")

        print(f"\n✅ RESPOSTA RECEBIDA:")
        print(f"📝 {response.content}")

        print("\n" + "=" * 60)
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"✅ Modelo {MODEL_NAME} está operacional")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ ERRO ao conectar com o modelo:")
        print(f"📋 Detalhes: {str(e)}")
        print("\n📌 Possíveis causas:")
        print("   1. API Key inválida ou expirada")
        print("   2. Sem conexão com a internet")
        print("   3. Modelo não disponível na sua região")
        print("   4. Cota da API excedida")

        return False


def test_ai_decision_simple():
    """
    Testa uma decisão simples da IA para validar o sistema completo.
    """
    from ai_recruiter import get_ai_decision, load_data

    print("\n" + "=" * 60)
    print("TESTANDO DECISÃO DA IA (INTEGRAÇÃO COMPLETA)")
    print("=" * 60)

    try:
        print("\n📂 Carregando dados do banco SQLite...")
        master_data = load_data()
        print(f"✅ Dados carregados: {len(master_data['projects'])} projetos")

        # Descrição de vaga simples para teste
        test_job = """
        Desenvolvedor Frontend Sênior - React
        
        Requisitos:
        - React.js avançado
        - TypeScript
        - Next.js
        - Tailwind CSS
        - APIs REST
        
        Experiência com PWAs será um diferencial.
        """

        print("\n🧠 Consultando IA para decisão...")
        decision = get_ai_decision(test_job, master_data)

        print(f"\n✅ DECISÃO RECEBIDA:")
        print(f"   📌 Perfil selecionado: {decision['selected_summary_key']}")
        print(f"   📌 Skills: {', '.join(decision['skills_order'][:5])}")
        print(f"   📌 Projetos selecionados: {len(decision['selected_project_ids'])}")

        for proj_id in decision["selected_project_ids"]:
            proj = next(
                (p for p in master_data["projects"] if p["id"] == proj_id), None
            )
            if proj:
                print(f"      ✓ {proj['title']}")

        print("\n" + "=" * 60)
        print("🎉 TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ ERRO no teste de integração:")
        print(f"📋 Detalhes: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    # Teste 1: Conectividade com o modelo
    success_connection = test_gemini_connection()

    if success_connection:
        # Teste 2: Integração completa
        input("\n⏸️  Pressione ENTER para executar o teste de integração...")
        test_ai_decision_simple()
    else:
        print("\n⚠️ Pulando teste de integração devido a falha de conexão")
