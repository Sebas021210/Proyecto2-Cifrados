from pydantic import BaseModel, Field

class ManualTransaction(BaseModel):
    data: str
    hash_extra: str = None