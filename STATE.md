# CommAgent — Project State Document

## What this is
A self-critiquing AI community agent for Track 3 (AI Community Agent) of the
Build with Swytchcode buildathon. It monitors a Telegram community for
questions, answers them using a Notion knowledge base, and — critically —
runs a self-critique step before posting: it checks whether its own draft
answer is actually supported by retrieved KB content. If not confident, it
escalates to a human instead of guessing.

Demo persona: a "Women in Tech" mentorship/bootcamp community.

## Why this exists (judging angle)
Most Track 3 submissions will be simple retrieve-and-answer bots. Our
differentiator is the self-critique loop — the agent validates its own
output against ground truth before acting, and visibly escalates instead of
hallucinating. This is the story to keep front-of-mind in every implementation
decision: don't just make it work, make the critique step *visibly* do
something in the demo.

## Deadline
Submission: 3:30 PM, 26 Sept 2026 (Commudle). Build budget: 7.5 hours from
~10.30 PM, 25 Sept 2026.

## Required for submission
- Working AI agent (LangGraph)
- ≥3 Swytchcode APIs: Telegram, Notion, (Resend optional/3rd if time allows —
  otherwise the 3rd is satisfied by Telegram+Notion+one more; confirm before
  submission which 3 are actually wired)
- Public GitHub repo, README, architecture diagram, setup instructions, demo

## Architecture
Telegram (member question)
-> Telegram Bot Webhook -> FastAPI backend
-> LangGraph agent:
1. retrieve (vector search over Notion KB, Chroma)
2. draft (LLM answer grounded in retrieved chunks)
3. critique (is the draft actually supported by retrieved context?)
4. decide:
confident -> post to Telegram + log "resolved" to Notion
not confident -> post "checking with a mentor" to Telegram
+ flag in Notion (+ optional Resend digest)
-> every step logged; dashboard shows the reasoning trail live



## Tech stack (locked — do not change mid-build)
- Agent framework: LangGraph (Python)
- Backend: FastAPI
- Vector store: Chroma (in-process, no external service)
- KB source: Notion API (fetch docs -> chunk -> embed)
- LLM: Claude API (2 calls per query: draft, critique)
- Bot: python-telegram-bot or raw Telegram Bot API via webhook
- Frontend: Next.js (App Router), polls backend `/logs` endpoint
- Deploy: frontend -> Vercel; backend -> Render

## Repo structure
commagent/
├── backend/
│ ├── main.py # FastAPI app + Telegram webhook route
│ ├── agent/
│ │ ├── graph.py # LangGraph graph definition
│ │ ├── nodes.py # retrieve, draft, critique, decide functions
│ │ └── kb.py # Notion fetch + chunk + Chroma index/query
│ ├── integrations/
│ │ ├── telegram.py
│ │ ├── notion.py
│ │ └── resend.py # optional, only if time allows
│ ├── requirements.txt
│ └── .env.example
├── frontend/
│ ├── app/
│ │ ├── page.tsx # dashboard: live reasoning trail
│ │ └── api/logs/route.ts # proxies backend /logs
│ └── package.json
├── docs/
│ ├── architecture.md # (or .png) diagram for submission
│ └── kb_seed/ # the mock Notion docs, also kept as .md backup
├── .cursorrules
├── STATE.md # this file
└── README.md



## KB seed content (docs/kb_seed/, mirrored into Notion)
1. `faq.md` — program logistics, access, reporting bugs, refund/cancellation
2. `policy.md` — community guidelines, eligibility, pricing/plans
3. `technical.md` — setup steps, common errors (if applicable)
4. `known_issues.md` — current known issues + ETA (used to demo
   time-sensitive correctness)

Plant at least one Telegram demo question with NO answer in the KB, to
reliably trigger the escalation path live for judges.

## Current status
- [x] Track locked (Track 3)
- [x] Idea locked (Community Answer Agent, self-critique loop)
- [x] Persona locked (Women in Tech community)
- [x] Stack locked
- [ ] Repo initialized
- [ ] KB seed docs written
- [ ] Notion workspace + API key set up
- [ ] Telegram bot created (@BotFather)
- [ ] Backend: agent graph (retrieve/draft/critique/decide)
- [ ] Backend: Telegram webhook wired
- [ ] Backend: deployed to Railway
- [ ] Frontend: dashboard built
- [ ] Frontend: deployed to Vercel
- [ ] End-to-end test (happy path + escalation path)
- [ ] README + architecture diagram
- [ ] Submitted to Commudle

## Rules for any AI assistant (Copilot/Cursor) picking this up
- Do NOT change the tech stack, track, or architecture — it's locked, time is
  the constraint, not the idea.
- Always keep the self-critique step meaningfully separate from the draft
  step (two distinct LLM calls / graph nodes) — collapsing them into one
  removes the entire project USP.
- Prefer working-but-simple over elegant-but-broken. Ship the happy path,
  then the escalation path, then polish.
- Update the "Current status" checklist above as steps complete.

## Deploy target
- Frontend -> Vercel
- Backend -> Render free tier (web service, auto-deploy from GitHub repo).
  Free tier cold-starts after ~15 min idle (~30-50s wake time) — ping the
  backend URL every few minutes during the demo/judging window to keep it
  warm.

### Render deploy steps
1. Push backend/ to GitHub (already in monorepo — set Render's root
   directory to `backend/`)
2. Render dashboard -> New -> Web Service -> connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: NOTION_API_KEY, TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY,
   (RESEND_API_KEY if used)
6. Deploy, copy the live URL, set it as the Telegram webhook target