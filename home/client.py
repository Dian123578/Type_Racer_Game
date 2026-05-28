import grpc
import time

import pb2.prompt_pb2 as prompt_pb2
import pb2.prompt_pb2_grpc as prompt_pb2_grpc
import pb2.scoring_pb2 as scoring_pb2
import pb2.scoring_pb2_grpc as scoring_pb2_grpc
from pb2.scoring_pb2 import TypingResult, Empty

def get_prompt(prompt_stub, level): # gets prompt
    request = prompt_pb2.LevelRequest(level=level)
    return prompt_stub.GetPrompt(request).prompt

def display_leaderboard(scoring_stub): # displays leaderboard
    response = scoring_stub.GetLeaderboard(Empty())
    print("\nLeaderboard:")
    for entry in response.entries:
        print(f"{entry.name} (Level {entry.level}) - Score: {entry.score:.2f}")

def main():
    mode = None
    while mode not in ("simple", "advanced"): # loops if correct setting is not given
        mode = input("Select mode [simple/advanced]: ").strip().lower()

    prompt_port = "50051" if mode == "simple" else "50061" # ensures the correct port corresponding to simple or advanced
    scoring_port = "50052" if mode == "simple" else "50062"

    with grpc.insecure_channel(f"localhost:{prompt_port}") as prompt_channel, \
         grpc.insecure_channel(f"localhost:{scoring_port}") as scoring_channel:

        prompt_stub = prompt_pb2_grpc.PromptServiceStub(prompt_channel)
        scoring_stub = scoring_pb2_grpc.ScoringServiceStub(scoring_channel)

        while True:
            print("\nMenu:")
            print("1. Start a new challenge")
            print("2. View scoreboard")
            print("3. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                while True:
                    try:
                        level = int(input("Choose difficulty level [1/2/3]: ").strip())
                    except ValueError:
                        print("Invalid input.") # So many different ways this can error!
                        continue

                    prompt = get_prompt(prompt_stub, level)
                    if prompt == "Invalid Level":
                        print("Invalid difficulty level.")
                        continue
                    break  # valid level and prompt received

                print("\nPrompt:") # prints prompt
                print(prompt)

                name = input("Enter your name: ").strip()
                input("Press Enter to start typing...") 
                start_time = time.time() # to find duration
                typed = input()
                duration = time.time() - start_time

                result = TypingResult( # attributes of attempt
                    name=name,
                    prompt=prompt,
                    typed_text=typed,
                    duration=duration,
                    level=level
                )

                response = scoring_stub.SubmitResult(result)
                print(f"\nAccuracy: {response.accuracy:.2f}")
                print(f"Speed: {response.speed:.2f} chars/sec")
                print(f"Score: {response.score:.2f}")

            elif choice == "2":
                display_leaderboard(scoring_stub) # displays leaderboard

            elif choice == "3":
                print("Goodbye!") # ends program
                break

            else:
                print("Invalid choice, please try again.") # in case of invalid inputs

if __name__ == "__main__":
    main()
