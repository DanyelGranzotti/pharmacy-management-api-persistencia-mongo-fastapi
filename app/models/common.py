from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 10
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
