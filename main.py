from typing import Optional

from fastapi import FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="Task Manager API",
    description="Минимальный API для создания и получения задач.",
    version="1.0.0",
)


class TaskCreate(BaseModel):
    """Данные для создания новой задачи."""

    title: str = Field(
        min_length=3,
        max_length=100,
        description="Заголовок задачи длиной от 3 до 100 символов.",
    )

    description: Optional[str] = Field(
        default=None,
        description="Дополнительное описание задачи.",
    )

    priority: int = Field(
        ge=1,
        le=5,
        description="Приоритет задачи: целое число от 1 до 5.",
    )


class TaskResponse(TaskCreate):
    """Данные созданной или найденной задачи."""

    id: int = Field(
        description="Уникальный идентификатор задачи.",
    )


tasks: dict[int, TaskResponse] = {}
next_id = 1


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой задачи",
    description=(
        "Создаёт новую задачу на основе переданных данных. "
        "Заголовок должен содержать от 3 до 100 символов, "
        "приоритет — целое число от 1 до 5. "
        "После успешного создания возвращает данные задачи "
        "вместе с присвоенным идентификатором."
    ),
    responses={
        422: {
            "description": "Переданные данные не соответствуют требованиям API."
        }
    },
)
def create_task(task: TaskCreate):
    global next_id

    new_task = TaskResponse(
        id=next_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
    )

    tasks[next_id] = new_task
    next_id += 1

    return new_task


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Получение задачи по идентификатору",
    description=(
        "Возвращает данные задачи по её идентификатору. "
        "Если задача с указанным идентификатором отсутствует, "
        "сервер возвращает HTTP 404 Not Found."
    ),
    responses={
        404: {
            "description": "Задача с указанным идентификатором не найдена."
        },
        422: {
            "description": "Переданные данные не соответствуют требованиям API."
        },
    },
)
def get_task(
    task_id: int = Path(
        ...,
        description="Идентификатор задачи, которую необходимо получить.",
    )
):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task
