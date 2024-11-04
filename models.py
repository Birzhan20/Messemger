from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_role_id = Column(Integer)
    name = Column(String(256), index=True)
    company_name = Column(String(256), index=True)
    description_tr = Column(Integer)
    bin = Column(Integer)
    email = Column(String(256), unique=True, index=True)
    email_verified_at = Column(DateTime)
    password = Column(String(256))
    balance = Column(DECIMAL)
    is_activated = Column(Boolean)
    moderation_status = Column(Boolean)
    representative_phone = Column(String(256), nullable=True)
    entrepreneurial_activity_id = Column(Integer, nullable=True)
    remember_token = Column(String(256), nullable=True)
    story_image_slug = Column(String(256), nullable=True)
    story_video_slug = Column(String(256), nullable=True)
    meta_title_tr = Column(Integer, nullable=True)
    meta_description_tr = Column(Integer, nullable=True)
    meta_keywords_tr = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    about_tr = Column(Integer, nullable=True)
    rating = Column(DECIMAL)
    reviews_count = Column(Integer)
    stripe_id = Column(String(256), nullable=True)
    pm_type = Column(String(256), nullable=True)
    pm_last_four = Column(String(256), nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)
    page_description_tr = Column(Integer, nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String, unique=True)
    file_type = Column(String)
    file_size = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"))
    user2_id = Column(Integer, ForeignKey("users.id"))

    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])

