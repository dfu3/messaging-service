from flask import Blueprint, request, jsonify
from app.service import send_message, save_message, get_conversations_all, get_messages_by_conversations
from datetime import datetime
import phonenumbers

api = Blueprint('api', __name__)

# --- Outbound Message Endpoints ---

@api.route('/api/messages/sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    error = validate_message_payload(data)
    if error:
        return error
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
    error = validate_message_payload(data, is_email=True)
    if error:
        return error
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
    error = validate_message_payload(data, inbound=True)
    if error:
        return error
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
    error = validate_message_payload(data, inbound=True, is_email=True)
    if error:
        return error
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


def is_valid_phone(number: str) -> bool:
    try:
        parsed = phonenumbers.parse(number, None)
        return phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        return False

def validate_message_payload(data, inbound=False, is_email=False):
    required_fields = ["from", "to", "body", "timestamp"]

    if inbound:
        required_fields.append("messaging_provider_id")

    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Validate 'from' and 'to' for phone or email
    if not is_email:
        if not isinstance(data["from"], str) or not is_valid_phone(data["from"]):
            return jsonify({"error": "'from' must be a valid phone number"}), 400
        if not isinstance(data["to"], str) or not is_valid_phone(data["to"]):
            return jsonify({"error": "'to' must be a valid phone number"}), 400
    else:
        if not isinstance(data["from"], str) or "@" not in data["from"]:
            return jsonify({"error": "'from' must be a valid email address"}), 400
        if not isinstance(data["to"], str) or "@" not in data["to"]:
            return jsonify({"error": "'to' must be a valid email address"}), 400

    if not isinstance(data["body"], str):
        return jsonify({"error": "'body' must be a string"}), 400

    if "attachments" in data and data["attachments"] is not None:
        if not isinstance(data["attachments"], list):
            return jsonify({"error": "'attachments' must be a list or null"}), 400
        if not all(isinstance(item, str) for item in data["attachments"]):
            return jsonify({"error": "All attachments must be strings"}), 400

    try:
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return jsonify({"error": "Invalid ISO 8601 format for 'timestamp'"}), 400

    return None
