from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data: T

class BaseRequest(BaseModel, Generic[T]):
    data: T