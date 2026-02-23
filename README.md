# Nexus AI Recruiter ⚡

> **Engine V9.0**: Otimização Inteligente de Currículos com LangGraph & Gemini 2.5 Flash.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Visão Geral

O **Nexus AI Recruiter** é uma ferramenta de "Hyper-Personalization" para processos seletivos de TI. Ele não apenas "edita" um currículo, mas **reescreve** a narrativa profissional do candidato para se alinhar matematicamente com a descrição da vaga (JD), utilizando uma arquitetura de agentes (LangGraph) e um prompt de engenharia avançada ("Super Prompt").

## ✨ Funcionalidades V9.0 ("Super App")

### 🧠 Engine de IA
- **LangGraph State-Machine**: Arquitetura resiliente com auto-retry e validação em etapas.
- **Super Prompt**: Prompt ultra-rígido focada em eliminar "alucinações" e linguagem corporativa clichê.
- **Dual-Language Detection**: Detecta se a vaga é **EN-US** ou **PT-BR** (heurística + LLM fallback).
- **Sanitização Automática**: Remove artefatos de markdown (`**bold**`, `*italic*`) que quebram formatação DOCX.

### 🎨 Interface Premium ("Awwwards-level")
- **Design System Custom**: CSS injetado com animações, glassmorphism e tipografia premium (Syne + DM Sans).
- **Feedback Real-Time**: Status detalhado do processamento (loading states, steps).
- **Preview Rico**: Visualização dos projetos selecionados e skills extraídas direto na UI.

### 🛠️ Recursos Poderosos
- **Modo Dev vs. Suporte**: Templates e narrativas distintas para vagas de Desenvolvimento vs. Suporte/ITSM.
- **Cover Letter Generator**: Gera cartas de apresentação no modelo "Hook-Context-Proof-Fit" (validado para TI).
- **Download Inteligente**: Baixe o currículo DOCX, a carta TXT ou um ZIP com ambos prontos para envio.

---

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/alessandrolsdev/curriculo-automatizado.git
cd curriculo-automatizado

# Crie o ambiente virtual
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração

Crie um arquivo `.env` na raiz (use `.env.example` como base):

```env
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 3. Rodando

```bash
streamlit run src/app.py
```
O app abrirá em `http://localhost:8501`.

---

## 📂 Estrutura do Projeto

```
curriculo-automatizado/
├── src/
│   ├── app.py           # Interface Streamlit (UI/UX)
│   ├── ai_recruiter.py  # Engine V9 (LangGraph + Logic)
│   ├── database.py      # Camada de Dados (SQLite + SQLAlchemy)
│   └── translations.py  # Internacionalização e Config de Templates
├── data/
│   └── curriculo.db     # Seu banco de dados pessoal (não versionado)
├── templates/
│   ├── base_template.docx      # Template Dev PT
│   ├── base_template_en.docx   # Template Dev EN
│   ├── support_template.docx   # Template Suporte PT
│   └── support_template_en.docx# Template Suporte EN
├── output/              # Arquivos gerados (ignorados no git)
└── requirements.txt     # Dependências
```

## 🧠 Como Funciona (O "Flow")

1. **Input**: Você cola a descrição da vaga (JD).
2. **Análise**: O Engine detecta idioma e contexto (Dev ou Suporte).
3. **Seleção**: Escolhe os 3 projetos mais relevantes do seu banco `curriculo.db`.
4. **Rescrita**:
   - Adapta descrições dos projetos para focar nas techs que a vaga pede.
   - Escreve um Resumo Profissional único ("Hyper-Personalized").
5. **Renderização**: Preenche o template DOCX via `docxtpl` preservando formatação.

---

## 🛡️ Privacidade

Este projeto foi desenhado para uso **pessoal**.
- Seus dados ficam em `data/curriculo.db` (SQLite local).
- O arquivo `.gitignore` garante que seu banco de dados e suas chaves de API nunca subam para o GitHub.

---

Desenvolvido por **Alessandro Lima**.
