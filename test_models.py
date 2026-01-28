import os
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Configurações
load_dotenv()
console = Console()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Lista de suspeitos baseada na sua imagem
CANDIDATES = [
    "gemini-3-pro",
    "gemini-3-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash"
]

def test_models():
    table = Table(title="🔍 Relatório de Disponibilidade de Modelos")
    table.add_column("Modelo", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Detalhe", style="dim")

    print("Testando conexão com os modelos...")
    
    for model_name in CANDIDATES:
        try:
            # Tenta gerar um "Oi" simples
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Teste de conexão.")
            
            if response.text:
                table.add_row(model_name, "[green]DISPONÍVEL[/green]", "Sucesso total")
            else:
                table.add_row(model_name, "[yellow]INCERTO[/yellow]", "Sem resposta de texto")
                
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                status = "[red]NÃO ENCONTRADO[/red]"
                detail = "Nome incorreto ou não liberado"
            elif "429" in error_msg:
                status = "[orange1]COTA EXCEDIDA[/orange1]"
                detail = "Limite 0 ou Plano Gratuito"
            else:
                status = "[red]ERRO[/red]"
                detail = error_msg[:30] + "..."
            
            table.add_row(model_name, status, detail)

    console.print(table)

if __name__ == "__main__":
    test_models()