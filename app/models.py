from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_1 = Column(Text, nullable=False)
    participant_2 = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)

    direction = Column(String(10), nullable=False)  # 'inbound' or 'outbound'
    from_address = Column(Text, nullable=False)
    to_address = Column(Text, nullable=False)
    type = Column(String(10), nullable=False)  # 'sms', 'mms', or 'email'
    body = Column(Text, nullable=False)
    attachments = Column(JSONB, default=list)  # list of attachment URLs
    provider_message_id = Column(Text, nullable=True)

    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship('Conversation', back_populates='messages')


class Provider(Base):
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)  # e.g., "twilio", "sendgrid"
    type = Column(String(10), nullable=False)  # 'sms', 'mms', 'email'
