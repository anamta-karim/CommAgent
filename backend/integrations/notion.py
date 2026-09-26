from swytchcode_runtime import exec as swx

def create_escalation_page(question: str, reason: str) -> dict:
    return swx("notion.page.create", {
        "title": question,
        "content": f"**Unanswered in Telegram**\n\nReason: {reason}",
    })