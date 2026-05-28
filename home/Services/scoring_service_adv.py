import os
import sys
import json
import grpc
from concurrent import futures

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pb2.scoring_pb2 as scoring_pb2
import pb2.scoring_pb2_grpc as scoring_pb2_grpc

from logging_decorator import log_call

GAMMA = 1.5
LEADERBOARD_FILE = "leaderboard.json"

class ScoringServiceAdvanced(scoring_pb2_grpc.ScoringServiceServicer): #mostly the same as simple file in terms of calculations
    def __init__(self):
        self.leaderboard = {1: [], 2: [], 3: []} # for each level
        self._load_leaderboard()

    def _calculate_accuracy(self, prompt, typed):
        correct = sum(1 for p, t in zip(prompt, typed) if p == t)
        return correct / len(prompt) if len(prompt) > 0 else 0.0

    def _calculate_speed(self, typed, duration):
        return len(typed) / duration if duration > 0 else 0.0

    def _calculate_score(self, accuracy, speed):
        return (accuracy ** GAMMA) * speed

    def _load_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE): # load entries from leaderboard if it exists
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
                for level_str, entries in data.items():
                    level = int(level_str)
                    self.leaderboard[level] = [
                        scoring_pb2.LeaderboardEntry(
                            name=e["name"],
                            accuracy=e["accuracy"],
                            speed=e["speed"],
                            score=e["score"],
                            level=e["level"]
                        ) for e in entries
                    ]

    def _save_leaderboard(self): # saves new leaderboard to json file, overwriting old file
        data = {
            str(level): [
                {
                    "name": e.name,
                    "accuracy": e.accuracy,
                    "speed": e.speed,
                    "score": e.score,
                    "level": e.level
                } for e in entries
            ] for level, entries in self.leaderboard.items()
        }
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _update_leaderboard(self, level, entry): 
        self.leaderboard[level].append(entry) # adds new entry 
        self.leaderboard[level].sort(key=lambda e: e.score, reverse=True)
        self.leaderboard[level] = self.leaderboard[level][:3] # keeps top 3 entries
        self._save_leaderboard()

    @log_call
    def SubmitResult(self, request, context): # calculations, same as simple file
        accuracy = self._calculate_accuracy(request.prompt, request.typed_text)
        speed = self._calculate_speed(request.typed_text, request.duration)
        score = self._calculate_score(accuracy, speed)

        entry = scoring_pb2.LeaderboardEntry(
            name=request.name,
            accuracy=accuracy,
            speed=speed,
            score=score,
            level=request.level
        )

        self._update_leaderboard(request.level, entry)

        return scoring_pb2.ScoreResponse(
            accuracy=accuracy,
            speed=speed,
            score=score
        )

    @log_call
    def GetLeaderboard(self, request, context): # gets leaderboard
        all_entries = []
        for level_entries in self.leaderboard.values():
            all_entries.extend(level_entries)
        return scoring_pb2.Leaderboard(entries=all_entries)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    scoring_pb2_grpc.add_ScoringServiceServicer_to_server(ScoringServiceAdvanced(), server)
    server.add_insecure_port("[::]:50062")  # Advanced scoring uses port 50053
    print("Advanced Scoring Service running on port 50062...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()


