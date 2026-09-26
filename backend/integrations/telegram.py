from swytchcode_runtime import exec as swx

def send_message(chat_id: str, text: str) -> dict:
    return swx("telegram_v5_0.sendmessage.create", {
        "body": {"chat_id": chat_id, "text": text}
    })