import unittest
import grpc
import collections.abc

import pb2.prompt_pb2 as prompt_pb2
import pb2.prompt_pb2_grpc as prompt_pb2_grpc
import pb2.scoring_pb2 as scoring_pb2
import pb2.scoring_pb2_grpc as scoring_pb2_grpc
from pb2.scoring_pb2 import TypingResult, Empty

class TestPrompt(unittest.TestCase):
    def setUp(self):
        self.channel = grpc.insecure_channel("localhost:50061")  # advanced prompt
        self.stub = prompt_pb2_grpc.PromptServiceStub(self.channel)

    def tearDown(self):
        self.channel.close()

    def test_valid_level(self):
        for level in [1, 2, 3]:
            response = self.stub.GetPrompt(prompt_pb2.LevelRequest(level=level))
            self.assertIsInstance(response.prompt, str)
            self.assertNotEqual(response.prompt, "")
            self.assertNotEqual(response.prompt, "Invalid Level")

    def test_invalid_level(self):
        response = self.stub.GetPrompt(prompt_pb2.LevelRequest(level=99))
        self.assertEqual(response.prompt, "Invalid Level")

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.channel = grpc.insecure_channel("localhost:50062")  # advanced scoring
        self.stub = scoring_pb2_grpc.ScoringServiceStub(self.channel)

    def teardown(self):
        self.channel.close()

    def test_exactmatch(self):
        prompt = "The quick brown fox jumps over the lazy dog"
        result = TypingResult(
            name="Alice",
            prompt=prompt,
            typed_text=prompt,
            duration=10.0,
            level=2
        )
        response = self.stub.SubmitResult(result)
        self.assertAlmostEqual(response.accuracy, 1.0, delta=0.01)
        self.assertGreater(response.score, 0)

    def test_submit_result_partial_match(self):
        prompt = "Hello world"
        typed = TypingResult(
            name="Bob",
            prompt=prompt,
            typed_text="Hella wurld",
            duration=5.0,
            level=1
        )
        response = self.stub.SubmitResult(typed)
        self.assertLess(response.accuracy, 1.0)
        self.assertGreaterEqual(response.score, 0)

    def test_empty_input(self):
        prompt = "Something"
        result = TypingResult(
            name="Eve",
            prompt=prompt,
            typed_text="",
            duration=5.0,
            level=1
        )
        response = self.stub.SubmitResult(result)
        self.assertEqual(response.accuracy, 0.0)
        self.assertEqual(response.score, 0.0)

    def test_leaderboard(self): # This test in particular was mostly chatgpt as i received errors for seemingly no reason. Chatgpt suggested the collections.abc module and the following code.
        response = self.stub.GetLeaderboard(Empty())
        self.assertIsInstance(response.entries, collections.abc.Sequence)
        for entry in response.entries:
            self.assertIsNotNone(entry.name)
            self.assertGreaterEqual(entry.score, 0)


if __name__ == "__main__":
    unittest.main()
