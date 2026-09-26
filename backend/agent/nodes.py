from langchain_google_genai import ChatGoogleGenerativeAI
from . import kb
from integrations import telegram, notion, resend

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

def _text(content) -> str:
    """Gemini sometimes returns content as a list of parts instead of a plain string."""
    if isinstance(content, list):
        return "".join(part if isinstance(part, str) else part.get("text", "") for part in content)
    return content

def retrieve(state: dict) -> dict:
    state["chunks"] = kb.query(state["question"])
    return state

def draft(state: dict) -> dict:
    ctx = "\n\n".join(state["chunks"])
    resp = llm.invoke(f"KB:\n{ctx}\n\nAnswer using ONLY the KB above:\n{state['question']}")
    state["draft_answer"] = _text(resp.content)
    return state

def critique(state: dict) -> dict:
    ctx = "\n\n".join(state["chunks"])
    resp = llm.invoke(
        f"KB:\n{ctx}\n\nDraft:\n{state['draft_answer']}\n\n"
        "Fully supported by the KB, no invented facts? Reply YES or NO only."
    )
    verdict = _text(resp.content)
    state["confident"] = verdict.strip().upper().startswith("Y")
    return state

def decide(state: dict) -> dict:
    if state["confident"]:
        telegram.send_message(state["chat_id"], state["draft_answer"])
    else:
        notion.create_escalation_page(state["question"], "Low self-critique confidence")
        resend.notify_moderator(state["question"], state["chat_id"])
        telegram.send_message(state["chat_id"], "Good question — looping in a human, hang tight!")
    return state