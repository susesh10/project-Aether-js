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
    tasks = memory.get("tasks") or []
    goals_text = ", ".join(goals) if goals else "None yet"
    plans_text = ", ".join(plans) if plans else "None yet"
    preferences_text = ", ".join(preferences) if preferences else "None yet"
    tasks_text = ", ".join(tasks) if tasks else "None yet"

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