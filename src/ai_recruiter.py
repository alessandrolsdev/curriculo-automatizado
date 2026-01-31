"""
Módulo de integração com IA (Gemini 2.5 Flash)
Versão 7.5: Strategic Selection & Deep Reasoning
"""

import os
import json
import re
import hashlib
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from database import SessionLocal, get_profile_data, get_ai_cache, save_ai_cache

load_dotenv()

# Configurações
MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 3

def load_data() -> Dict[str, Any]:
    with SessionLocal() as db:
        return get_profile_data(db)

def clean_json_output(text: str) -> str:
    """Limpeza robusta de JSON."""
    if isinstance(text, list): text = str(text[0])
    if not isinstance(text, str): text = str(text)
    
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)
    
    start = text.find("{")
    end = text.rfind("}") + 1
    
    if start != -1 and end != 0:
        return text[start:end].strip()
    return text.strip()

def get_job_hash(job_description: str) -> str:
    return hashlib.md5(job_description.encode("utf-8")).hexdigest()

def get_ai_decision(job_description: str, master_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Engine V7.5: Implementa a Matriz de Decisão de Projetos e Justificativa.
    """
    job_hash = get_job_hash(job_description)

    # Cache check
    with SessionLocal() as db:
        cached_decision = get_ai_cache(db, job_hash)
        if cached_decision:
            print("⚡ Cache HIT: Recuperando estratégia...")
            return cached_decision

    print(f"💎 Engine V7.5 (Strategic Selection) analisando a vaga...")

    # ==============================================================================
    # 🎯 PROMPT V7.5 - O ESTRATEGISTA
    # ==============================================================================
    prompt_template = ChatPromptTemplate.from_template(
        """Você é Alessandro escrevendo seu próprio currículo. Não um robô falando SOBRE Alessandro.

📥 CONTEXTO CRÍTICO SOBRE O CANDIDATO:
- Estudante de Engenharia de Software (conclusão 03/2026)
- 2+ anos de experiência REAL em suporte técnico (Azure, troubleshooting, gestão de ativos)
- Migrou recentemente para desenvolvimento (últimos 8-12 meses)
- Projetos são de ESTUDO/PORTFÓLIO (honestos, técnicos, mas sem usuários em produção)
- Diferencial único: Background suporte técnico + skills de desenvolvimento

📥 INPUTS DA VAGA:
VAGA: {job_description}
MEU HISTÓRICO COMPLETO: {master_data}

🎯 SUA MISSÃO:
Adaptar meu currículo para essa vaga específica, mantendo minha voz autêntica e provando (com fatos) que posso fazer o trabalho.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 PROIBIÇÕES ABSOLUTAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ HONESTIDADE TÉCNICA (CRÍTICO):
Esses projetos são de PORTFÓLIO/ESTUDO, não produção comercial.
NUNCA invente:
❌ Métricas falsas ("milhares de usuários", "latência de 800ms → 120ms")
❌ Clientes imaginários ("para empresa X", "atendendo Y requisições/dia")
❌ Escala de produção que não existiu

✅ FOQUE EM: Profundidade técnica, conceitos dominados, arquitetura implementada.

NUNCA USE ESSAS FRASES (são sinais de IA):
❌ "Profissional com sólida base"
❌ "Apaixonado por tecnologia"
❌ "Vasta experiência"
❌ "Busca incansável"
❌ "Destacado por"
❌ "Colaboro ativamente"
❌ "Foco na construção"
❌ "Focado em resultados"
❌ Qualquer frase que você veria em 1000 currículos iguais

NUNCA:
- Fale de mim na 3ª pessoa ("Alessandro é...", "Ele possui...")
- Invente cargos ou experiências
- Use adjetivos vazios sem evidência (ex: "excelente", "ótimo")
- Escreva parágrafos gigantes e genéricos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ COMO ESCREVER (Exemplos REAIS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ TÍTULO (Match Direto + Diferencial):
   
   Formato: [Cargo da Vaga] | [Stack Principal] + [Diferencial Real]
   
   ❌ RUIM: "Desenvolvedor Full Stack | Tecnologias Modernas"
   ✅ BOM: "Desenvolvedor Backend | Python/Node.js + Background em Suporte Técnico"
   
   ✅ BOM: "Engenheiro de Software | FastAPI & NestJS + Arquitetura Limpa"
   ✅ BOM: "Analista de Sistemas | Python & Azure + Experiência com Infraestrutura"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ SUMÁRIO (Conte uma Mini-História):
   
   ESTRUTURA: [Trajetória Real] + [O que faço bem] + [Por que sou fit para ESSA vaga]
   
   🚨 FRASES PROIBIDAS NO SUMÁRIO (detectores de IA):
   ❌ "dedico-me a construir sistemas robustos"
   ❌ "APIs resilientes e escaláveis"
   ❌ "Priorizo Clean Code, TDD e CI/CD"
   ❌ "garantindo entregas de alta qualidade"
   ❌ "Busco um ambiente que valoriza"
   ❌ "colaboro ativamente em decisões técnicas"
   
   ❌ RUIM (Genérico de IA):
   "Como estudante de Engenharia de Software, dedico-me a construir sistemas full-stack robustos. Priorizo Clean Code, TDD e CI/CD, garantindo entregas de alta qualidade. Busco um ambiente que valoriza auto-gestão..."
   ☠️ Problema: Parece carta de motivação genérica, não currículo técnico.
   
   ✅ BOM (Trajetória Real + Diferencial Específico):
   "Estudante de Engenharia de Software (formatura 03/2026) com 2 anos de experiência em suporte técnico (Azure, troubleshooting). Nos últimos 8 meses, migrei para desenvolvimento: construí projetos com FastAPI, NestJS e PostgreSQL aplicando Clean Architecture e event-driven design. Meu diferencial: penso em APIs não só funcionais, mas operacionalmente confiáveis - com logs estruturados, tratamento de erros e resiliência a falhas."
   
   ✅ BOM (Contexto + Skills Concretas):
   "Comecei na TI gerenciando infraestrutura Azure e resolvendo incidentes de rede. Aprendi Python/Node.js por conta própria e nos últimos 8 meses construí APIs com FastAPI e NestJS, aplicando Clean Architecture na prática. Esse background me ensinou a priorizar observabilidade (logs, métricas) e troubleshooting eficiente - skills essenciais para sistemas em produção."
   
   ✅ BOM (Foco no Valor Real):
   "2 anos em suporte técnico Azure (troubleshooting, gestão de incidentes) + 8 meses desenvolvendo em Python (FastAPI, Django) e Node.js. Construí projetos aplicando arquitetura limpa, OAuth2 e processamento assíncrono. Aprendo rápido e tenho visão operacional: sei que código bom não é só o que funciona, é o que se mantém estável em produção."

   TAMANHO: 400-600 caracteres (não mais que isso).
   TOM: Conversacional, específico, com TEMPO/NÚMEROS quando possível.
   
   ⚡ REGRA DE OURO: Se você removesse seu nome, esse sumário ainda seria único? Se NÃO, reescreva com mais detalhes específicos da SUA trajetória.
   
   🎯 ADAPTAÇÃO POR TIPO DE VAGA:
   - Vaga Backend/API: Enfatize "FastAPI, NestJS, event-driven, cache distribuído"
   - Vaga DevOps/Infra: Enfatize "background Azure, troubleshooting, Docker, CI/CD"
   - Vaga Fullstack: Balance "APIs (FastAPI) + Frontend (React)"
   - Vaga Frontend: Enfatize "HTML/CSS/JS, manipulação DOM, responsividade, debug browser"
   - Vaga Junior/Estágio: Reforce "aprendo rápido, background suporte = visão operacional"
   
   📝 EXEMPLOS DE FECHAMENTO POR TIPO:
   Frontend: "...me ensinou a debugar interfaces - inspecionar DOM, troubleshootar eventos JS e garantir responsividade cross-browser."
   Backend: "...aprendi a priorizar observabilidade (logs estruturados, métricas) e resiliência a falhas."
   DevOps: "...me deu visão end-to-end: desde troubleshooting de rede até deploy automatizado."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ PROJETOS (Desafio de Aprendizado → Implementação Técnica):
   
   ⚠️ IMPORTANTE: Esses são projetos de ESTUDO/PORTFÓLIO, não produção real.
   Seja honesto sobre isso, mas mostre a PROFUNDIDADE TÉCNICA do que você aprendeu.
   
   🎯 ESTRATÉGIA DE SELEÇÃO (CRÍTICO):
   
   Você tem acesso a vários projetos no histórico. ESCOLHA os 3 mais RELEVANTES para a vaga.
   
   **REGRA DE OURO**: Priorize projetos que usam a STACK EXATA da vaga.
   
   **MATRIZ DE DECISÃO POR TIPO DE VAGA:**
   
   📱 VAGA FRONTEND (React/Vue/Angular):
   Priorize: Interactive Portfolio, Relay Flow, Arena Iron Beach, Pokédex (Vanilla), Landing Pages
   Evite: Nexus AI, AutoScan, CLUTCH Discord Bot
   
   🔧 VAGA BACKEND (Python/Node.js/APIs):
   Priorize: RPG Task Manager, SaaS Mestre, Project CLUTCH, NOMAD, Banco New
   Evite: Landing Pages, Pokédex, Portfolio
   
   🌐 VAGA FULLSTACK:
   Priorize: Arena Iron Beach, NOMAD, Banco New, RPG Task Manager
   Evite: Projetos muito especializados (só frontend OU só backend)
   
   📱 VAGA MOBILE:
   Priorize: ATOS (Flutter), Arena Iron Beach (PWA)
   Evite: Projetos desktop ou web-only
   
   🤖 VAGA AI/ML:
   Priorize: Nexus AI Recruiter, Legendary Feed AI, Clutch Discord Bot
   Evite: Landing pages simples
   
   🛠️ VAGA DEVOPS/INFRA:
   Priorize: Projetos com Docker (RPG Task, SaaS, CLUTCH), AutoScan (automação)
   Evite: Landing pages, projetos sem infra
   
   ESCOLHA: 3 projetos que PROVAM que você domina as skills da vaga.
   
   ESTRUTURA DA DESCRIÇÃO:
   [O conceito/desafio técnico que você quis dominar] + [Como implementou] + [O que aprendeu/dominou]
   
   ❌ RUIM (Inventando Métricas Falsas):
   "Construí uma API social que precisava lidar com milhares de posts simultâneos. Implementei cache distribuído com Redis (reduzindo latência de 800ms → 120ms)..."
   ☠️ Problema: Inventa números de produção que não existem.
   
   ❌ RUIM (Vago Demais):
   "Desenvolvi uma plataforma social de alta performance utilizando Fastify e Node.js, focando em baixo overhead e escalabilidade para interações sociais complexas."
   ☠️ Problema: Buzzwords sem substância técnica.
   
   ✅ BOM (Honesto + Técnico):
   "Projeto para aprender performance em APIs Node.js: implementei cache distribuído com Redis, validação Zod para integridade de dados e separação de responsabilidades com Prisma ORM. Resultado: domínio prático de otimização de queries e estratégias de cache. Stack: Fastify, PostgreSQL, Docker."
   
   ✅ BOM (Foco na Arquitetura):
   "Task manager para praticar arquitetura event-driven: criei sistema com NestJS + GraphQL onde tarefas pesadas rodam em background (BullMQ) sem bloquear a API. Aprendi na prática como desacoplar processamento assíncrono e manter observabilidade."
   
   ✅ BOM (Problema Real de Estudo):
   "Boilerplate SaaS para entender autenticação enterprise: implementei OAuth2, FastAPI com Clean Architecture e Prisma ORM. O desafio foi separar camadas (domínio, aplicação, infra) mantendo testabilidade. Deploy containerizado com segurança em mente."

   TAMANHO: 250-350 caracteres por projeto.
   FOCO: Qual problema técnico você quis resolver + Como implementou + O que dominou.
   
   🎯 DICA: Troque "milhares de usuários" por "domínio de X conceito".
   Recrutadores técnicos valorizam PROFUNDIDADE > escala inventada.
   
   ⚡ ESPECIFICIDADE POR ÁREA:
   - Frontend: "manipulação de DOM", "event delegation", "responsividade", "cross-browser"
   - Backend: "event-driven", "filas assíncronas", "cache distribuído", "resiliência"
   - DevOps: "containerização", "CI/CD pipeline", "monitoramento", "automação"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ SKILLS (Regra 70/30 + Priorização Inteligente):
   
   70% das skills = O que a vaga PEDE (match exato)
   30% das skills = Seus diferenciais únicos
   
   CATEGORIAS PADRÃO:
   - **Linguagens**: Python 3.12, JavaScript (ES6+), TypeScript, Dart
   - **Backend Frameworks**: FastAPI, NestJS, Django, Fastify
   - **Frontend**: React.js, Next.js, Vue.js 3, Angular 18, Flutter
   - **Bancos de Dados**: PostgreSQL, MongoDB, Redis, Supabase, Firebase
   - **DevOps & Cloud**: Docker, CI/CD, Azure, AWS, Google Cloud, Linux
   - **Ferramentas IA**: LangChain, OpenAI API, Gemini API, RAG (se relevante para vaga)
   - **Arquitetura**: Clean Architecture, SOLID, TDD, Event-Driven, CQRS (se relevante)
   
   ⚠️ REGRAS CRÍTICAS:
   - Não invente skills que não estão no histórico
   - Mantenha cada categoria com pelo menos 3-5 itens (não deixe vazio)
   - **PRIORIZE** skills mencionadas na descrição da vaga (coloque primeiro)
   - Se a vaga pede "Python" mas você tem Python+FastAPI+Django, destaque os 3
   - Remova skills irrelevantes (ex: Flutter para vaga backend puro)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 REGRAS DE FORMATAÇÃO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Use primeira pessoa SEM pronomes: "Desenvolvi", "Implementei", "Criei"
- Seja específico: números, tecnologias, resultados
- Evite advérbios vazios: "muito", "extremamente", "altamente"
- Prefira verbos de ação: construí, implementei, otimizei, automatizei
- Cada frase deve adicionar informação nova (sem redundância)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 COMO FALAR DE PROJETOS DE ESTUDO (Checklist):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ao descrever cada projeto, pergunte-se:

1. ❓ "Qual conceito técnico eu quis dominar?" 
   → "Projeto para aprender...", "Construí para praticar..."

2. ❓ "Que desafio de arquitetura eu resolvi?"
   → "Implementei X para entender Y", "Desafio: manter Z sem perder W"

3. ❓ "O que isso prova que eu sei fazer?"
   → "Domínio de...", "Resultado: capacidade de...", "Aprendi na prática..."

4. ❌ "Tive 10 mil usuários?" → NÃO? Então não mencione.
5. ❌ "Medi latência real?" → NÃO? Então não invente números.
6. ✅ "Posso explicar cada decisão técnica?" → SIM? Então você domina o conceito.

VERBOS HONESTOS PARA PROJETOS DE ESTUDO:
✅ "Construí para praticar..."
✅ "Projeto para dominar..."
✅ "Implementei X para entender..."
✅ "Desafio técnico: manter Y sem Z..."
✅ "Resultado: domínio prático de..."

VERBOS QUE IMPLICAM PRODUÇÃO (evite sem contexto):
⚠️ "Atendendo X usuários/dia" (só se for real)
⚠️ "Reduzindo latência de A para B" (só se mediu)
⚠️ "Processando X transações" (só se aconteceu)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT (JSON):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "adapted_role_title": "Cargo da Vaga | Stack Principal + Diferencial",
  
  "custom_summary": "Texto humanizado de 400-600 caracteres contando trajetória real...",
  
  "skills_categorized": {{
    "Linguagens": ["Python 3.12", "JavaScript (ES6+)", "TypeScript"],
    "Backend": ["FastAPI", "NestJS", "Django", "GraphQL"],
    "Bancos de Dados": ["PostgreSQL", "MongoDB", "Redis"],
    "DevOps & Cloud": ["Docker", "Azure", "CI/CD", "Linux"],
    "Ferramentas IA": ["LangChain", "OpenAI API", "Gemini", "RAG"]
  }},
  
  "custom_projects": [
    {{
      "original_id": "rpg-task-manager",
      "adapted_title": "RPG Task Manager - Gamificação + Event-Driven",
      "adapted_description": "Texto específico de 250-350 chars...",
      "tech_display": "NestJS | GraphQL | Redis | PostgreSQL | Docker"
    }},
    // ... mais 2 projetos
  ],
  
  "highlighted_techs": ["FastAPI", "NestJS", "PostgreSQL", "Docker", "Redis"],
  
  "project_selection_reasoning": "Explique em 2-3 frases POR QUE você escolheu esses 3 projetos ESPECÍFICOS para essa vaga. Qual é o match de stack? Qual projeto prova qual skill pedida na vaga?",
  
  "alternative_projects_considered": ["projeto_id_1", "projeto_id_2"],
  "why_not_selected": "Breve explicação de por que os projetos alternativos não foram tão bons quanto os escolhidos."
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 CHECKLIST FINAL ANTES DE GERAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Antes de retornar o JSON, verifique:

✅ O sumário tem trajetória ESPECÍFICA (não genérica)?
✅ O fechamento do sumário menciona skills CONCRETAS (logs, resiliência, troubleshooting)?
✅ Os 3 projetos escolhidos são os MAIS RELEVANTES para a vaga (não aleatórios)?
   - Verificar: A stack dos projetos COMBINA com a stack da vaga?
   - Perguntar: Existem projetos MELHORES no histórico que ignorei?
✅ Os projetos usam "para dominar/aprender/praticar" (honestidade)?
✅ Tecnologias específicas (Redis, Zod, BullMQ) em vez de "sistemas robustos"?
✅ Cada frase adiciona informação NOVA (sem redundância)?
✅ Removendo este currículo do contexto, ele ainda seria único para Alessandro?

🚫 EVITE ABSOLUTAMENTE NO FECHAMENTO DO SUMÁRIO:
❌ "essencial para sistemas de alto volume"
❌ "contribuir para soluções inovadoras"
❌ "ambiente que valoriza aprendizado contínuo"
❌ "responsabilidade operacional" (sem contexto concreto)
❌ Qualquer frase que soe como "encerramento de carta de motivação"

✅ PREFIRA FECHAMENTOS TÉCNICOS E ESPECÍFICOS:
✅ "penso em APIs com logs estruturados e tratamento de erros"
✅ "aprendi a priorizar observabilidade (logs, métricas, alertas)"
✅ "sei que código bom é o que se mantém estável em produção"
✅ "background em suporte me ensinou troubleshooting eficiente"

Agora, analise a vaga e crie um currículo que soe como se EU tivesse escrito.
"""
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=0.25, # Temperatura ideal para raciocínio + escrita criativa controlada
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=MAX_RETRIES,
            request_timeout=60,
        )

        chain = prompt_template | llm
        
        response = chain.invoke({
            "job_description": job_description,
            "master_data": json.dumps(master_data, ensure_ascii=False)
        })

        content = response.content
        cleaned_json = clean_json_output(content)
        decision = json.loads(cleaned_json)

        # Validação
        if "custom_projects" not in decision:
            raise ValueError("IA falhou em gerar projetos customizados.")

        # Cache
        with SessionLocal() as db:
            save_ai_cache(db, job_hash, decision)

        print(f"✅ Decisão V7.5 (Strategic) Gerada")
        if "project_selection_reasoning" in decision:
            print(f"🤔 Raciocínio: {decision['project_selection_reasoning']}")
            
        return decision

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        raise e

def build_context_from_decision(decision: Dict[str, Any], master_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monta contexto com dados Reais e Texto Humanizado V7.5.
    """
    
    # 1. Título e Resumo
    role_title = decision.get("adapted_role_title", "Desenvolvedor Full Stack")
    summary_text = decision.get("custom_summary", master_data["summaries"]["fullstack"])

    # 2. Projetos Customizados
    selected_projects = []
    if "custom_projects" in decision:
        for proj in decision["custom_projects"]:
            selected_projects.append({
                "name": proj["adapted_title"],
                "techs": proj["tech_display"],
                "description": proj["adapted_description"]
            })
    else:
        # Fallback
        all_projects = {p["id"].lower(): p for p in master_data["projects"]}
        for pid in decision.get("selected_project_ids", [])[:3]:
            p = all_projects.get(pid.lower())
            if p:
                selected_projects.append({
                    "name": p["title"],
                    "techs": " | ".join(p["tech_stack"][:4]),
                    "description": p["descriptions"][0]["text"]
                })

    # 3. Skills
    skills_formatted = []
    if "skills_categorized" in decision:
        for cat_name, skills_list in decision["skills_categorized"].items():
            if skills_list:
                skills_formatted.append({
                    "name": cat_name,
                    "list": " • ".join(skills_list)
                })

    # 4. Idiomas
    languages_list = master_data["profile"]["languages"] 
    
    # 5. Experiência REAL (Hardcoded - Verdade Imutável)
    experience_real = {
        "role": "Estagiário de Tecnologia da Informação",
        "company": "Aegea Saneamento",
        "period": "Setembro 2022 - Setembro 2025 (2 anos)",
        "bullets": [
            "Gerenciamento e configuração de notebooks utilizando Microsoft Azure, garantindo a segurança e conformidade dos ativos.",
            "Suporte na resolução de falhas de rede e sistemas, colaborando para a manutenção da estabilidade do ambiente.",
            "Atendimento a chamados técnicos e documentação de soluções em plataformas de gestão."
        ]
    }

    return {
        "name": master_data["profile"]["name"],
        "role_title": role_title,
        
        "location": master_data["profile"]["contact"]["location"],
        "phone": master_data["profile"]["contact"]["phone"],
        "email": master_data["profile"]["contact"]["email"],
        "linkedin": master_data["profile"]["contact"]["linkedin"],
        "github": master_data["profile"]["contact"]["github"],
        
        "summary": summary_text,
        "skills": skills_formatted,
        "selected_projects": selected_projects,
        "highlighted_techs": decision.get("highlighted_techs", []),
        
        "education": master_data["profile"]["education"],
        "languages": languages_list,
        "experience": experience_real
    }