from flask import current_app
from datetime import datetime, timezone
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Message, Conversation

# stuff for mocking cleint call
import requests_mock
import uuid
import os


def save_message(
    direction: str,
    from_address: str,
    to_address: str,
    msg_type: str,
    body: str,
    attachments: list,
    timestamp: str,
    provider_message_id=None
) -> Message:
    """
    Finds or creates a conversation, then saves a message tied to it.
    """
    # Find or create a conversation
    try:
        conversation = Conversation.query.filter(
            or_(
                and_(
                    Conversation.participant_1 == from_address,
                    Conversation.participant_2 == to_address
                ),
                and_(
                    Conversation.participant_1 == to_address,
                    Conversation.participant_2 == from_address
                )
            )
        ).first()

        if not conversation:
            conversation = Conversation(
                participant_1=from_address,
                participant_2=to_address
            )
            db.session.add(conversation)
            db.session.flush()

    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Failed to fetch or create conversation: {e}")

    # Create and save the message
    message = Message(
        direction=direction,
        from_address=from_address,
        to_address=to_address,
        type=msg_type,
        body=body,
        attachments=attachments or [],
        timestamp=timestamp,
        created_at=datetime.now(timezone.utc),
        conversation_id=conversation.id,
        provider_message_id=provider_message_id
    )

    try:
        db.session.add(message)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Failed to save message: {e}")

    return message


def get_conversations_all():
    return Conversation.query.order_by(Conversation.updated_at.desc()).all()

def get_messages_by_conversations(conversation_id):
    return Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()

def send_message(
    from_address: str,
    to_address: str,
    msg_type: str,
    body: str,
    attachments: list,
    timestamp: str
) -> Message:
    """
    Saves and sends a message via the appropriate provider.
    Handles retry logic and failures via the provider class.
    """
    direction = "outbound"

    # Save the message without provider_message_id
    saved_message = save_message(
        direction=direction,
        from_address=from_address,
        to_address=to_address,
        msg_type=msg_type,
        body=body,
        attachments=attachments,
        timestamp=timestamp
    )

    # Choose the appropriate provider
    if msg_type == "sms" or msg_type == "mms":
        provider = current_app.config['sms_provider']
    elif msg_type == "email":
        provider = current_app.config['email_provider']
    else:
        raise ValueError(f"Unsupported message type: {msg_type}")

    # Try sending via the mocked provider
    try:
        with requests_mock.Mocker() as m:
            # simluate real http client call
            m.post(os.environ['VERIZON_POST_ENDPOINT'], json={'id': f"sms-{uuid.uuid4()}"})
            m.post(os.environ['GMAIL_POST_ENDPOINT'], json={'id': f"email-{uuid.uuid4()}"})

            external_id = provider.send_with_retry({
                "from": from_address,
                "to": to_address,
                "body": body,
                "attachments": attachments,
                "timestamp": timestamp
            })

            if external_id:
                # Update message with external ID
                saved_message.provider_message_id = external_id
                db.session.commit()

    except Exception as e:
        # outbound messages without a provider_message_id can be assumed to have failed
        print(f"Message sending failed: {e}")

    return saved_message
