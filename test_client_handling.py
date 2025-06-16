from client_integrations.providers import SmsProvider
import requests_mock

sms_client = SmsProvider(endpoint="https://api.verizon.com/sms/send")

def test_provider_client_success():
    print('test_provider_client_success')
    with requests_mock.Mocker() as m:
        matcher = m.post("https://api.verizon.com/sms/send", json={"id": "sms-123"}, status_code=201)
        provider_id = sms_client.send_with_retry({'body': 'this is a text'})
        print(f"Provider ID: {provider_id}")
        assert provider_id == "sms-123"

def test_provider_client_retry():
    print('test_provider_client_retry')
    with requests_mock.Mocker() as m:
        matcher = m.post("https://api.verizon.com/sms/send", status_code=429)
        provider_id = sms_client.send_with_retry({'body': 'this is a text'}, max_retries=2)
        initial_call = 1
        retry_calls = matcher.call_count - initial_call
        print(f"Call count for 2 retries: {retry_calls}")
        assert provider_id == None
        assert retry_calls == 2

def test_provider_client_bad_request():
    print('test_provider_client_bad_request')
    with requests_mock.Mocker() as m:
        matcher = m.post("https://api.verizon.com/sms/send", status_code=400)
        provider_id = sms_client.send_with_retry({'body': 'this is a text'})
        print(f"No ID after Bad Request:  {provider_id} -end")
        assert provider_id == None

def test_provider_client_server_error():
    print('test_provider_client_server_error')
    with requests_mock.Mocker() as m:
        matcher = m.post("https://api.verizon.com/sms/send", status_code=500)
        provider_id = sms_client.send_with_retry({'body': 'this is a text'})
        print(f"No ID after Server Error:  {provider_id} -end")
        assert provider_id == None

print("=== Testing Provider Client Handling ===")
print()
test_provider_client_success()
print()
test_provider_client_retry()
print()
test_provider_client_bad_request()
print()
test_provider_client_server_error()
print()
print("=== Test script completed ===")