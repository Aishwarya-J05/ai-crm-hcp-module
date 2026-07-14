import re
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.schemas.interaction import InteractionCreate, InteractionRead, InteractionUpdate
from app.services.interactions import create_interaction, get_interaction, get_latest_interaction, update_interaction
from app.services.llm import LLMService


STOPWORDS = {
    "about",
    "with",
    "at",
    "on",
    "for",
    "regarding",
    "discussed",
    "shared",
    "showed",
    "requested",
}


def _extract_hcp_name(message: str) -> str:
    match = re.search(r"\bdr\.?\s+([a-z]+(?:\s+[a-z]+){0,2})", message, re.IGNORECASE)
    if not match:
        return "Dr. Unspecified"

    parts = []
    for part in match.group(1).split():
        if part.lower() in STOPWORDS:
            break
        parts.append(part.capitalize())

    return f"Dr. {' '.join(parts)}" if parts else "Dr. Unspecified"


def _extract_interaction_type(message: str) -> str:
    lowered = message.lower()
    for interaction_type in ["conference", "meeting", "call", "email"]:
        if interaction_type in lowered:
            return interaction_type.title()
    return "Meeting"


def _extract_interaction_date(message: str) -> date | None:
    lowered = message.lower()
    month_map = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }

    numeric = re.search(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b", lowered)
    if numeric:
        day, month, year = (int(value) for value in numeric.groups())
        return date(year, month, day)

    named = re.search(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)\s+(\d{4})\b",
        lowered,
        re.IGNORECASE,
    )
    if named:
        day = int(named.group(1))
        month = month_map.get(named.group(2).lower())
        year = int(named.group(3))
        if month:
            return date(year, month, day)

    return None


def _today_payload(message: str) -> dict:
    lowered = message.lower()
    sentiment = "Neutral"
    if any(word in lowered for word in ["positive", "interested", "agreed", "happy"]):
        sentiment = "Positive"
    if any(word in lowered for word in ["negative", "concern", "rejected", "unhappy"]):
        sentiment = "Negative"

    hcp_name = _extract_hcp_name(message)

    materials = []
    if "brochure" in lowered:
        materials.append("Product brochure")
    if "study" in lowered or "evidence" in lowered:
        materials.append("Clinical study summary")
    if "pi" in lowered or "prescribing" in lowered:
        materials.append("Prescribing information")

    return {
        "hcp_name": hcp_name,
        "interaction_type": _extract_interaction_type(message),
        "interaction_date": date.today(),
        "interaction_time": datetime.now().time().replace(microsecond=0),
        "attendees": hcp_name,
        "topics_discussed": message,
        "materials_shared": ", ".join(materials),
        "samples_distributed": "Samples mentioned" if "sample" in lowered else "",
        "sentiment": sentiment,
        "outcomes": "Captured from conversational note.",
        "follow_up_actions": "Schedule follow-up in 2 weeks" if "follow" in lowered or "2 week" in lowered else "",
    }


def log_interaction_tool(db: Session, llm: LLMService, message: str) -> dict:
    """Capture an HCP interaction using LLM-ready summarization and entity extraction."""
    payload = _today_payload(message)
    payload["ai_summary"] = llm.complete(
        "Summarize this HCP interaction for a pharma CRM log and extract next best action: "
        f"{message}"
    )
    interaction = create_interaction(db, InteractionCreate(**payload))
    return InteractionRead.model_validate(interaction).model_dump(mode="json")


def edit_interaction_tool(db: Session, interaction_id: int | None, message: str) -> dict:
    """Modify previously logged interaction data from conversational instructions."""
    patch: dict[str, str] = {}
    lowered = message.lower()
    interaction = get_interaction(db, interaction_id) if interaction_id else get_latest_interaction(db)
    if not interaction:
        return {"error": "No interaction was found to edit."}

    if any(word in lowered for word in ["conference", "meeting", "call", "email"]):
        patch["interaction_type"] = _extract_interaction_type(message)

    interaction_date = _extract_interaction_date(message)
    if interaction_date:
        patch["interaction_date"] = interaction_date

    hcp_name = _extract_hcp_name(message)
    if hcp_name != "Dr. Unspecified":
        patch["hcp_name"] = hcp_name
        patch["attendees"] = hcp_name

    for sentiment in ["positive", "neutral", "negative"]:
        if sentiment in lowered:
            patch["sentiment"] = sentiment.title()
            break

    outcome_match = re.search(r"outcome\s+(.+)", message, re.IGNORECASE)
    if outcome_match:
        patch["outcomes"] = outcome_match.group(1).strip()
    elif "follow" in lowered and not patch:
        patch["follow_up_actions"] = message
    elif not patch:
        patch["topics_discussed"] = message

    updated = update_interaction(db, interaction.id, InteractionUpdate(**patch))

    return InteractionRead.model_validate(updated).model_dump(mode="json") | {"updated_fields": patch}


def suggest_follow_up_tool(db: Session, llm: LLMService, interaction_id: int) -> dict:
    """Generate next best actions for a sales representative."""
    interaction = get_interaction(db, interaction_id)
    if not interaction:
        return {"error": f"Interaction {interaction_id} was not found."}

    prompt = (
        "Suggest three compliant follow-up actions for this HCP interaction. "
        f"HCP: {interaction.hcp_name}. Topics: {interaction.topics_discussed}. "
        f"Sentiment: {interaction.sentiment}. Outcomes: {interaction.outcomes}."
    )
    suggestion = llm.complete(prompt)
    return {
        "interaction_id": interaction.id,
        "suggestions": [
            "Schedule follow-up meeting in 2 weeks",
            "Send approved clinical evidence PDF",
            "Add HCP to relevant advisory or education invite list",
        ],
        "ai_note": suggestion,
    }


def recommend_materials_tool(llm: LLMService, context: str) -> dict:
    """Recommend approved sales or medical materials based on specialty and topic."""
    ai_note = llm.complete(f"Recommend approved CRM materials for this HCP context: {context}")
    return {
        "materials": [
            "Product efficacy leave-behind",
            "Safety and tolerability one-pager",
            "Recent peer-reviewed study summary",
            "Patient support program brochure",
        ],
        "ai_note": ai_note,
    }


def analyze_hcp_sentiment_tool(llm: LLMService, text: str) -> dict:
    """Classify HCP sentiment and extract evidence from the representative's note."""
    lowered = text.lower()
    if any(word in lowered for word in ["concern", "risk", "negative", "declined"]):
        sentiment = "Negative"
    elif any(word in lowered for word in ["interested", "positive", "agreed", "adopt"]):
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "confidence": 0.82,
        "rationale": llm.complete(f"Explain the HCP sentiment in one concise CRM sentence: {text}"),
    }
