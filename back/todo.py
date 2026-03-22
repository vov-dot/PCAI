import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: str = ""
    completed_at: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        return cls(**data)


class TodoManager:
    def __init__(self, storage_path: str = "data/tasks.json"):
        self.storage_path = Path(storage_path)
        self.tasks: List[Task] = []
        self._ensure_storage_dir()
        self._load_tasks()
    
    def _ensure_storage_dir(self):
        """Создание директории для хранения"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_tasks(self):
        """Загрузка задач из файла"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data]
            except (json.JSONDecodeError, KeyError):
                self.tasks = []
    
    def _save_tasks(self):
        """Сохранение задач в файл"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)
    
    def _get_next_id(self) -> int:
        """Получение следующего ID"""
        if not self.tasks:
            return 1
        return max(t.id for t in self.tasks) + 1
    
    def add_task(self, title: str, description: str = "", priority: str = "medium") -> Task:
        """Добавление новой задачи"""
        task = Task(
            id=self._get_next_id(),
            title=title.strip(),
            description=description.strip(),
            priority=priority if priority in ["low", "medium", "high"] else "medium"
        )
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def remove_task(self, task_id: int) -> bool:
        """Удаление задачи по ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self._save_tasks()
                return True
        return False
    
    def complete_task(self, task_id: int) -> Optional[Task]:
        """Отметка задачи как выполненной"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                task.completed_at = datetime.now().isoformat()
                self._save_tasks()
                return task
        return None
    
    def uncomplete_task(self, task_id: int) -> Optional[Task]:
        """Снятие отметки о выполнении"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = False
                task.completed_at = None
                self._save_tasks()
                return task
        return None
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Получение задачи по ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """Получение всех задач"""
        return self.tasks
    
    def get_pending_tasks(self) -> List[Task]:
        """Получение незавершённых задач"""
        return [t for t in self.tasks if not t.completed]
    
    def get_completed_tasks(self) -> List[Task]:
        """Получение завершённых задач"""
        return [t for t in self.tasks if t.completed]
    
    def filter_by_priority(self, priority: str) -> List[Task]:
        """Фильтрация по приоритету"""
        return [t for t in self.tasks if t.priority == priority]
    
    def search_tasks(self, query: str) -> List[Task]:
        """Поиск задач по тексту"""
        query = query.lower()
        return [
            t for t in self.tasks 
            if query in t.title.lower() or query in t.description.lower()
        ]
    
    def get_statistics(self) -> dict:
        """Статистика по задачам"""
        total = len(self.tasks)
        completed = len(self.get_completed_tasks())
        pending = total - completed
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0
        }
    
    def clear_completed(self) -> int:
        """Удаление всех завершённых задач"""
        initial_count = len(self.tasks)
        self.tasks = self.get_pending_tasks()
        self._save_tasks()
        return initial_count - len(self.tasks)


# Глобальный экземпляр
todo = TodoManager()