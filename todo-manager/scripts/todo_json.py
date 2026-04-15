#!/usr/bin/env python3
"""
待办事项 JSON 文件操作脚本
用于读写和同步 todo.json 文件
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

TODO_JSON_PATH = "/workspace/projects/workspace/todo.json"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
EDITABLE_FIELDS = {
    "content",
    "priority",
    "created",
    "completed",
    "completed_at",
    "due_date",
    "category",
    "recurrence",
    "notes",
}


def read_todos() -> List[Dict]:
    """读取所有待办事项"""
    if not os.path.exists(TODO_JSON_PATH):
        return []

    with open(TODO_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('todos', [])


def save_todos(todos: List[Dict]) -> None:
    """保存所有待办事项到 todo.json"""
    data = {
        'todos': todos
    }

    with open(TODO_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_completed_at(todo: Dict) -> Optional[datetime]:
    """解析完成时间，无法解析时返回 None"""
    completed_at = todo.get("completed_at")
    if not completed_at:
        return None

    for fmt in (TIMESTAMP_FORMAT, "%Y-%m-%d"):
        try:
            return datetime.strptime(completed_at, fmt)
        except ValueError:
            continue

    return None


def add_todo(content: str, priority: str = 'medium') -> int:
    """添加新的待办事项"""
    todos = read_todos()

    # 生成新ID（最大ID + 1）
    max_id = max([t.get('id', 0) for t in todos], default=0)
    new_id = max_id + 1

    new_todo = {
        'id': new_id,
        'content': content,
        'priority': priority,
        'created': datetime.now().strftime('%Y-%m-%d'),
        'completed': False
    }

    todos.append(new_todo)
    save_todos(todos)

    return new_id


def update_todo(todo_id: int, **kwargs) -> bool:
    """更新待办事项"""
    todos = read_todos()

    for todo in todos:
        if todo.get('id') == todo_id:
            for key, value in kwargs.items():
                if key not in EDITABLE_FIELDS:
                    continue

                if value is None:
                    todo.pop(key, None)
                    continue

                todo[key] = value

            if todo.get("completed") and not todo.get("completed_at"):
                todo["completed_at"] = datetime.now().strftime(TIMESTAMP_FORMAT)
            elif not todo.get("completed"):
                todo.pop("completed_at", None)

            save_todos(todos)
            return True

    return False


def complete_todo(todo_id: int) -> bool:
    """标记待办事项为已完成"""
    return update_todo(
        todo_id,
        completed=True,
        completed_at=datetime.now().strftime(TIMESTAMP_FORMAT),
    )


def delete_todo(todo_id: int) -> bool:
    """删除待办事项"""
    todos = read_todos()
    original_len = len(todos)

    todos = [t for t in todos if t.get('id') != todo_id]

    if len(todos) < original_len:
        save_todos(todos)
        return True

    return False


def get_pending_todos() -> List[Dict]:
    """获取所有未完成的待办"""
    return [t for t in read_todos() if not t.get('completed', False)]


def get_completed_todos() -> List[Dict]:
    """获取所有已完成的待办"""
    return [t for t in read_todos() if t.get('completed', False)]


def get_recently_completed_todos(days: int = 3) -> List[Dict]:
    """获取最近 N 天内完成的待办；缺少 completed_at 的旧数据视为归档，不默认展示"""
    cutoff = datetime.now() - timedelta(days=days)
    recent_completed = []

    for todo in get_completed_todos():
        completed_at = _parse_completed_at(todo)
        if completed_at and completed_at >= cutoff:
            recent_completed.append(todo)

    return recent_completed


def get_display_todos(completed_within_days: int = 3) -> List[Dict]:
    """
    获取默认展示用待办：
    - 所有未完成事项
    - 最近 N 天内完成的事项
    已完成超过 N 天的事项保留在 todo.json 中作为备案，但默认不展示。
    """
    return get_pending_todos() + get_recently_completed_todos(completed_within_days)


def find_todo_by_content(keyword: str) -> Optional[Dict]:
    """根据关键词查找待办"""
    for todo in read_todos():
        if keyword.lower() in todo.get('content', '').lower():
            return todo
    return None


def get_todos_by_priority(priority: str) -> List[Dict]:
    """根据优先级获取待办"""
    return [t for t in read_todos() if t.get('priority', '').lower() == priority.lower()]


if __name__ == '__main__':
    # 测试代码
    print(f"待办文件路径: {TODO_JSON_PATH}")
    print(f"文件存在: {os.path.exists(TODO_JSON_PATH)}")

    todos = read_todos()
    print(f"\n当前待办数量: {len(todos)}")
    print(f"未完成: {len(get_pending_todos())}")
    print(f"已完成: {len(get_completed_todos())}")
