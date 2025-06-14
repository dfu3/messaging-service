import uuid
import random
import time
from abc import ABC, abstractmethod


class ProviderError(Exception):
    def __init__(self, status_code: int, message: str = "Provider error"):
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {message}")


class Provider(ABC):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def send_with_retry(self, message_data: dict, max_retries: int = 3, retry_delay: float = 2.0) -> str | None:
        retries = 0

        while retries <= max_retries:
            try:
                return self._send(message_data)
            except ProviderError as e:
                if e.status_code == 429:
                    retries += 1
                    if retries > max_retries:
                        print("Max retries reached. Giving up.")
                        return None
                    print(f"Retry {retries}/{max_retries} due to rate limiting. Waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                elif 400:
                    print(f"Bad Request, adjust implementation: {e}. Not retrying.")
                    return None
                elif 401:
                    print(f"Unauthorized, check creds: {e}. Not retrying.")
                    return None
                elif 500 <= e.status_code < 600:
                    print(f"Server error: {e}. Not retrying.")
                    return None
                else:
                    print(f"Unexpected error: {e}. Not retrying.")
                    return None

    @abstractmethod
    def _send(self, message_data: dict) -> str:
        pass


class SmsProvider(Provider):
    def _send(self, message_data: dict) -> str:
        print(f"[SMS] Sending message to endpoint: {self.endpoint}")
        chance = random.random()

        if chance < 0.6:
            print("SMS sent successfully")
            return f"sms-{uuid.uuid4()}"
        elif chance < 0.7:
            raise ProviderError(400, "SMS Bad Request to client")
        elif chance < 0.8:
            raise ProviderError(401, "SMS Not Authorized with client")
        elif chance < 0.9:
            raise ProviderError(429, "SMS rate limited")
        else:
            raise ProviderError(500, "SMS provider internal error")


class EmailProvider(Provider):
    def _send(self, message_data: dict) -> str:
        print(f"[Email] Sending message to endpoint: {self.endpoint}")
        chance = random.random()

        if chance < 0.85:
            print("Email sent successfully")
            return f"email-{uuid.uuid4()}"
        elif chance < 0.95:
            raise ProviderError(429, "Email rate limited")
        else:
            raise ProviderError(502, "Email provider bad gateway")
