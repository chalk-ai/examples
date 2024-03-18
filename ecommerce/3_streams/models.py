from pydantic import BaseModel

class InteractionMessage(BaseModel):
    id: str
    user_id: str
    seller_id: str
    interaction_kind: str
