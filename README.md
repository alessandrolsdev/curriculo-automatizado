# Nexus AI Recruiter

> Sistema Inteligente de Otimização e Geração de Currículos.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Visão Geral

O **Nexus AI Recruiter** é uma aplicação desenvolvida para automatizar e otimizar a personalização de currículos tech. Utilizando a API **Google Gemini Pro**, o sistema analisa descrições de vagas em tempo real e reestrutura o currículo do candidato para destacar as experiências, projetos e habilidades mais relevantes para aquela oportunidade específica.

### Diferenciais
- **Análise Semântica**: Compreensão profunda dos requisitos da vaga (Skills, Stack, Cultura).
- **Adaptação Dinâmica**: Seleção inteligente de projetos e resumos profissionais.
- **Interface Moderna**: UI desenvolvida em Streamlit com design system responsivo e Glassmorphism.
- **Saída Otimizada**: Geração de arquivos `.docx` prontos para ATS (Applicant Tracking Systems).

## 🚀 Tecnologias

- **Frontend**: [Streamlit](https://streamlit.io/) (Interface Web)
- **Backend**: Python 3.10+
- **IA/LLM**: [Google Gemini](https://ai.google.dev/) (via `langchain-google-genai`)
- **Manipulação de Documentos**: `docxtpl` (Templating de arquivos Word)
- **Gerenciamento de Ambiente**: `python-dotenv`

## 📂 Estrutura do Projeto

```
curriculo-automatizado/
├── data/
│   └── master_data.json       # Base de conhecimento (Experiências, Projetos, Skills)
├── src/
│   ├── app.py                 # Ponto de entrada da aplicação Streamlit
│   ├── ai_recruiter.py        # Módulo Core de Lógica e Integração com IA
│   └── main.py                # Script Legacy para geração manual
├── templates/
│   └── base_template.docx     # Template Jinja2 para o currículo
├── output/                    # Diretório de saída dos currículos gerados
├── .env                       # Variáveis de ambiente (API Keys)
└── requirements.txt           # Dependências do projeto
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
- Python instalado (recomendado 3.10 ou superior).
- Chave de API do Google Gemini (`GOOGLE_API_KEY`).

### 2. Clonar o Repositório
```bash
git clone https://github.com/alessandrolsdev/curriculo-automatizado.git
cd curriculo-automatizado
```

### 3. Configurar Ambiente Virtual
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
GOOGLE_API_KEY=sua_chave_aqui
```

## ▶️ Como Usar

### Interface Web (Recomendado)
Para iniciar a interface interativa:

```bash
streamlit run src/app.py
```
O navegador abrirá automaticamente em `http://localhost:8501`. Cole a descrição da vaga desejada, selecione o modelo de IA e clique em **Gerar Currículo**.

### Verificação de Modelos
Para testar a conectividade com a API do Google:
```bash
python test_models.py
```

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido com 💙 por Alessandro Lima.
