"""
Script de Verificação de Modelos Gemini
=======================================

Utilitário para testar a conectividade e disponibilidade dos modelos
Google Generative AI configurados na conta do usuário.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Configurações Iniciais
load_dotenv()
console = Console()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Lista de modelos a serem verificados
CANDIDATES = [
    "gemini-3-pro",
    "gemini-3-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


def test_models():
    """
    Testa a geração de conteúdo simples para cada modelo na lista CANDIDATES
    e exibe um relatório formatado no terminal.
    """
    table = Table(title="🔍 Relatório de Disponibilidade de Modelos")
    table.add_column("Modelo", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Detalhe", style="dim")

    console.print("[bold]Iniciando diagnósticos de conexão...[/bold]")

    for model_name in CANDIDATES:
        try:
            # Teste de conectividade simples
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Ping.")

            if response.text:
                table.add_row(model_name, "[green]DISPONÍVEL[/green]", "Resposta OK")
            else:
                table.add_row(model_name, "[yellow]INSTÁVEL[/yellow]", "Resposta vazia")

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                status = "[red]NÃO ENCONTRADO[/red]"
                detail = "Nome invalido ou s/ acesso"
            elif "429" in error_msg:
                status = "[orange1]COTA EXCEDIDA[/orange1]"
                detail = "Quota limit reached"
            else:
                status = "[red]ERRO[/red]"
                detail = error_msg[:40] + "..."

            table.add_row(model_name, status, detail)

    console.print(table)


if __name__ == "__main__":
    test_models()
