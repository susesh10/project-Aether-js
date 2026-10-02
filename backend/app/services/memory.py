from app.core.database import memory_collection


DEFAULT_USER_ID = "default"

def get_default_memory():
    return {
        "user_id": DEFAULT_USER_ID,
        "name": "",
        "goals": [],
        "plans": [],
        "preferences": [],
        "tasks": []
    }

def get_memory(user_id: str = DEFAULT_USER_ID) -> dict:
    memory = memory_collection.find_one({"user_id": user_id})

    if memory is None:
        memory = get_default_memory()
        memory_collection.insert_one(memory)
        memory = memory_collection.find_one({"user_id": user_id})

    # Remove MongoDB's internal _id for cleaner use
    memory.pop("_id", None)
    return memory

def format_memory_for_prompt(memory: dict) -> str:
    name = memory.get("name") or "Unknown"
    goals = memory.get("goals") or []
    plans = memory.get("plans") or []
    preferences = memory.get("preferences") or []
    raw_tasks = memory.get("tasks") or []

    goals_text = ", ".join(goals) if goals else "None yet"
    plans_text = ", ".join(plans) if plans else "None yet"
    preferences_text = ", ".join(preferences) if preferences else "None yet"

    if raw_tasks and isinstance(raw_tasks[0], dict):
        tasks_text = "; ".join(
            f"{t.get('id')}:{t.get('title')}[{t.get('status')}]"
            for t in raw_tasks
        ) or "None yet"
    else:
        # old string-style tasks, if any remain
        tasks_text = ", ".join(raw_tasks) if raw_tasks else "None yet"

    return f"""
Long-term memory about the user:
- Name: {name}
- Goals: {goals_text}
- Plans: {plans_text}
- Preferences: {preferences_text}
- Tasks: {tasks_text}
""".strip()

def update_memory(fields: dict, user_id: str = DEFAULT_USER_ID) -> dict:
    memory_collection.update_one(
        {"user_id": user_id},
        {"$set": fields},
        upsert=True
    )
    return get_memory(user_id)
def merge_memory_update(current: dict, extracted: dict) -> dict:
    updated = {}

    # Name: update only if a real new name is provided
    if extracted.get("name"):
        updated["name"] = extracted["name"]

    # Lists: add only new items
    for key in ["goals", "plans", "preferences", "tasks"]:
        old_items = current.get(key, [])
        new_items = extracted.get(key, []) or []
        merged = old_items[:]
        for item in new_items:
            if item and item not in merged:
                merged.append(item)
        if merged != old_items:
            updated[key] = merged

    return updated
def clear_memory(user_id: str = DEFAULT_USER_ID) -> dict:
    """Reset long-term memory to default empty values."""
    memory_collection.delete_one({"user_id": user_id})
    return get_memory(user_id)
def add_task(title: str, steps: list | None = None, user_id: str = DEFAULT_USER_ID) -> dict:
    memory = get_memory(user_id)
    tasks = memory.get("tasks", [])

    new_task = {
        "id": str(len(tasks) + 1),
        "title": title.strip(),
        "status": "todo",          # todo | in_progress | done
        "steps": steps or [],
        "result": ""
    }
    tasks.append(new_task)
    update_memory({"tasks": tasks}, user_id)
    return new_task


def update_task_status(
    task_id: str,
    status: str,
    result: str = "",
    user_id: str = DEFAULT_USER_ID
) -> dict | None:
    memory = get_memory(user_id)
    tasks = memory.get("tasks", [])

    for task in tasks:
        if str(task.get("id")) == str(task_id):
            task["status"] = status
            if result:
                task["result"] = result
            update_memory({"tasks": tasks}, user_id)
            return task
    return None



def list_tasks(user_id: str = DEFAULT_USER_ID) -> list:
    memory = get_memory(user_id)
    return memory.get("tasks", [])

def get_progress_summary(user_id: str = DEFAULT_USER_ID) -> dict:
    memory = get_memory(user_id)
    goals = memory.get("goals") or []
    plans = memory.get("plans") or []
    raw_tasks = memory.get("tasks") or []

    tasks = raw_tasks if raw_tasks and isinstance(raw_tasks[0], dict) else []
    # if old string tasks, treat as open todos with no id
    if raw_tasks and not tasks:
        tasks = [{"id": str(i + 1), "title": t, "status": "todo"} for i, t in enumerate(raw_tasks) if t]

    todo = [t for t in tasks if t.get("status") == "todo"]
    in_progress = [t for t in tasks if t.get("status") == "in_progress"]
    done = [t for t in tasks if t.get("status") == "done"]

    def brief(items, limit=8):
        out = []
        for t in items[:limit]:
            out.append({"id": t.get("id"), "title": t.get("title"), "status": t.get("status")})
        return out

    return {
        "name": memory.get("name") or "",
        "goals": goals[:10],
        "plans": plans[:10],
        "counts": {
            "todo": len(todo),
            "in_progress": len(in_progress),
            "done": len(done),
            "total_tasks": len(tasks),
        },
        "open_tasks": brief(todo + in_progress),
        "recent_done": brief(list(reversed(done))[:5]),
    }
def delete_task(task_id: str = "", title: str = "", user_id: str = DEFAULT_USER_ID) -> dict | None:
    """Remove a task by id or by matching title (case-insensitive)."""
    memory = get_memory(user_id)
    tasks = memory.get("tasks") or []
    if not tasks:
        return None

    remaining = []
    removed = None
    title_l = (title or "").strip().lower()

    for task in tasks:
        if not isinstance(task, dict):
            remaining.append(task)
            continue
        match_id = task_id and str(task.get("id")) == str(task_id)
        match_title = title_l and (task.get("title") or "").strip().lower() == title_l
        if removed is None and (match_id or match_title):
            removed = task
            continue
        remaining.append(task)

    if removed is None and title_l:
        # partial title match as fallback
        for task in tasks:
            if isinstance(task, dict) and title_l in (task.get("title") or "").lower():
                removed = task
                remaining = [t for t in tasks if t is not removed]
                break

    if removed is None:
        return None

    update_memory({"tasks": remaining}, user_id)
    return removed