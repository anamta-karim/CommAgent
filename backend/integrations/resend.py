from swytchcode_runtime import exec as swx

def notify_moderator(question: str, chat_id: str) -> dict:
    return swx("resend.email.create", {
        "to": "moderator@example.com",
        "subject": "CommAgent escalation",
        "text": f"Chat {chat_id} asked:\n{question}\n\nNo confident KB answer found.",
    })