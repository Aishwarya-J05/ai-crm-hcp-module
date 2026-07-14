from sqlalchemy.orm import Session

from app.models.interaction import HCPInteraction
from app.schemas.interaction import InteractionCreate, InteractionUpdate


def list_interactions(db: Session) -> list[HCPInteraction]:
    return db.query(HCPInteraction).order_by(HCPInteraction.created_at.desc()).all()


def get_interaction(db: Session, interaction_id: int) -> HCPInteraction | None:
    return db.get(HCPInteraction, interaction_id)


def get_latest_interaction(db: Session) -> HCPInteraction | None:
    return db.query(HCPInteraction).order_by(HCPInteraction.created_at.desc()).first()


def create_interaction(db: Session, payload: InteractionCreate) -> HCPInteraction:
    interaction = HCPInteraction(**payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def update_interaction(db: Session, interaction_id: int, payload: InteractionUpdate) -> HCPInteraction | None:
    interaction = get_interaction(db, interaction_id)
    if not interaction:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction
