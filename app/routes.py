from flask import Blueprint, request, jsonify, current_app
from app.service import send_message, save_message, get_conversations_all, get_messages_by_conversations
from app import db

api = Blueprint('api', __name__)

# --- Outbound Message Endpoints ---

@api.route('/api/messages/sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    try:
        message = send_message(
            from_address=data['from'],
            to_address=data['to'],
            msg_type=data['type'],  # should be 'sms' or 'mms'
            body=data['body'],
            attachments=data.get('attachments', []),
            timestamp=data['timestamp']
        )
        return jsonify({"message_id": str(message.id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/api/messages/email', methods=['POST'])
def send_email():
    data = request.get_json()
    try:
        message = send_message(
            from_address=data['from'],
            to_address=data['to'],
            msg_type='email',
            body=data['body'],
            attachments=data.get('attachments', []),
            timestamp=data['timestamp']
        )
        return jsonify({"message_id": str(message.id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Inbound Webhook Endpoints ---

@api.route('/api/webhooks/sms', methods=['POST'])
def receive_sms_webhook():
    data = request.get_json()
    try:
        message = save_message(
            direction='inbound',
            from_address=data['from'],
            to_address=data['to'],
            msg_type=data['type'],  # 'sms' or 'mms'
            body=data['body'],
            attachments=data.get('attachments', []),
            timestamp=data['timestamp'],
            provider_message_id=data.get('messaging_provider_id')
        )
        return jsonify({"message_id": str(message.id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/api/webhooks/email', methods=['POST'])
def receive_email_webhook():
    data = request.get_json()
    try:
        message = save_message(
            direction='inbound',
            from_address=data['from'],
            to_address=data['to'],
            msg_type='email',
            body=data['body'],
            attachments=data.get('attachments', []),
            timestamp=data['timestamp'],
            provider_message_id=data.get('provider_message_id')
        )
        return jsonify({"message_id": str(message.id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Conversation Endpoints ---

@api.route('/api/conversations', methods=['GET'])
def get_conversations():
    conversations = get_conversations_all()
    result = [
        {
            "id": str(conv.id),
            "participant_1": conv.participant_1,
            "participant_2": conv.participant_2,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        } for conv in conversations
    ]
    return jsonify(result), 200


@api.route('/api/conversations/<uuid:conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    messages = get_messages_by_conversations(conversation_id)
    result = [
        {
            "id": str(msg.id),
            "direction": msg.direction,
            "from": msg.from_address,
            "to": msg.to_address,
            "type": msg.type,
            "body": msg.body,
            "attachments": msg.attachments,
            "provider_message_id": msg.provider_message_id,
            "timestamp": msg.timestamp.isoformat(),
            "created_at": msg.created_at.isoformat()
        } for msg in messages
    ]
    return jsonify(result), 200
