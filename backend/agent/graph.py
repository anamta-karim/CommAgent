import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from . import nodes

class AgentState(TypedDict):
    chat_id: str
    question: str
    chunks: list[str]
    draft_answer: str
    confident: bool
    trace: list[dict]

def _logged(name, fn):
    def wrapped(state):
        state = fn(state)
        outputs = {
            "retrieve": lambda: state["chunks"],
            "draft": lambda: state["draft_answer"],
            "critique": lambda: {"confident": state["confident"]},
            "decide": lambda: "replied" if state["confident"] else "escalated",
        }
        state.setdefault("trace", []).append({
            "node": name, "timestamp": time.time(), "output": outputs[name]()
        })
        return state
    return wrapped

graph = StateGraph(AgentState)
for name in ("retrieve", "draft", "critique", "decide"):
    graph.add_node(name, _logged(name, getattr(nodes, name)))
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "draft")
graph.add_edge("draft", "critique")
graph.add_edge("critique", "decide")
graph.add_edge("decide", END)

compiled_graph = graph.compile()