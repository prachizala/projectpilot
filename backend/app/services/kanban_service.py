from typing import List
from sqlalchemy.orm import Session
from app.models.models import Task

class KanbanService:
    @staticmethod
    def reorder_task(
        db: Session,
        task: Task,
        new_status: str,
        new_position: int
    ) -> Task:
        old_status = task.status
        old_position = task.position

        # Fetch all tasks in target column
        target_tasks = db.query(Task).filter(
            Task.project_id == task.project_id,
            Task.status == new_status,
            Task.id != task.id
        ).order_by(Task.position.asc()).all()

        # Clamp new_position to valid bounds
        new_position = max(0, min(new_position, len(target_tasks)))

        if old_status == new_status:
            # Reordering within same column
            if old_position < new_position:
                # Moving down: shift intervening tasks up
                for t in target_tasks:
                    if old_position < t.position <= new_position:
                        t.position -= 1
            elif old_position > new_position:
                # Moving up: shift intervening tasks down
                for t in target_tasks:
                    if new_position <= t.position < old_position:
                        t.position += 1
        else:
            # Moving between different columns
            # 1. Close the gap in old column
            old_tasks = db.query(Task).filter(
                Task.project_id == task.project_id,
                Task.status == old_status,
                Task.id != task.id
            ).all()
            for t in old_tasks:
                if t.position > old_position:
                    t.position -= 1

            # 2. Open space in new column
            for t in target_tasks:
                if t.position >= new_position:
                    t.position += 1

        task.status = new_status
        task.position = new_position
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def append_task(db: Session, project_id: int, owner_id: int, data: dict) -> Task:
        """Appends a new task to the end of a specified column."""
        status = data.get("status", "todo")
        max_pos = db.query(Task).filter(
            Task.project_id == project_id,
            Task.status == status
        ).count()

        task = Task(
            project_id=project_id,
            owner_id=owner_id,
            title=data["title"].strip(),
            description=data.get("description"),
            status=status,
            position=max_pos,
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date")
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
