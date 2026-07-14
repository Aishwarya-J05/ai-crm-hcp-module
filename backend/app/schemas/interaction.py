from datetime import date, datetime, time

from pydantic import BaseModel, Field


class InteractionBase(BaseModel):
    hcp_name: str = Field(min_length=1, max_length=160)
    interaction_type: str = "Meeting"
    interaction_date: date
    interaction_time: time
    attendees: str = ""
    topics_discussed: str = ""
    materials_shared: str = ""
    samples_distributed: str = ""
    sentiment: str = "Neutral"
    outcomes: str = ""
    follow_up_actions: str = ""
    ai_summary: str = ""


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    hcp_name: str | None = None
    interaction_type: str | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    attendees: str | None = None
    topics_discussed: str | None = None
    materials_shared: str | None = None
    samples_distributed: str | None = None
    sentiment: str | None = None
    outcomes: str | None = None
    follow_up_actions: str | None = None
    ai_summary: str | None = None


class InteractionRead(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    tool: str
    message: str
    data: dict
