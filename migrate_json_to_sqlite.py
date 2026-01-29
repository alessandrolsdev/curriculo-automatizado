"""
Script de Migração: JSON para SQLite

Este script migra os dados do master_data.json para o banco SQLite.
Executa validações de integridade e cria backup do arquivo original.

Autor: Alessandro Lima
Data: 2026-01-28
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Adiciona o diretório src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import (
    init_db,
    SessionLocal,
    Profile,
    Education,
    Summary,
    Project,
    TechStack,
    ProjectDescription,
    HardSkill,
    Language,
)

# Configurações
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "master_data.json")
JSON_BACKUP_PATH = os.path.join(BASE_DIR, "data", "master_data.json.backup")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(
    LOG_DIR, f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

# Garante que o diretório de logs existe
os.makedirs(LOG_DIR, exist_ok=True)


class MigrationLogger:
    """Logger personalizado para a migração."""

    def __init__(self, log_file):
        self.log_file = log_file
        self.messages = []

    def log(self, message, level="INFO"):
        """Adiciona mensagem ao log e exibe no console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] [{level}] {message}"

        self.messages.append(formatted_msg)
        print(formatted_msg)

    def save(self):
        """Salva todas as mensagens em arquivo."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.messages))
        print(f"\n📄 Log salvo em: {self.log_file}")


def load_json_data(logger):
    """
    Carrega e valida o arquivo JSON.

    Args:
        logger: Instância do MigrationLogger

    Returns:
        Dados do JSON em formato dict
    """
    logger.log("Carregando master_data.json...")

    if not os.path.exists(JSON_PATH):
        logger.log(f"ERRO: Arquivo não encontrado em {JSON_PATH}", "ERROR")
        sys.exit(1)

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.log(
            f"✅ JSON carregado: {len(data.get('projects', []))} projetos encontrados"
        )
        return data

    except json.JSONDecodeError as e:
        logger.log(f"ERRO ao decodificar JSON: {str(e)}", "ERROR")
        sys.exit(1)


def backup_json(logger):
    """
    Cria backup do arquivo JSON original.

    Args:
        logger: Instância do MigrationLogger
    """
    logger.log("Criando backup do JSON original...")

    try:
        shutil.copy2(JSON_PATH, JSON_BACKUP_PATH)
        logger.log(f"✅ Backup criado: {JSON_BACKUP_PATH}")
    except Exception as e:
        logger.log(f"ERRO ao criar backup: {str(e)}", "ERROR")
        sys.exit(1)


def migrate_profile(db, data, logger):
    """
    Migra dados do perfil do usuário.

    Args:
        db: Sessão do SQLAlchemy
        data: Dados completos do JSON
        logger: Instância do MigrationLogger

    Returns:
        Objeto Profile criado
    """
    logger.log("Migrando dados do perfil...")

    profile_data = data["profile"]
    contact_data = profile_data["contact"]

    # Cria o perfil
    profile = Profile(
        name=profile_data["name"],
        email=contact_data["email"],
        phone=contact_data["phone"],
        linkedin=contact_data["linkedin"],
        github=contact_data["github"],
        location=contact_data["location"],
    )

    db.add(profile)
    db.flush()  # Flush para obter o ID sem commit

    # Educação
    for edu in profile_data.get("education", []):
        education = Education(
            profile_id=profile.id,
            degree=edu["degree"],
            institution=edu["institution"],
            period=edu["period"],
        )
        db.add(education)

    # Idiomas
    for lang in profile_data.get("languages", []):
        language = Language(profile_id=profile.id, language=lang)
        db.add(language)

    # Hard Skills
    for skill in profile_data.get("hard_skills", []):
        hard_skill = HardSkill(
            profile_id=profile.id,
            skill_name=skill,
            category=None,  # Categoria pode ser adicionada futuramente
        )
        db.add(hard_skill)

    logger.log(f"✅ Perfil migrado: {profile.name}")
    logger.log(f"   - {len(profile_data.get('education', []))} formações")
    logger.log(f"   - {len(profile_data.get('languages', []))} idiomas")
    logger.log(f"   - {len(profile_data.get('hard_skills', []))} skills")

    return profile


def migrate_summaries(db, data, profile, logger):
    """
    Migra resumos profissionais.

    Args:
        db: Sessão do SQLAlchemy
        data: Dados completos do JSON
        profile: Objeto Profile
        logger: Instância do MigrationLogger
    """
    logger.log("Migrando resumos profissionais...")

    summaries_data = data.get("summaries", {})
    count = 0

    for key, text in summaries_data.items():
        summary = Summary(profile_id=profile.id, key=key, text=text)
        db.add(summary)
        count += 1

    logger.log(f"✅ {count} resumos migrados")


def migrate_projects(db, data, logger):
    """
    Migra projetos do portfólio.

    Args:
        db: Sessão do SQLAlchemy
        data: Dados completos do JSON
        logger: Instância do MigrationLogger
    """
    logger.log("Migrando projetos...")

    projects_data = data.get("projects", [])
    count = 0

    for proj_data in projects_data:
        # Cria o projeto
        project = Project(
            project_id=proj_data["id"],
            title=proj_data["title"],
            type=proj_data.get("type", "Geral"),
        )

        db.add(project)
        db.flush()  # Flush para obter o ID

        # Tech Stack
        for tech in proj_data.get("tech_stack", []):
            tech_stack = TechStack(project_id=project.id, technology=tech)
            db.add(tech_stack)

        # Descrições
        for desc in proj_data.get("descriptions", []):
            description = ProjectDescription(
                project_id=project.id, focus=desc["focus"], text=desc["text"]
            )
            db.add(description)

        count += 1
        logger.log(
            f"   ✓ {project.title} ({len(proj_data.get('tech_stack', []))} techs, {len(proj_data.get('descriptions', []))} descrições)"
        )

    logger.log(f"✅ {count} projetos migrados")


def validate_migration(db, original_data, logger):
    """
    Valida a integridade dos dados migrados.

    Args:
        db: Sessão do SQLAlchemy
        original_data: Dados originais do JSON
        logger: Instância do MigrationLogger

    Returns:
        True se validação passou, False caso contrário
    """
    logger.log("\nValidando integridade da migração...")

    errors = []

    # Validar perfil
    profile_count = db.query(Profile).count()
    if profile_count != 1:
        errors.append(f"Esperado 1 perfil, encontrado {profile_count}")

    # Validar projetos
    expected_projects = len(original_data.get("projects", []))
    actual_projects = db.query(Project).count()
    if expected_projects != actual_projects:
        errors.append(
            f"Esperado {expected_projects} projetos, encontrado {actual_projects}"
        )

    # Validar summaries
    expected_summaries = len(original_data.get("summaries", {}))
    actual_summaries = db.query(Summary).count()
    if expected_summaries != actual_summaries:
        errors.append(
            f"Esperado {expected_summaries} resumos, encontrado {actual_summaries}"
        )

    # Validar skills
    expected_skills = len(original_data["profile"].get("hard_skills", []))
    actual_skills = db.query(HardSkill).count()
    if expected_skills != actual_skills:
        errors.append(f"Esperado {expected_skills} skills, encontrado {actual_skills}")

    # Validar idiomas
    expected_languages = len(original_data["profile"].get("languages", []))
    actual_languages = db.query(Language).count()
    if expected_languages != actual_languages:
        errors.append(
            f"Esperado {expected_languages} idiomas, encontrado {actual_languages}"
        )

    if errors:
        logger.log("❌ VALIDAÇÃO FALHOU:", "ERROR")
        for error in errors:
            logger.log(f"   - {error}", "ERROR")
        return False

    logger.log("✅ Validação passou! Todos os dados foram migrados corretamente.")
    logger.log(f"\nEstatísticas finais:")
    logger.log(f"   - Perfis: {profile_count}")
    logger.log(f"   - Projetos: {actual_projects}")
    logger.log(f"   - Resumos: {actual_summaries}")
    logger.log(f"   - Skills: {actual_skills}")
    logger.log(f"   - Idiomas: {actual_languages}")
    logger.log(f"   - Tech Stack: {db.query(TechStack).count()}")
    logger.log(f"   - Descrições: {db.query(ProjectDescription).count()}")

    return True


def main():
    """Função principal da migração."""
    logger = MigrationLogger(LOG_FILE)

    logger.log("=" * 60)
    logger.log("INICIANDO MIGRAÇÃO: JSON → SQLite")
    logger.log("=" * 60)

    try:
        # 1. Carregar JSON
        data = load_json_data(logger)

        # 2. Criar backup
        backup_json(logger)

        # 3. Inicializar banco de dados
        logger.log("\nInicializando banco de dados SQLite...")
        init_db()
        logger.log("✅ Estrutura do banco criada")

        # 4. Migrar dados
        logger.log("\nIniciando migração de dados...")

        db = SessionLocal()

        try:
            # Migrar perfil
            profile = migrate_profile(db, data, logger)

            # Migrar summaries
            migrate_summaries(db, data, profile, logger)

            # Migrar projetos
            migrate_projects(db, data, logger)

            # Commit de todas as mudanças
            logger.log("\nSalvando alterações no banco...")
            db.commit()
            logger.log("✅ Commit realizado com sucesso")

            # Validar migração
            validation_passed = validate_migration(db, data, logger)

            if validation_passed:
                logger.log("\n" + "=" * 60)
                logger.log("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
                logger.log("=" * 60)
                logger.log(f"\nPróximos passos:")
                logger.log(
                    f"1. O arquivo original foi preservado em: {JSON_BACKUP_PATH}"
                )
                logger.log(f"2. Novo banco SQLite criado")
                logger.log(f"3. Execute 'streamlit run src/app.py' para testar")
            else:
                db.rollback()
                logger.log(
                    "\n❌ Migração CANCELADA devido a erros de validação", "ERROR"
                )
                sys.exit(1)

        except Exception as e:
            db.rollback()
            logger.log(f"\n❌ ERRO durante migração: {str(e)}", "ERROR")
            import traceback

            logger.log(traceback.format_exc(), "ERROR")
            sys.exit(1)

        finally:
            db.close()

    finally:
        # Salvar log
        logger.save()


if __name__ == "__main__":
    main()
