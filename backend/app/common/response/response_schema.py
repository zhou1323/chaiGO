#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from app.common.response.response_code import CustomResponseCode
from asgiref.sync import sync_to_async
from sqlmodel import SQLModel

_ExcludeData = set[int | str] | dict[int | str, Any]

__all__ = ["ResponseModel", "response_base"]


class ResponseModel(SQLModel):
    """
    Unified return model

    E.g. ::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    code: int = CustomResponseCode.HTTP_200.code
    message: str = CustomResponseCode.HTTP_200.message
    data: Any | None = None


class ResponseBase:
    """
    Unified return method. The method in this class will return a ResponseModel model, which exists as a coding style

    E.g. ::

        @router.get('/test')
        def test() -> ResponseModel:
            return await response_base.success(data={'test': 'test'})
    """

    @staticmethod
    @sync_to_async
    def __response(
        *, res: CustomResponseCode = None, data: Any | None = None
    ) -> ResponseModel:
        return ResponseModel(code=res.code, message=res.message, data=data)

    async def success(
        self,
        *,
        res: CustomResponseCode = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseModel:
        return await self.__response(res=res, data=data)

    async def fail(
        self,
        *,
        res: CustomResponseCode = CustomResponseCode.HTTP_400,
        data: Any = None,
    ) -> ResponseModel:
        return await self.__response(res=res, data=data)


response_base = ResponseBase()
