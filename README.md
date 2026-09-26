# CommAgent

A Telegram bot for community FAQ support that knows when to stop guessing and ask a human instead.

Built for Track 3 (AI Community Agent) at Build with Swytchcode, Gurgaon.

## The idea

Most community bots retrieve an answer and post it, even when they're wrong. CommAgent adds a self-check step in the middle: after drafting an answer from the knowledge base, it reviews its own response and checks whether it's actually backed by the source material. If it's confident, it replies right away. If not, it escalates instead of hallucinating: it logs the question in Notion, alerts a moderator by email, and tells the user a real person is on it.

The demo persona is a Women in Tech mentorship community, but the pattern applies to any group that fields repetitive questions and doesn't want a bot quietly making things up when it doesn't actually know the answer.

## How it works

```
Telegram message
      |
FastAPI webhook
      |
LangGraph agent:
  1. retrieve   -> vector search over the knowledge base (Chroma)
  2. draft      -> LLM answers using only the retrieved context
  3. critique   -> LLM checks its own draft against that context
  4. decide     -> confident: reply directly on Telegram
               -> not confident: log to Notion, alert on Resend,
                  tell the user a human will follow up
```

Every step is logged so the reasoning trail can be inspected, not just the final answer.

## Tech stack

- **Backend:** FastAPI
- **Agent:** LangGraph (explicit state graph, not a prebuilt agent)
- **LLM:** Gemini, via `langchain-google-genai`
- **Retrieval:** Chroma, indexed from local markdown KB files at startup
- **Integrations:** Telegram (delivery), Notion (escalation logging), Resend (moderator alerts) — via Swytchcode

## Repo structure

```
backend/
  main.py              FastAPI app + Telegram webhook route
  agent/
    graph.py            LangGraph graph definition
    nodes.py             retrieve, draft, critique, decide
    kb.py                KB loading + Chroma index/query
  integrations/
    telegram.py
    notion.py
    resend.py
docs/
  kb_seed/               knowledge base source files
```

## Knowledge base

The bot answers only from `docs/kb_seed/`, covering:
- Program logistics and FAQs
- Community guidelines and eligibility
- Setup and common technical issues
- Known issues and their status

Anything outside this scope triggers escalation rather than a guess.

## Running it locally

1. Set up environment variables (`.env`, see `.env.example`):
   - Telegram bot token
   - Notion / Resend credentials (via Swytchcode)
2. Start the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
3. Expose it publicly (for local demo purposes):
   ```bash
   ngrok http 8000
   ```
4. Register the Telegram webhook with the resulting URL:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<NGROK_URL>/telegram/webhook"
   ```
5. Message the bot on Telegram.

## What's demoed

- **Confident path:** a question the KB actually covers gets answered directly.
- **Escalation path:** a question outside the KB (e.g. asking about visa sponsorship, which the program doesn't cover) gets caught by the self-critique step, logged to Notion, and flagged to a moderator, while the user gets an honest "looping in a human" reply instead of a made-up answer.

## Notes on the self-critique step

This is the actual differentiator of the project: the draft and critique are two distinct LLM calls, kept deliberately separate so the agent is checking its own work rather than just answering once and moving on. It isn't perfect (a hedged, honest "I don't know" from the model can occasionally slip past the critique check), so there's a lightweight keyword safety net on top that catches those cases and forces escalation. That layered approach, a soft LLM check plus a hard fallback rule, is intentional: the goal is to make failure visible and recoverable rather than to claim the critique is flawless.
