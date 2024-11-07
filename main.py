from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import aiofiles
from models import Message, UploadedFile, Chat
from schemas import MessageCreate
import uvicorn

DATABASE_URL = 'mysql+pymysql://mytrade:jh2jh8%26%237S1%40%21%21DFERkj_@0.0.0.0:3306/mytrade'

app = FastAPI()


engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


MAX_FILE_SIZE = 500 * 1024 * 1024


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Размер файла превышает 500 МБ")

    if not file.content_type.startswith(("image/", "video/", "application/pdf")):
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")

    file_location = f"uploads/{file.filename}"
    async with aiofiles.open(file_location, "wb") as file_object:
        await file_object.write(contents)

    # Сохранение информации о файле в базе данных
    db_file = UploadedFile(
        filename=file.filename,
        file_path=file_location,
        file_type=file.content_type,
        file_size=len(contents)
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return {"file_location": file_location, "file_id": db_file.id}


@app.post("/messages/")
async def send_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    # Проверка существования чата между отправителем и получателем
    chat = await db.execute(
        select(Chat).where(
            or_(
                (Chat.user1_id == message.sender_id) & (Chat.user2_id == message.receiver_id),
                (Chat.user1_id == message.receiver_id) & (Chat.user2_id == message.sender_id)
            )
        )
    )
    chat = chat.scalars().first()

    if not chat:
        # Создаем новый чат, если его не существует
        chat = Chat(user1_id=message.sender_id, user2_id=message.receiver_id)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

    # Создаем сообщение
    db_message = Message(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        file_id=message.file_id,
        chat_id=chat.id
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message


@app.get("/messages/{chat_id}")
async def get_messages(chat_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.timestamp.desc())
        .limit(10)
    )
    messages = result.scalars().all()
    return messages

manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", user_id)
            await manager.broadcast(f"User #{user_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"User #{user_id} left the chat")


@app.post("/chats/")
async def create_chat():
    async with AsyncSessionLocal() as session:
        chat = Chat()
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat


if __name__ == "__main__":
    uvicorn.run("main:app", port=8010)
