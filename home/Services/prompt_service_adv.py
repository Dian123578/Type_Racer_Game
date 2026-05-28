import sys
import os
import random
import re      #learned re module from https://docs.python.org/3/library/re.html
from concurrent import futures

import grpc

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pb2.prompt_pb2 as prompt_pb2
import pb2.prompt_pb2_grpc as prompt_pb2_grpc

from logging_decorator import log_call
from nltk_helper import get_random_sentence  # your helper function


class PromptReturnAdv(prompt_pb2_grpc.PromptServiceServicer):
    def __init__(self):
        # Precompile regex patterns
        self.patterns = {
            1: re.compile(r'^[a-z ]+$'),  # lowercase and spaces only
            2: re.compile(r'^[a-zA-Z0-9 ]+$'),  # letters (capital, lowercase), digits, spaces only
            3: re.compile(r'^[a-zA-Z0-9 .,?!\'"-]+$')  # letters(capital, lowercase), digits, spaces, punctuation
        }

    def _valid_level_1(self, text):
        return bool(self.patterns[1].match(text)) and (30 <= len(text) <= 120) #checking text length

    def _valid_level_2(self, text): 
        if not (30 <= len(text) <= 120): # checking text length and capitalisation or numbers for randomly generated prompts
            return False
        if not self.patterns[2].match(text):
            return False
        has_upper = any(c.isupper() for c in text)
        has_digit = any(c.isdigit() for c in text)
        return has_upper or has_digit # or logic is necessary as prompt only needs one of either to be valid.

    def _valid_level_3(self, text): # checking for text length, capitals, digits, punctuation
        if not (30 <= len(text) <= 120):
            return False
        if not self.patterns[3].match(text):
            return False
        has_upper = any(c.isupper() for c in text)
        has_digit = any(c.isdigit() for c in text)
        has_punct = any(c in ".,?!'-\"" for c in text)
        return has_upper and has_digit and has_punct # and logic is necessary as prompt needs all three.

    def _clean_level_1(self, text): #this function ensures that text satisfies level 1 requirements
        text = text.lower()
        return ''.join(c for c in text if c.isalpha() or c == ' ') 

    def _clean_level_2(self, text): # this function ensures that if text doesn't satisfy level 2 requirements, a number is added
        text = ''.join(c for c in text if c.isalnum() or c == ' ')
        if not any(c.isupper() for c in text) and not any(c.isdigit() for c in text):
            text += ' 1'  # ensure digit if missing uppercase/digit
        return text

    def _clean_level_3(self, text):  # this function ensures that if text doesn't satisfy level 3 requirements, text is added
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,?!'-\"")
        text = ''.join(c for c in text if c in allowed)
        if not any(c.isupper() for c in text):
            text = 'A ' + text  # add uppercase
        if not any(c.isdigit() for c in text):
            text += ' 2'  # add digit
        if not any(c in ".,?!'-\"" for c in text):
            text += '.'  # add punctuation
        return text

    def _generate_prompt(self, level): # generates random prompts, cleans them, returns cleaned prompt
        attempts = 0
        while attempts < 100:
            sentence = get_random_sentence()
            if level == 1:
                cleaned = self._clean_level_1(sentence)
                if self._valid_level_1(cleaned):
                    return cleaned
            elif level == 2:
                cleaned = self._clean_level_2(sentence)
                if self._valid_level_2(cleaned):
                    return cleaned
            elif level == 3:
                cleaned = self._clean_level_3(sentence)
                if self._valid_level_3(cleaned):
                    return cleaned
            attempts += 1

        # fallback prompts
        fallback = { # in case it takes over 100 attempts, program reverts back to simple prompts
            1: "it was the best of times it was the worst of times it was the age of wisdom",
            2: "Somebody opens the door and gets shot and you think that of me I am the one who knocks",
            3: "40000 people used to live here. Now it's a ghost town..."
        }
        return fallback.get(level, "Invalid Level")

    @log_call
    def GetPrompt(self, request, context): # generates prompt
        level = request.level
        if level not in (1, 2, 3):
            return prompt_pb2.PromptResponse(prompt="Invalid Level")
        prompt = self._generate_prompt(level)
        return prompt_pb2.PromptResponse(prompt=prompt)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) 
    prompt_pb2_grpc.add_PromptServiceServicer_to_server(PromptReturnAdv(), server)
    server.add_insecure_port("[::]:50061")
    server.start()
    print("Advanced Prompt Service running on port 50061...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
