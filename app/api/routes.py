"""
API Routes for Manus Agent System
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime

from app.db.database import get_db
from app.models.models import Project, Article, Task
from app.agents.orchestrator import OrchestratorAgent
from app.services.llm_service import LLMService

router = APIRouter()

# ── Request / Response Models ─────────────────────────────────────────────────

class TaskRequest(BaseModel):
    task: str
    project_id: Optional[int] = None
    context: Optional[dict] = None

    @field_validator("context", mode="before")
    @classmethod
    def default_context(cls, v):
        return v or {}


class TaskResponse(BaseModel):
    task_id: int
    status: str
    result: dict


class ProjectCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None


class ArticleCreate(BaseModel):
    project_id: Optional[int] = None
    title: str
    content: str
    category: Optional[str] = None


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_llm_service(request: Request = None) -> LLMService:
    """Safely get LLM service from app state or create a new one"""
    if request and hasattr(request.app.state, "llm_service"):
        return request.app.state.llm_service
    return LLMService()


# ── Orchestrator endpoint ─────────────────────────────────────────────────────

@router.post("/agent/execute", response_model=None)
async def execute_agent_task(
    request: TaskRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Execute a task using the orchestrator agent"""
    task_record = None
    try:
        llm_service = _get_llm_service(http_request)
        orchestrator = OrchestratorAgent(llm_service)
        task_record = Task(
            project_id=request.project_id,
            task_type="agent_task",
            description=request.task,
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(task_record)
        db.commit()
        db.refresh(task_record)

        result = await orchestrator.run(
            task=request.task,
            project_context=request.context,
        )

        task_record.status = "completed" if "error" not in result else "failed"
        task_record.result_data = result
        task_record.completed_at = datetime.utcnow()
        if "error" in result:
            task_record.error_message = result["error"]
        db.commit()

        return TaskResponse(
            task_id=task_record.id,
            status=task_record.status,
            result=result,
        )
    except Exception as e:
        if task_record is not None:
            task_record.status = "failed"
            task_record.error_message = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ── Project endpoints ─────────────────────────────────────────────────────────

@router.post("/projects", status_code=201)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"id": db_project.id, "name": db_project.name, "domain": db_project.domain}


@router.get("/projects")
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all projects"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return [{"id": p.id, "name": p.name, "domain": p.domain, "is_active": p.is_active} for p in projects]


@router.get("/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": project.id, "name": project.name, "domain": project.domain}


# ── Article endpoints ─────────────────────────────────────────────────────────

@router.post("/articles", status_code=201)
async def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article"""
    db_article = Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return {"id": db_article.id, "title": db_article.title, "status": db_article.status}


@router.get("/articles")
async def list_articles(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List articles"""
    query = db.query(Article)
    if project_id:
        query = query.filter(Article.project_id == project_id)
    articles = query.offset(skip).limit(limit).all()
    return [{"id": a.id, "title": a.title, "category": a.category, "status": a.status} for a in articles]


@router.get("/articles/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"id": article.id, "title": article.title, "content": article.content}


# ── Task endpoints ────────────────────────────────────────────────────────────

@router.get("/tasks")
async def list_tasks(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List tasks"""
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return [{"id": t.id, "task_type": t.task_type, "status": t.status, "created_at": str(t.created_at)} for t in tasks]


@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task.id, "task_type": task.task_type, "status": task.status, "result_data": task.result_data}


# ── News endpoint ─────────────────────────────────────────────────────────────

@router.post("/news/fetch")
async def fetch_news(
    category: str = "technology",
    keywords: Optional[str] = None,
    limit: int = 10,
):
    """Fetch news articles"""
    from app.tools.news_fetch import NewsFetchTool
    news_tool = NewsFetchTool()
    result = await news_tool.safe_execute(
        category=category,
        keywords=keywords or "",
        limit=limit,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


# ── Content generation endpoint ───────────────────────────────────────────────

@router.post("/content/generate")
async def generate_content(
    topic: str,
    content_type: str = "article",
    keywords: Optional[List[str]] = None,
    http_request: Request = None,
    db: Session = Depends(get_db),
):
    """Generate content"""
    llm_service = _get_llm_service(http_request)
    from app.agents.content_agent import ContentAgent
    content_agent = ContentAgent(llm_service)
    context = {
        "topic": topic,
        "keywords": keywords or [],
        "style": "news" if content_type == "article" else "blog",
    }
    result = await content_agent.execute(
        task=f"Generate {content_type} about {topic}",
        context=context,
    )
    return result
