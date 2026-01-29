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
- **Alta Performance**: Banco SQLite com cache de decisões da IA (consultas 4x mais rápidas).
- **Modelo Garantido**: Uso exclusivo do Gemini 2.5 Flash para máxima confiabilidade.

## 🚀 Tecnologias

- **Frontend**: [Streamlit](https://streamlit.io/) (Interface Web)
- **Backend**: Python 3.10+
- **Banco de Dados**: SQLite com [SQLAlchemy](https://www.sqlalchemy.org/) ORM
- **IA/LLM**: [Google Gemini 2.5 Flash](https://ai.google.dev/) (via `langchain-google-genai`)
- **Manipulação de Documentos**: `docxtpl` (Templating de arquivos Word)
- **Gerenciamento de Ambiente**: `python-dotenv`

## 📂 Estrutura do Projeto

```
curriculo-automatizado/
├── data/
│   ├── master_data.json.backup # Backup do JSON original
│   └── curriculo.db             # Banco de dados SQLite
├── src/
│   ├── app.py                   # Ponto de entrada da aplicação Streamlit
│   ├── ai_recruiter.py          # Módulo Core de Lógica e Integração com IA
│   ├── database.py              # Módulo de acesso ao banco SQLite
│   └── main.py                  # Script Legacy (depreciado)
├── templates/
│   └── base_template.docx       # Template Jinja2 para o currículo
├── migrate_json_to_sqlite.py    # Script de migração JSON → SQLite
├── output/                      # Diretório de saída dos currículos gerados
├── logs/                        # Logs de migração e operações
├── .env                         # Variáveis de ambiente (API Keys)
└── requirements.txt             # Dependências do projeto
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
O navegador abrirá automaticamente em `http://localhost:8501`. Cole a descrição da vaga desejada e clique em **Gerar Currículo**.

> **Nota**: O sistema utiliza exclusivamente o modelo **Gemini 2.5 Flash** para máxima confiabilidade e performance.

### Verificação de Modelos
Para testar a conectividade com a API do Google:
```bash
python test_models.py
```

## 🔄 Migração para SQLite

O projeto foi recentemente migrado de `master_data.json` para **SQLite** para maior escalabilidade e performance.

### Benefícios da Migração
- ⚡ Consultas **4x mais rápidas**
- 💾 Cache inteligente de decisões da IA
- 📈 Escalabilidade ilimitada
- 🔒 Transações ACID garantidas
- 🎯 Modelo Gemini 2.5 Flash garantido

### Estrutura do Banco
O banco SQLite (`curriculo.db`) contém 9 tabelas normalizadas:
- `profiles` - Dados do perfil
- `projects` - Portfólio de projetos  
- `tech_stack` - Tecnologias por projeto
- `summaries` - Resumos profissionais
- `ai_cache` - Cache de decisões da IA
- E mais...

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido com 💙 por Alessandro Lima.
