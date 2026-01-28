import json
import os
from docxtpl import DocxTemplate
from datetime import datetime

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'master_data.json')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'base_template.docx')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def load_data():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_content(data, target_role="fullstack"):
    """
    Aqui é onde a mágica do 'One-Page' acontece.
    Filtramos o conteúdo baseado no foco da vaga.
    """
    context = {}
    
    # 1. Dados Pessoais (Sempre iguais)
    context['name'] = data['profile']['name']
    context['location'] = data['profile']['location']
    context['phone'] = data['profile']['phone']
    context['email'] = data['profile']['email']
    context['linkedin'] = data['profile']['linkedin']
    context['github'] = data['profile']['github']
    context['education'] = data['education']
    
    # 2. Resumo e Título (Adaptativos)
    # Se não achar o específico, usa o fullstack como padrão
    context['role_title'] = "Desenvolvedor " + target_role.title()
    context['summary'] = data['profile']['summaries'].get(target_role, data['profile']['summaries']['fullstack'])

    # 3. Skills (Filtra as irrelevantes para economizar espaço)
    # Ex: Se a vaga é RPA, frontend vai pro final ou sai
    context['skills'] = []
    
    if target_role == 'rpa':
        order = ['rpa_ai', 'backend', 'database', 'devops']
    elif target_role == 'frontend':
        order = ['frontend', 'devops']
    else:
        order = ['backend', 'frontend', 'database', 'devops', 'rpa_ai']

    for key in order:
        if key in data['skills']:
            context['skills'].append({
                'name': key.replace('_', ' & ').upper(),
                'list': ", ".join(data['skills'][key])
            })

    # 4. Projetos (O Segredo do One-Page: Limite de 3)
    context['selected_projects'] = []
    project_limit = 3
    count = 0
    
    for proj in data['projects']:
        if count >= project_limit: 
            break
            
        # Lógica simples de match: Se o tipo do projeto bate com a vaga
        # Ou se é um projeto "Fullstack" (coringa)
        is_relevant = False
        if target_role in proj['type'].lower() or 'fullstack' in proj['type'].lower():
            is_relevant = True
        
        # Para RPA, força a inclusão de projetos de automação
        if target_role == 'rpa' and 'rpa' in proj['id']:
            is_relevant = True

        if is_relevant:
            # Pega a descrição correta
            desc_text = ""
            for desc in proj['descriptions']:
                if desc['focus'] == target_role:
                    desc_text = desc['text']
                    break
            if not desc_text: # Fallback
                desc_text = proj['descriptions'][0]['text']

            context['selected_projects'].append({
                'name': proj['title'],
                'techs': " | ".join(proj['tech_stack']),
                'description': desc_text
            })
            count += 1

    # 5. Experiência (Pega a mais recente)
    # Simplificado para pegar a primeira do JSON (Aegea)
    latest_job = data['experience'][0]
    
    # Filtra bullets baseados em tags
    selected_bullets = []
    for bullet in latest_job['description_bullets']:
        # Se a vaga é em inglês, pega bullets em inglês
        if target_role == 'english' and 'text_en' in bullet:
            selected_bullets.append(bullet['text_en'])
        elif 'text' in bullet:
             selected_bullets.append(bullet['text'])
             
    context['experience'] = {
        'role': latest_job['role'],
        'company': latest_job['company'],
        'period': latest_job['period'],
        'bullets': selected_bullets[:4] # Limita a 4 bullets para não estourar
    }

    return context

def generate_cv(target_role="fullstack"):
    print(f"🤖 Gerando currículo para perfil: {target_role.upper()}...")
    
    data = load_data()
    context = filter_content(data, target_role)
    
    doc = DocxTemplate(TEMPLATE_PATH)
    doc.render(context)
    
    filename = f"Currículo_Alessandro_Lima_{target_role.upper()}_{datetime.now().strftime('%Y%m%d')}.docx"
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    doc.save(file_path)
    print(f"✅ Sucesso! Salvo em: {file_path}")

if __name__ == "__main__":
    # Teste: Gerando versões diferentes para provar que funciona
    generate_cv("rpa")
    generate_cv("frontend")
    generate_cv("backend")