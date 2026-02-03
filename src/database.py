"""
Módulo de Banco de Dados - Nexus AI Recruiter

Este módulo gerencia toda a camada de persistência usando SQLite e SQLAlchemy ORM.
Responsável por armazenar perfil, projetos, skills e histórico de currículos gerados.

Autor: Alessandro Lima
"""

import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Configurações de Caminho
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "curriculo.db")
DB_URL = f"sqlite:///{DB_PATH}"

# Engine com configurações otimizadas para SQLite
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},  # Permite uso multi-thread
    poolclass=StaticPool,  # Pool estático para SQLite
    echo=False,  # Defina True para debug de queries
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os Modelos ORM
Base = declarative_base()


# ==================== MODELOS ORM ====================


class Profile(Base):
    """
    Tabela de Perfil do Usuário.
    Armazena informações básicas de contato e identificação.
    """

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    linkedin = Column(String(200))
    github = Column(String(200))
    location = Column(String(200))

    # Relacionamentos
    education = relationship(
        "Education", back_populates="profile", cascade="all, delete-orphan"
    )
    summaries = relationship(
        "Summary", back_populates="profile", cascade="all, delete-orphan"
    )
    hard_skills = relationship(
        "HardSkill", back_populates="profile", cascade="all, delete-orphan"
    )
    languages = relationship(
        "Language", back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Profile(name='{self.name}', email='{self.email}')>"


class Education(Base):
    """
    Tabela de Educação/Formação Acadêmica.
    """

    __tablename__ = "education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    degree = Column(String(200), nullable=False)
    institution = Column(String(200), nullable=False)
    period = Column(String(100))

    # Relacionamento
    profile = relationship("Profile", back_populates="education")

    def __repr__(self):
        return f"<Education(degree='{self.degree}', institution='{self.institution}')>"


class Summary(Base):
    """
    Tabela de Resumos Profissionais.
    Armazena diferentes versões de resumo (frontend, backend, fullstack, etc).
    """

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    key = Column(String(50), nullable=False, unique=True)  # Ex: 'frontend', 'backend'
    text = Column(Text, nullable=False)

    # Relacionamento
    profile = relationship("Profile", back_populates="summaries")

    def __repr__(self):
        return f"<Summary(key='{self.key}')>"


class Project(Base):
    """
    Tabela de Projetos do Portfólio.
    """

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        String(100), nullable=False, unique=True
    )  # ID único do projeto (ex: 'nexus_ai_recruiter')
    title = Column(String(200), nullable=False)
    type = Column(String(100))  # Ex: 'Frontend', 'Backend', 'Fullstack'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    tech_stack = relationship(
        "TechStack", back_populates="project", cascade="all, delete-orphan"
    )
    descriptions = relationship(
        "ProjectDescription", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id='{self.project_id}', title='{self.title}')>"


class TechStack(Base):
    """
    Tabela de Tecnologias utilizadas em cada Projeto.
    Relação N:N entre Projetos e Tecnologias.
    """

    __tablename__ = "tech_stack"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    technology = Column(String(100), nullable=False)

    # Relacionamento
    project = relationship("Project", back_populates="tech_stack")

    def __repr__(self):
        return f"<TechStack(technology='{self.technology}')>"


class ProjectDescription(Base):
    """
    Tabela de Descrições dos Projetos.
    Cada projeto pode ter múltiplas descrições focadas em diferentes áreas.
    """

    __tablename__ = "project_descriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    focus = Column(
        String(50), nullable=False
    )  # Ex: 'frontend', 'backend', 'ai_engineering'
    text = Column(Text, nullable=False)

    # Relacionamento
    project = relationship("Project", back_populates="descriptions")

    def __repr__(self):
        return f"<ProjectDescription(focus='{self.focus}')>"


class HardSkill(Base):
    """
    Tabela de Habilidades Técnicas (Hard Skills).
    """

    __tablename__ = "hard_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(100))  # Ex: 'Frontend', 'Backend', 'Database', 'Tools'

    # Relacionamento
    profile = relationship("Profile", back_populates="hard_skills")

    def __repr__(self):
        return f"<HardSkill(skill='{self.skill_name}')>"


class Language(Base):
    """
    Tabela de Idiomas.
    """

    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    language = Column(String(100), nullable=False)

    # Relacionamento
    profile = relationship("Profile", back_populates="languages")

    def __repr__(self):
        return f"<Language(language='{self.language}')>"


# ==================== FUNÇÕES HELPER ====================


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas.
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Banco de dados inicializado em: {DB_PATH}")


def get_db() -> Session:
    """
    Generator para obter sessão do banco de dados.
    Uso recomendado com context manager.

    Exemplo:
        with get_db() as db:
            profile = db.query(Profile).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_profile_data(db: Session) -> Dict[str, Any]:
    """
    Retorna todos os dados do perfil em formato de dicionário (compatível com JSON antigo).

    Args:
        db: Sessão do SQLAlchemy

    Returns:
        Dicionário com estrutura similar ao master_data.json
    """
    profile = db.query(Profile).first()

    if not profile:
        raise ValueError("Nenhum perfil encontrado no banco de dados")

    # Monta estrutura compatível com o formato antigo
    data = {
        "profile": {
            "name": profile.name,
            "contact": {
                "email": profile.email,
                "phone": profile.phone,
                "linkedin": profile.linkedin,
                "github": profile.github,
                "location": profile.location,
            },
            "education": [
                {
                    "degree": edu.degree,
                    "institution": edu.institution,
                    "period": edu.period,
                }
                for edu in profile.education
            ],
            "languages": [lang.language for lang in profile.languages],
            "hard_skills": [skill.skill_name for skill in profile.hard_skills],
        },
        "summaries": {summary.key: summary.text for summary in profile.summaries},
        "projects": [],
    }

    # Busca todos os projetos
    projects = db.query(Project).all()

    for project in projects:
        data["projects"].append(
            {
                "id": project.project_id,
                "title": project.title,
                "tech_stack": [tech.technology for tech in project.tech_stack],
                "type": project.type,
                "descriptions": [
                    {"focus": desc.focus, "text": desc.text}
                    for desc in project.descriptions
                ],
            }
        )

    return data


def get_projects_by_ids(db: Session, project_ids: List[str]) -> List[Project]:
    """
    Busca projetos específicos por seus IDs.

    Args:
        db: Sessão do SQLAlchemy
        project_ids: Lista de IDs de projetos

    Returns:
        Lista de objetos Project
    """
    return db.query(Project).filter(Project.project_id.in_(project_ids)).all()


def get_all_skills(db: Session) -> List[str]:
    """
    Retorna todas as hard skills cadastradas.

    Args:
        db: Sessão do SQLAlchemy

    Returns:
        Lista de strings com nomes das skills
    """
    skills = db.query(HardSkill).all()
    return [skill.skill_name for skill in skills]


def get_db_stats() -> Dict[str, int]:
    """
    Retorna estatísticas gerais do banco de dados.

    Returns:
        Dicionário com contadores de registros
    """
    with SessionLocal() as db:
        return {
            "total_projects": db.query(Project).count(),
            "total_skills": db.query(HardSkill).count(),
            "total_summaries": db.query(Summary).count(),
        }


if __name__ == "__main__":
    # Inicializa o banco quando executado diretamente
    init_db()
    print("🎯 Estrutura do banco de dados criada com sucesso!")
