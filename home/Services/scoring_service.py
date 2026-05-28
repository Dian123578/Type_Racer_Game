import sys
import os
import json
import grpc
from concurrent import futures

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pb2.scoring_pb2 as scoring_pb2
import pb2.scoring_pb2_grpc as scoring_pb2_grpc

from logging_decorator import log_call

GAMMA = 1.5  # Score weighting factor for accuracy

class ScoringService(scoring_pb2_grpc.ScoringServiceServicer): # Basically the same as the other one
    def __init__(self):
        self.leaderboard = {1: [], 2: [], 3: []}  # leaderborad stores 3 levels

    def _calculate_accuracy(self, prompt, typed):
        sum = 0
        length = min(len(prompt), len(typed)) # avoiding indexing error if typed and prompt aren't the same length
        for i in range (length): #loop is fixed to length of typed since
            if prompt[i] == typed[i]: # if each character typed corresponds to prompt
                sum+=1
        accuracy = sum/len(prompt)
        return accuracy

    def _calculate_speed(self, typed, duration):
        if duration > 0: # to avoid divison by 0 error
            speed = len(typed) / duration 
        else: 
            speed = 0.0
        return speed

    def _calculate_score(self, accuracy, speed):
        return (accuracy ** GAMMA) * speed

    def _update_leaderboard(self, level, entry):
        self.leaderboard[level].append(entry)
        self.leaderboard[level].sort(key=lambda e: e.score, reverse=True) # update leaderboard for specific levels
        self.leaderboard[level] = self.leaderboard[level][:3]

    @log_call
    def SubmitResult(self, request, context): # calculates correct stuff
        accuracy = self._calculate_accuracy(request.prompt, request.typed_text)
        speed = self._calculate_speed(request.typed_text, request.duration)
        score = self._calculate_score(accuracy, speed)

        result = scoring_pb2.LeaderboardEntry(
            name=request.name,
            accuracy=accuracy,
            speed=speed,
            score=score,
            level=request.level
        )

        self._update_leaderboard(request.level, result) 

        return scoring_pb2.ScoreResponse(
            accuracy=accuracy,
            speed=speed,
            score=score
        )

    @log_call
    def GetLeaderboard(self, request, context): # returns entries in leaderboard
        all_entries = []
        for level in [1, 2, 3]:
            all_entries.extend(self.leaderboard[level])
        return scoring_pb2.Leaderboard(entries=all_entries)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    scoring_pb2_grpc.add_ScoringServiceServicer_to_server(ScoringService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Scoring Service running on port 50052...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
