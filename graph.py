from langgraph.graph import StateGraph, END

from state import TutorState
from nodes_m1 import select_checkpoint, explain_topic
from nodes_m2 import generate_questions, ask_questions, verify_answers
from nodes_m3 import feynman_teach


graph = StateGraph(TutorState)

graph.add_node("select_checkpoint", select_checkpoint)
graph.add_node("explain_topic", explain_topic)
graph.add_node("generate_questions", generate_questions)
graph.add_node("ask_questions", ask_questions)
graph.add_node("verify_answers", verify_answers)
graph.add_node("feynman_teach", feynman_teach)

graph.set_entry_point("select_checkpoint")

graph.add_edge("select_checkpoint", "explain_topic")
graph.add_edge("explain_topic", "generate_questions")
graph.add_edge("generate_questions", "ask_questions")
graph.add_edge("ask_questions", "verify_answers")


def score_router(state: TutorState):
    if state.get("score", 0) >= state["checkpoint"]["success_threshold"]:
        return "end"
    return "retry"


graph.add_conditional_edges(
    "verify_answers",
    score_router,
    {"retry": "feynman_teach", "end": END},
)

graph.add_edge("feynman_teach", "generate_questions")

app = graph.compile()
