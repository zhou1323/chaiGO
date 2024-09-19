from typing import Annotated
from app.api.deps import get_current_user
from app.common.response.response_schema import ResponseModel, response_base
from fastapi import APIRouter, Depends, Query, Response, Path, Body
from app.api.task.service.task_service import task_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/test")
async def test() -> ResponseModel:
    task = task_service.test_task()
    return await response_base.success(data={"task_id": task.id})


@router.get("/")
async def get_all_tasks() -> ResponseModel:
    tasks = task_service.get_list()
    return await response_base.success(data=tasks)


@router.get("/current")
async def get_current_task() -> ResponseModel:
    task = task_service.get()
    return await response_base.success(data=task)


@router.get("/{uid}/status")
async def get_task_status(
    uid: Annotated[str, Path(description="task id")]
) -> ResponseModel:
    status = task_service.get_status(uid)
    return await response_base.success(data=status)


@router.get("/{uid}")
async def get_task_result(
    uid: Annotated[str, Path(description="task id")]
) -> ResponseModel:
    task = task_service.get_result(uid)
    return await response_base.success(data=task)


@router.post("/{name}")
async def run_task(
    name: Annotated[str, Path(description="task name")],
    args: Annotated[
        list | None, Body(description="task function position arguments")
    ] = None,
    kwargs: Annotated[
        dict | None, Body(description="task function keyword arguments")
    ] = None,
) -> ResponseModel:
    task = task_service.run(name=name, args=args, kwargs=kwargs)
    return await response_base.success(data=task)
