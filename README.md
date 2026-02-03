# Nexus AI Recruiter

> Sistema Inteligente de Geração Automatizada de Currículos com IA

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Visão Geral

O **Nexus AI Recruiter** é uma aplicação desenvolvida para automatizar e otimizar a personalização de currículos para vagas tech. Utilizando o modelo **Google Gemini 2.5 Flash**, o sistema analisa descrições de vagas em tempo real e reestrutura dinamicamente o currículo do candidato para destacar as experiências, projetos e habilidades mais relevantes para aquela oportunidade específica.

### ✨ Principais Funcionalidades

- **🤖 Análise Inteligente de Vagas**: Compreensão semântica profunda dos requisitos (skills, stack, cultura)
- **📝 Geração Automática de Currículos**: Seleção estratégica de projetos e resumos personalizados
- **📧 Cartas de Apresentação**: Geração opcional de cover letters humanizadas
- **🌍 Suporte Multilíngue**: Auto-detecção ou forçar Português/Inglês
- **🎨 Interface Moderna**: UI premium com gradientes, glassmorphism e animações suaves
- **📦 Download em ZIP**: Baixe currículo + carta de uma vez
- **💾 Banco de Dados SQLite**: Armazenamento eficiente de perfil e projetos
- **🔧 Validações Ultra-Rígidas**: Sistema que evita frases genéricas e corporativas

## 🚀 Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| **Frontend** | [Streamlit](https://streamlit.io/) com CSS customizado |
| **Backend** | Python 3.10+ |
| **Database** | SQLite com [SQLAlchemy](https://www.sqlalchemy.org/) ORM |
| **IA/LLM** | [Google Gemini 2.5 Flash](https://ai.google.dev/) via `langchain-google-genai` |
| **Documentos** | `docxtpl` para templating de arquivos Word |
| **Ambiente** | `python-dotenv` para gerenciamento de variáveis |

## 📂 Estrutura do Projeto

```
curriculo-automatizado/
├── data/
│   └── curriculo.db              # Banco de dados SQLite (perfil, projetos, skills)
├── src/
│   ├── app.py                    # Interface Streamlit (ponto de entrada)
│   ├── ai_recruiter.py           # Engine de IA e lógica principal
│   ├── database.py               # Camada de persistência (ORM)
│   ├── translations.py           # Sistema de internacionalização (i18n)
│   └── ai_service.py             # Serviço legado de IA
├── templates/
│   ├── base_template.docx        # Template PT-BR
│   └── base_template_en.docx     # Template EN-US
├── output/                       # Currículos e cartas gerados
├── logs/                         # Logs de execução
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore                    # Arquivos ignorados pelo Git
├── requirements.txt              # Dependências Python
└── README.md                     # Este arquivo
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos

- **Python 3.10+** instalado
- **Chave de API do Google Gemini** ([obtenha aqui](https://ai.google.dev/))

### 2. Clonar o Repositório

```bash
git clone https://github.com/alessandrolsdev/curriculo-automatizado.git
cd curriculo-automatizado
```

### 3. Configurar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure sua API key:

```bash
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave:

```env
GOOGLE_API_KEY=sua_chave_aqui
```

## ▶️ Como Usar

### Iniciar a Aplicação

```bash
streamlit run src/app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

### Workflow de Uso

1. **[Opcional] Preencha informações da vaga:**
   - Título da vaga (ex: "Backend Developer")
   - Nome da empresa (ex: "Google")

2. **Selecione o idioma:**
   - 🔍 Auto-detectar (padrão)
   - 🇧🇷 Forçar Português
   - 🇺🇸 Forçar Inglês

3. **Marque a opção de carta de apresentação** (se desejar)

4. **Cole a descrição completa da vaga**

5. **Clique em "✨ Analisar e Gerar"**

6. **Baixe o pacote ZIP** contendo:
   - Currículo personalizado (.docx)
   - Carta de apresentação (.txt) - se marcado

### Exemplo de Output

**Arquivos gerados:**
```
output/
├── CV_Alessandro_Backend_Developer_PT_20260203_120530.docx
├── CoverLetter_Alessandro_PT_20260203_120530.txt
└── Candidatura_Alessandro_Backend_Developer_20260203.zip
```

## 🗄️ Banco de Dados

O sistema utiliza **SQLite** com as seguintes tabelas:

| Tabela | Descrição |
|--------|-----------|
| `profiles` | Dados pessoais e contato |
| `education` | Formação acadêmica |
| `summaries` | Resumos profissionais (frontend, backend, fullstack) |
| `projects` | Portfólio de projetos |
| `tech_stack` | Tecnologias por projeto |
| `project_descriptions` | Descrições focadas por área |
| `hard_skills` | Habilidades técnicas categorizadas |
| `languages` | Idiomas |

### Localização do Banco

```
data/curriculo.db
```

O banco é criado automaticamente na primeira execução através do módulo `database.py`.

## 🎨 UI/UX Design

A interface foi completamente redesenhada com:

- ✨ **Background animado** com gradiente em loop
- 💎 **Glassmorphism** nos cards e inputs
- 🌈 **Gradientes dinâmicos** em botões e títulos
- ⚡ **Animações suaves** em hover e focus
- 🎯 **Feedback visual** em todas as interações
- 📱 **Design responsivo** e moderno
- 🎨 **Scrollbar customizada** com gradiente

## 🧠 Engine de IA (V8.2)

### Características do Prompt

- **Modelo**: Gemini 2.5 Flash
- **Temperatura**: 0.20 (respostas consistentes)
- **Validações Ultra-Rígidas**:
  - ❌ Proíbe 3ª pessoa ("Alessandro se destaca")
  - ❌ Proíbe frases corporativas ("sólida base", "expertise")
  - ✅ Limita sumário a 400-550 caracteres
  - ✅ Força exatamente 3 projetos
  - ✅ Valida idioma forçado

### Sistema de Validação

O sistema aplica múltiplas camadas de validação pós-IA:

```python
# Exemplo de validação automática
- Remove nome completo no meio do texto
- Substitui frases proibidas
- Unifica múltiplos parágrafos
- Limita quantidade de projetos
- Verifica linguagem corporativa
```

## 🌍 Internacionalização (i18n)

Sistema completo de tradução que adapta:

- ✅ Templates de currículo (PT-BR / EN-US)
- ✅ Experiências profissionais
- ✅ Títulos e labels
- ✅ Cartas de apresentação

**Detecção automática** baseada em keywords da vaga:
- PT: "Buscamos", "requisitos", "será responsável"
- EN: "We are looking", "requirements", "responsibilities"

## 📝 Documentação dos Componentes

### `src/app.py`
Interface Streamlit com design premium. Gerencia inputs do usuário, controle de idioma, geração de currículos/cartas e download em ZIP.

### `src/ai_recruiter.py`
Engine principal de IA. Contém o prompt V8.2 ultra-validado, integração com Gemini, validações pós-geração e construção de contexto.

### `src/database.py`
Camada de persistência com SQLAlchemy ORM. Define modelos de dados, sessões e funções helper para acesso ao banco.

### `src/translations.py`
Sistema de internacionalização. Traduz experiências profissionais e seleciona templates corretos baseado no idioma.

## 🔧 Scripts Utilitários

### Verificar Conectividade

```bash
python test_models.py
```

Testa a conexão com a API do Google Gemini.

## 📦 Dependências Principais

```
streamlit>=1.28.0
langchain-google-genai>=1.0.0
sqlalchemy>=2.0.0
docxtpl>=0.16.7
python-dotenv>=1.0.0
```

Veja `requirements.txt` para a lista completa.

## 🚧 Melhorias Futuras

- [ ] Sistema de templates customizáveis
- [ ] Histórico de currículos gerados
- [ ] Exportação para PDF
- [ ] API REST para integração
- [ ] Dashboard de analytics
- [ ] Sistema de usuários múltiplos

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Alessandro Lima**
- GitHub: [@alessandrolsdev](https://github.com/alessandrolsdev)
- LinkedIn: [Alessandro Lima](https://linkedin.com/in/alessandrolsdev)

---

<div align="center">
  Desenvolvido com 💙 e ☕ por Alessandro Lima
</div>
