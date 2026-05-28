from functools import wraps
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") #This line was sourced from chatgpt. The prompt was the rest of the code.

def log_call(func):
    @wraps(func)
    def wrapper(self, request, context, *args, **kwargs):
        logging.info(f"[{datetime.now()}] RPC call: {func.__name__} | request: {request}")
        response = func(self, request, context, *args, **kwargs)
        logging.info(f"Response: {response}")
        return response
    return wrapper
