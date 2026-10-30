from langgraph.graph import (
    END,
    StateGraph,
)

from agents.dispatcher import dispatch_tool
from agents.router import route_question
from agents.state import ClaimsAgentState
from agents.synthesizer import synthesize_answer
from agents.planner import plan_question
from agents.hybrid_synthesizer import synthesize_hybrid_answer
from tools.knowledge import knowledge_search
from core.models import ToolName, ToolRoute


def route_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Route the user question and determine whether the
    request requires structured analytics or knowledge
    retrieval.
    """

    route = route_question(
        state["question"]
    )

    mode = (
        "knowledge"
        if route.tool == ToolName.KNOWLEDGE_SEARCH
        else "analytics"
    )

    return {
        "route": route,
        "mode": mode,
    }

def execute_tool_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Execute the validated tool selected by the router.
    """

    result = dispatch_tool(
        state["route"]
    )

    sources = []

    for item in result.get(
        "results",
        []
    ):
        source = item.get("source")

        if source and source not in sources:
            sources.append(source)

    return {
        "tool_result": result,
        "sources": sources,
    }

def synthesize_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Generate the final grounded analyst-facing response.
    """

    answer = synthesize_answer(
        question=state["question"],
        route=state["route"],
        tool_result=state["tool_result"],
    )

    return {
        "answer": answer,
    }

def plan_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Determine whether the request requires analytics,
    knowledge retrieval, or both.
    """

    plan = plan_question(
        state["question"]
    )

    return {
        "plan": plan,
        "mode": plan.mode.value,
        "knowledge_query": (
            plan.knowledge_query
        ),
    }

def select_mode(
    state: ClaimsAgentState,
) -> str:
    """
    Select the workflow path produced by the planner.
    """

    return state["mode"]

def route_analytics_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Route the analytical component to a validated
    deterministic analytical tool.
    """

    plan = state["plan"]

    analytical_question = (
        plan.analytical_question
        or state["question"]
    )

    route = route_question(
        analytical_question
    )

    return {
        "analytical_route": route,
    }

def execute_analytics_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Execute the structured analytical route.
    """

    result = dispatch_tool(
        state["analytical_route"]
    )

    return {
        "analytical_result": result,
    }


def retrieve_knowledge_node(
    state: ClaimsAgentState,
) -> dict:
    """
    Retrieve methodology or documentation evidence.
    """

    query = (
        state["knowledge_query"]
        or state["question"]
    )

    result = knowledge_search(
        query=query,
        k=3,
    )

    sources = []

    for item in result["results"]:
        source = item.get("source")

        if (
            source
            and source not in sources
        ):
            sources.append(source)

    return {
        "knowledge_result": result,
        "sources": sources,
    }

def synthesize_analytics_node(
    state: ClaimsAgentState,
) -> dict:

    answer = synthesize_answer(
        question=state["question"],
        route=state["analytical_route"],
        tool_result=state["analytical_result"],
    )

    return {
        "answer": answer,
    }


def synthesize_knowledge_node(
    state: ClaimsAgentState,
) -> dict:

    route = ToolRoute(
        tool=ToolName.KNOWLEDGE_SEARCH,
        arguments={
            "query": (
                state["knowledge_query"]
                or state["question"]
            )
        },
    )

    answer = synthesize_answer(
        question=state["question"],
        route=route,
        tool_result=state["knowledge_result"],
    )

    return {
        "answer": answer,
    }

def synthesize_hybrid_node(
    state: ClaimsAgentState,
) -> dict:

    answer = synthesize_hybrid_answer(
        question=state["question"],
        analytical_result=state[
            "analytical_result"
        ],
        knowledge_result=state[
            "knowledge_result"
        ],
    )

    return {
        "answer": answer,
    }

def after_analytics(
    state: ClaimsAgentState,
) -> str:

    if state["mode"] == "hybrid":
        return "retrieve_knowledge"

    return "synthesize_analytics"

def after_knowledge(
    state: ClaimsAgentState,
) -> str:

    if state["mode"] == "hybrid":
        return "synthesize_hybrid"

    return "synthesize_knowledge"


def build_claims_graph():

    graph = StateGraph(
        ClaimsAgentState
    )

    graph.add_node(
        "plan",
        plan_node,
    )

    graph.add_node(
        "route_analytics",
        route_analytics_node,
    )

    graph.add_node(
        "execute_analytics",
        execute_analytics_node,
    )

    graph.add_node(
        "retrieve_knowledge",
        retrieve_knowledge_node,
    )

    graph.add_node(
        "synthesize_analytics",
        synthesize_analytics_node,
    )

    graph.add_node(
        "synthesize_knowledge",
        synthesize_knowledge_node,
    )

    graph.add_node(
        "synthesize_hybrid",
        synthesize_hybrid_node,
    )

    graph.set_entry_point(
        "plan"
    )

    graph.add_conditional_edges(
        "plan",
        select_mode,
        {
            "analytics": "route_analytics",
            "knowledge": "retrieve_knowledge",
            "hybrid": "route_analytics",
        },
    )

    graph.add_edge(
        "route_analytics",
        "execute_analytics",
    )

    graph.add_conditional_edges(
        "execute_analytics",
        after_analytics,
        {
            "retrieve_knowledge": (
                "retrieve_knowledge"
            ),
            "synthesize_analytics": (
                "synthesize_analytics"
            ),
        },
    )

    graph.add_conditional_edges(
        "retrieve_knowledge",
        after_knowledge,
        {
            "synthesize_hybrid": (
                "synthesize_hybrid"
            ),
            "synthesize_knowledge": (
                "synthesize_knowledge"
            ),
        },
    )

    graph.add_edge(
        "synthesize_analytics",
        END,
    )

    graph.add_edge(
        "synthesize_knowledge",
        END,
    )

    graph.add_edge(
        "synthesize_hybrid",
        END,
    )

    return graph.compile()



claims_graph = build_claims_graph()


def run_claims_graph(
    question: str,
) -> dict:

    if not question.strip():
        raise ValueError(
            "question cannot be empty."
        )

    initial_state: ClaimsAgentState = {
        "question": question,
        "plan": None,
        "mode": None,

        "analytical_route": None,
        "analytical_result": None,

        "knowledge_query": None,
        "knowledge_result": None,

        "answer": None,
        "sources": [],
    }

    return claims_graph.invoke(
        initial_state
    )

from agents.reporting import (
    build_agent_response,
)


def ask_claims_agent(
    question: str,
):
    """
    Public application interface for the Medicare
    Claims Intelligence Agent.
    """

    state = run_claims_graph(
        question
    )

    return build_agent_response(
        state
    )