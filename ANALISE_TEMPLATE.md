# Análise do Template base_template.docx

## Problema Identificado

O template Word usa variáveis Jinja2 com **nomes específicos** que não batem com o contexto que estamos enviando!

### 1. Skills
**Template espera:**
```jinja2
{% for category in skills %} • {{ category.name }}: {{ category.list }}
{% endfor %}
```

**O que estamos enviando:**
```python
"skills": ["React.js", "TypeScript", ...]  # Lista simples ❌
```

**O que devemos enviar:**
```python
"skills": [
    {"name": "Frontend", "list": "React.js, TypeScript, Next.js"},
    {"name": "Backend", "list": "Python, FastAPI, Node.js"}
]
```

---

### 2. Projects
**Template espera:**
```jinja2
{% for proj in selected_projects %}
{{ proj.name }} | {{ proj.techs }}
• {{ proj.description }}
{% endfor %}
```

**O que estamos enviando:**
```python
{"title": "...", "tech": "...", "description": "..."}  # ❌ Nomes errados!
```

**O que devemos enviar:**
```python
{"name": "...", "techs": "...", "description": "..."}  # ✅ Nomes corretos!
```

---

### 3. Education
**Template espera:**
```jinja2
{% for edu in education %}
{{ edu.degree }} | {{ edu.institution }} {{ edu.period }}
{% endfor %}
```

**O que estamos enviando:**
```python
"education": {"degree": "...", ...}  # ❌ Um objeto único!
```

**O que devemos enviar:**
```python
"education": [{"degree": "...", ...}]  # ✅ Lista de objetos!
```

---

## Solução

Corrigir a função `build_context_from_decision` em `ai_recruiter.py` para enviar os dados no formato exato que o template espera.
