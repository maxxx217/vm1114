import subprocess
import os

base_dir = os.path.abspath('.')
file_url = f"file://{base_dir}/scratch/integrated_test.html"

# 1. Capture game screen (question)
cmd_game = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    f"--screenshot=screenshots/test_game_q_desk.png",
    "--window-size=1000,950",
    f"{file_url}?view=screen-game&pet=dog&q=0"
]
subprocess.run(cmd_game, check=True)
print("Saved screenshots/test_game_q_desk.png")

# 2. Capture game screen flipped (explanation)
cmd_flip = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    f"--screenshot=screenshots/test_game_flip_desk.png",
    "--window-size=1000,950",
    f"{file_url}?view=screen-game&pet=dog&q=0&flip=1"
]
subprocess.run(cmd_flip, check=True)
print("Saved screenshots/test_game_flip_desk.png")

# 3. Mobile question
cmd_mob = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    f"--screenshot=screenshots/test_game_q_mob.png",
    "--window-size=430,932",
    f"{file_url}?view=screen-game&pet=dog&q=0"
]
subprocess.run(cmd_mob, check=True)
print("Saved screenshots/test_game_q_mob.png")

# 4. Mobile flipped
cmd_mob_flip = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    f"--screenshot=screenshots/test_game_flip_mob.png",
    "--window-size=430,932",
    f"{file_url}?view=screen-game&pet=dog&q=0&flip=1"
]
subprocess.run(cmd_mob_flip, check=True)
print("Saved screenshots/test_game_flip_mob.png")
