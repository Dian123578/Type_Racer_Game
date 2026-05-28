TO RUN:

1. In seperate terminals, run the following:
    python3 Services/prompt_service.py
    python3 Services/prompt_service_adv.py
    python3 Services/scoring_service.py
    python3 Services/scoring_service_adv.py  
   This will ensure all the relevant servers are running. Although you won't be using all of them,
   the client will give you the option of selecting advanced or simple.

2. In a seperate terminal, run the following:
    python3 client.py

3. Follow the instructions and enjoy!



NOTE: The leaderboard stores a maximum of 9 entries, 3 for each level.




FOR UNIT TESTS:
   Run the following:
    python3 Services/prompt_service.py
    python3 Services/prompt_service_adv.py
    python3 Services/scoring_service.py
    python3 Services/scoring_service_adv.py
    python3 testing.py
   The relevant output will be displayed when running the testing.py file.
   
