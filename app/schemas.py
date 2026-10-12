from pydantic import BaseModel, Field
from typing import Optional

class EventRequest(BaseModel):
    type: str  # "deposit", "withdraw" ou "transfer"
    origin: Optional[str] = None
    destination: Optional[str] = None
    amount: int = Field(gt=0) # Garante que o valor seja sempre maior que zero
