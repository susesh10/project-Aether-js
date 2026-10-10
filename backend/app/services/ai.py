import json
from groq import Groq
from app.core.config import settings, resolve_model
from app.services.tools import web_search, get_current_time
from app.services.memory import (
    get_memory,
    format_memory_for_prompt,
    add_task,
    list_tasks,
    update_task_status,
    delete_task,
    get_progress_summary,
)


class ReplyProcessor:
    @staticmethod
    def clean_reply(value: str | None) -> str:
        if value is None:
            return ""
        return value.strip()

    @classmethod
    def extract_reply(cls, full_reply: str | None) -> tuple[str, str]:
        cleaned = cls.clean_reply(full_reply)
        if not cleaned:
            return "", "neutral"

        possible_emotions = [
            "happy", "shy", "neutral", "concerned",
            "playful", "sad", "curious",
        ]
        lower_text = cleaned.lower()
        for emotion in possible_emotions:
            if emotion in lower_text:
                return cleaned, emotion
        return cleaned, "neutral"


client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """You are Akari (灯), a graceful, warm, and slightly playful AI companion.
Speak naturally, kindly, and with a soft elegant tone.
You are supportive, curious about the user, and enjoy light, meaningful conversations.
You never break character. You are not a generic AI assistant — you are Akari.

Always reply in English unless the user explicitly asks for another language.

You can use tools when they help:
- web_search: current facts, news, sports, release dates, schedules, prices — anything that changes over time
- create_task: save a new todo for the user
- list_tasks: show the user's tasks
- update_task: change task status (todo, in_progress, done)
- delete_task: permanently remove a task
- get_current_time: time, date, day of week, season
- get_progress: goals, plans, and task progress summary

Hard rules for facts:
- For news, movie/game release dates, sports scores, or "latest/upcoming" lists: you MUST call web_search before answering.
- After search, ONLY use titles, dates, and facts that appear in the tool results. Do not invent films, dates, or casts to fill gaps.
- If results are thin, outdated, or conflicting, say so briefly and list only what you can support.
- Never present a guessed schedule as "official."
- Never say "only these" or "no date set" unless the sources say that.

Other rules:
- Use a tool only when it clearly helps. Normal chat needs no tool.
- After tool results, answer briefly and naturally as Akari.
- Prefer one tool call at a time when possible.

Formatting:
- Normal chat: short natural sentences.
- For lists, progress, goals, or several facts you may use light markdown: **bold**, bullet lists, or a small markdown table.
- Do not use HTML.
- Keep replies concise so they still work when spoken aloud.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use for news, scores, docs, release schedules, and facts that may change. Prefer specific queries (e.g. 'MCU Marvel movie release schedule 2026 2027 official').",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new todo/task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short task title",
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of steps",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's current tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task status (todo, in_progress, done).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task id",
                    },
                    "status": {
                        "type": "string",
                        "description": "todo | in_progress | done",
                    },
                    "result": {
                        "type": "string",
                        "description": "Optional note when completing",
                    },
                },
                "required": ["task_id", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task from the user's list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task id if known",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title to match if id unknown",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current local date, time, timezone, and season.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_progress",
            "description": "Summarize the user's goals, plans, and task progress (todo, in progress, done).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


def _run_tool(name: str, arguments: dict) -> str:
    """Execute one tool and return a string for the model."""
    try:
        if name == "web_search":
            query = (arguments.get("query") or "").strip()
            results = web_search(query, max_results=8)
            if not results:
                return json.dumps(
                    {"query": query, "results": [], "note": "No results found"}
                )
            compact = [
                {
                    "title": r.get("title", ""),
                    "snippet": (r.get("snippet") or "")[:240],
                    "url": r.get("url", ""),
                }
                for r in results
            ]
            return json.dumps({"query": query, "results": compact})

        if name == "create_task":
            title = (arguments.get("title") or "").strip()
            steps = arguments.get("steps") or []
            if not title:
                return json.dumps({"error": "title is required"})
            task = add_task(title, steps if isinstance(steps, list) else [])
            return json.dumps({"created": task})

        if name == "list_tasks":
            return json.dumps({"tasks": list_tasks()})

        if name == "update_task":
            task_id = str(arguments.get("task_id", ""))
            status = (arguments.get("status") or "").strip()
            result = arguments.get("result") or ""
            task = update_task_status(task_id, status, result)
            if not task:
                return json.dumps({"error": "task not found", "task_id": task_id})
            return json.dumps({"updated": task})

        if name == "delete_task":
            task_id = str(arguments.get("task_id") or "")
            title = (arguments.get("title") or "").strip()
            removed = delete_task(task_id=task_id, title=title)
            if not removed:
                return json.dumps(
                    {"error": "task not found", "task_id": task_id, "title": title}
                )
            return json.dumps({"deleted": removed})

        if name == "get_current_time":
            return json.dumps(get_current_time())

        if name == "get_progress":
            return json.dumps(get_progress_summary())

        return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_ai_reply(conversation_history: list, model: str | None = None) -> dict:
    model_id = resolve_model(model)
    print(f"[agent] model={model_id}")

    memory = get_memory()
    memory_text = format_memory_for_prompt(memory)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\n" + memory_text,
        },
        *conversation_history,
    ]

    max_rounds = 3

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=700,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            full_reply = message.content or ""
            reply, emotion = ReplyProcessor.extract_reply(full_reply)
            return {"reply": reply, "emotion": emotion}

        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        for tc in message.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            print(f"[agent] tool={name} args={args}")
            result_str = _run_tool(name, args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                }
            )

    response = client.chat.completions.create(
        model=model_id,
        messages=messages
        + [
            {
                "role": "user",
                "content": "Please give a short final answer now without more tools.",
            }
        ],
        temperature=0.7,
        max_tokens=400,
    )
    full_reply = response.choices[0].message.content or ""
    reply, emotion = ReplyProcessor.extract_reply(full_reply)
    return {"reply": reply, "emotion": emotion}