from celery.exceptions import NotRegistered
from celery.result import AsyncResult
from app.core.celery import celery_app
from fastapi import HTTPException


class TaskService:
    def get_list(self):
        filtered_tasks = []
        tasks = celery_app.tasks
        for key, value in tasks.items():
            if not key.startswith("celery."):
                filtered_tasks.append({key, value})
        return filtered_tasks

    def get(self):
        return celery_app.current_worker_task

    def get_status(self, uid: str):
        try:
            result = AsyncResult(id=uid, app=celery_app)
        except NotRegistered:
            raise HTTPException(status_code=404, detail="Task not found")
        return result.status

    def get_result(self, uid: str):
        try:
            result = AsyncResult(id=uid, app=celery_app)
        except NotRegistered:
            raise HTTPException(status_code=404, detail="Task not found")
        return result

    def run(self, name: str, args: list | None = None, kwargs: dict | None = None):
        task = celery_app.send_task(name=name, args=args, kwargs=kwargs)
        return task


task_service = TaskService()
