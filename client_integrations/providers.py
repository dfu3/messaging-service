import time
from abc import ABC, abstractmethod
import requests
from requests.exceptions import HTTPError

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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
                        logging.info("Max retries reached. Giving up.")
                        return None
                    logging.info(f"Retry {retries}/{max_retries} due to rate limiting. Waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                elif 400:
                    logging.info(f"Bad Request, adjust implementation: {e}. Not retrying.")
                    return None
                elif 401:
                    logging.info(f"Unauthorized, check creds: {e}. Not retrying.")
                    return None
                elif 500 <= e.status_code < 600:
                    logging.info(f"Server error: {e}. Not retrying.")
                    return None

    @abstractmethod
    def _send(self, message_data: dict) -> str:
        pass


class SmsProvider(Provider):
    def _send(self, message_data: dict) -> str:

        logging.info(f"[SMS] Sending message to endpoint: {self.endpoint}")
        try:
            resp = requests.post(self.endpoint, json=message_data)
            resp.raise_for_status()
        except HTTPError as e:
            raise ProviderError(e.response.status_code, "SMS HTTP Error")
        except Exception as e:
            logging.info(f"Unexpected SMS Client error: {e}. Not retrying.")
            return None
        else:
            return resp.json()['id'] 


class EmailProvider(Provider):
    def _send(self, message_data: dict) -> str:
        
        logging.info(f"[Email] Sending message to endpoint: {self.endpoint}")
        try:
            resp = requests.post(self.endpoint, json=message_data)
            resp.raise_for_status()
        except HTTPError as e:
            raise ProviderError(e.response.status_code, "Email HTTP Error")
        except Exception as e:
            logging.info(f"Unexpected Email Client error: {e}. Not retrying.")
            return None
        else:
            return resp.json()['id'] 
