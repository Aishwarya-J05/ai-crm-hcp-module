from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.graph import run_agent
from app.db.session import get_db
from app.schemas.interaction import AgentResponse, ChatRequest, InteractionCreate, InteractionRead, InteractionUpdate
from app.services.interactions import create_interaction, list_interactions, update_interaction

router = APIRouter(prefix="/api", tags=["HCP interactions"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/interactions", response_model=list[InteractionRead])
def get_interactions(db: Session = Depends(get_db)) -> list[InteractionRead]:
    return list_interactions(db)


@router.post("/interactions", response_model=InteractionRead)
def post_interaction(payload: InteractionCreate, db: Session = Depends(get_db)) -> InteractionRead:
    return create_interaction(db, payload)


@router.patch("/interactions/{interaction_id}", response_model=InteractionRead)
def patch_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
) -> InteractionRead:
    interaction = update_interaction(db, interaction_id, payload)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.post("/agent/chat", response_model=AgentResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> AgentResponse:
    result = run_agent(db, payload.message)
    return AgentResponse(tool=result["tool"], message=result["response"], data=result["data"])
