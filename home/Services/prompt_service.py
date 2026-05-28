'''
Stack exchange explained how to import from the parent directory 
https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import grpc
from concurrent import futures
import pb2.prompt_pb2 as prompt_pb2
import pb2.prompt_pb2_grpc as prompt_pb2_grpc


from logging_decorator import log_call

class PromptReturn(prompt_pb2_grpc.PromptServiceServicer): #prompts
  def __init__(self):
    self.prompts = {
      1: "it was the best of times it was the worst of times it was the age of wisdom it was the age of foolishness",
      2: "Somebody opens the door and gets shot and you think that of me I am the one who knocks",
      3: "40000 people used to live here. Now it's a ghost town..."
    }
    
  @log_call  
  def GetPrompt(self, request, context):
    level = request.level #method is executed when there is a grpc request
    prompt = self.prompts.get(level, "Invalid Level") #returns invalid level if level doesn't exist
    return prompt_pb2.PromptResponse(prompt=prompt)

def serve(): 
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    prompt_pb2_grpc.add_PromptServiceServicer_to_server(PromptReturn(), server)
    server.add_insecure_port("[::]:50051") # each server has to run on a seperate port
    server.start()
    print("Prompt Service running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
