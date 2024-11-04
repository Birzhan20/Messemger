from pydantic import BaseModel


class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    file_id: int | None = None
