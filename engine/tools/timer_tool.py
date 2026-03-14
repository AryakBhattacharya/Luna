import time

class TimerTool:

    @staticmethod
    def run(seconds: int):

        #print(f"\n[Timer started for {seconds} seconds]\n")

        time.sleep(seconds)

        return "Time's up!"