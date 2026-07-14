from typing import TypedDict
import re

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agent.tools import (
    analyze_hcp_sentiment_tool,
    edit_interaction_tool,
    log_interaction_tool,
    recommend_materials_tool,
    suggest_follow_up_tool,
)
from app.services.llm import LLMService


class AgentState(TypedDict):
    message: str
    tool: str
    data: dict
    response: str


def _extract_id(message: str) -> int | None:
    explicit = re.search(r"(?:interaction|id|#)\s*#?(\d+)", message, re.IGNORECASE)
    if explicit:
        return int(explicit.group(1))
    return None


def _route(state: AgentState) -> str:
    text = state["message"].lower()
    if (
        text.startswith(("edit", "change", "set", "update"))
        or " edit " in f" {text} "
        or "update interaction" in text
        or "change the interaction" in text
        or "interaction type" in text
    ):
        return "edit_interaction"
    if text.startswith("log") or " log " in f" {text} " or "met dr" in text or "meeting with" in text:
        return "log_interaction"
    if "follow" in text or "next best" in text:
        return "suggest_follow_up"
    if "recommend" in text or "material" in text or "brochure" in text:
        return "recommend_materials"
    if "sentiment" in text or "tone" in text or "concern" in text:
        return "analyze_hcp_sentiment"
    return "log_interaction"


def run_agent(db: Session, message: str) -> AgentState:
    llm = LLMService()

    def classify(state: AgentState) -> AgentState:
        state["tool"] = _route(state)
        return state

    def log_node(state: AgentState) -> AgentState:
        state["data"] = log_interaction_tool(db, llm, state["message"])
        state["response"] = f"Logged interaction for {state['data'].get('hcp_name', 'the HCP')}."
        return state

    def edit_node(state: AgentState) -> AgentState:
        state["data"] = edit_interaction_tool(db, _extract_id(state["message"]), state["message"])
        state["response"] = "Updated the interaction." if "error" not in state["data"] else state["data"]["error"]
        return state

    def follow_node(state: AgentState) -> AgentState:
        state["data"] = suggest_follow_up_tool(db, llm, _extract_id(state["message"]) or 1)
        state["response"] = (
            "Generated follow-up recommendations."
            if "error" not in state["data"]
            else state["data"]["error"]
        )
        return state

    def materials_node(state: AgentState) -> AgentState:
        state["data"] = recommend_materials_tool(llm, state["message"])
        state["response"] = "Recommended approved materials for this HCP context."
        return state

    def sentiment_node(state: AgentState) -> AgentState:
        state["data"] = analyze_hcp_sentiment_tool(llm, state["message"])
        state["response"] = f"Detected {state['data']['sentiment']} sentiment."
        return state

    graph = StateGraph(AgentState)
    graph.add_node("classify", classify)
    graph.add_node("log_interaction", log_node)
    graph.add_node("edit_interaction", edit_node)
    graph.add_node("suggest_follow_up", follow_node)
    graph.add_node("recommend_materials", materials_node)
    graph.add_node("analyze_hcp_sentiment", sentiment_node)
    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        lambda state: state["tool"],
        {
            "log_interaction": "log_interaction",
            "edit_interaction": "edit_interaction",
            "suggest_follow_up": "suggest_follow_up",
            "recommend_materials": "recommend_materials",
            "analyze_hcp_sentiment": "analyze_hcp_sentiment",
        },
    )
    for node in [
        "log_interaction",
        "edit_interaction",
        "suggest_follow_up",
        "recommend_materials",
        "analyze_hcp_sentiment",
    ]:
        graph.add_edge(node, END)

    app = graph.compile()
    return app.invoke({"message": message, "tool": "", "data": {}, "response": ""})
