import requests
import json

BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

def print_response(resp):
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
    print()

def main():
    print("=== Testing Messaging Service Endpoints ===")
    print(f"Base URL: {BASE_URL}\n")

    # Test 1: Send SMS
    print("1. Testing SMS send...")
    resp = requests.post(f"{BASE_URL}/api/messages/sms", headers=HEADERS, json={
        "from": "+12016661234",
        "to": "+18045551234",
        "type": "sms",
        "body": "Hello! This is a test SMS message.",
        "attachments": None,
        "timestamp": "2024-11-01T14:00:00Z"
    })
    print_response(resp)

    # Test 2: Send MMS
    print("2. Testing MMS send...")
    resp = requests.post(f"{BASE_URL}/api/messages/sms", headers=HEADERS, json={
        "from": "+12016661234",
        "to": "+18045551234",
        "type": "mms",
        "body": "Hello! This is a test MMS message with attachment.",
        "attachments": ["https://example.com/image.jpg"],
        "timestamp": "2024-11-01T14:00:00Z"
    })
    print_response(resp)

    # Test 3: Send Email
    print("3. Testing Email send...")
    resp = requests.post(f"{BASE_URL}/api/messages/email", headers=HEADERS, json={
        "from": "user@usehatchapp.com",
        "to": "contact@gmail.com",
        "body": "Hello! This is a test email message with <b>HTML</b> formatting.",
        "attachments": ["https://example.com/document.pdf"],
        "timestamp": "2024-11-01T14:00:00Z"
    })
    print_response(resp)

    # Test 4: Incoming SMS webhook
    print("4. Testing incoming SMS webhook...")
    resp = requests.post(f"{BASE_URL}/api/webhooks/sms", headers=HEADERS, json={
        "from": "+18045551234",
        "to": "+12016661234",
        "type": "sms",
        "messaging_provider_id": "message-1",
        "body": "This is an incoming SMS message",
        "attachments": None,
        "timestamp": "2024-11-01T14:00:00Z"
    })
    print_response(resp)

    # Test 5: Incoming MMS webhook
    print("5. Testing incoming MMS webhook...")
    resp = requests.post(f"{BASE_URL}/api/webhooks/sms", headers=HEADERS, json={
        "from": "+18045551234",
        "to": "+12016661234",
        "type": "mms",
        "messaging_provider_id": "message-2",
        "body": "This is an incoming MMS message",
        "attachments": ["https://example.com/received-image.jpg"],
        "timestamp": "2024-11-01T14:00:00Z"
    })
    print_response(resp)

    # Test 6: Incoming Email webhook
    print("6. Testing incoming Email webhook...")
    resp = requests.post(f"{BASE_URL}/api/webhooks/email", headers=HEADERS, json={
        "from": "contact@gmail.com",
        "to": "user@usehatchapp.com",
        "messaging_provider_id": "message-3",
        "body": "<html><body>This is an incoming email with <b>HTML</b> content</body></html>",
        "attachments": ["https://example.com/received-document.pdf"],
        "timestamp": "2024-11-01T14:00:00Z"
    })
    print_response(resp)

    # Test 7: Get conversations
    print("7. Testing get conversations...")
    resp = requests.get(f"{BASE_URL}/api/conversations", headers=HEADERS)
    print_response(resp)
    try:
        convos = resp.json()
        convo_id = convos[0]["id"] if convos else None
    except Exception:
        convo_id = None

    # Test 8: Get messages for a conversation
    if convo_id:
        print("8. Testing get messages for conversation...")
        resp = requests.get(f"{BASE_URL}/api/conversations/{convo_id}/messages", headers=HEADERS)
        print_response(resp)
    else:
        print("8. Skipped: No conversation found.\n")

    print("=== Test script completed ===")

if __name__ == "__main__":
    main()
