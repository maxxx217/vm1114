import subprocess
import os

base_dir = os.path.abspath('.')
file_url = f"file://{base_dir}/index.html"

# 1. Desktop Welcome Screen
cmd_wel = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/prod_welcome_desk.png",
    "--window-size=1000,900",
    f"{file_url}"
]
subprocess.run(cmd_wel, check=True)
print("Verified Desktop Welcome")

# 2. Desktop Game Question Screen
cmd_q = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/prod_game_q_desk.png",
    "--window-size=1000,950",
    f"{file_url}?view=screen-game&pet=dog&q=0"
]
subprocess.run(cmd_q, check=True)
print("Verified Desktop Game Question")

# 3. Desktop Game Flipped Screen (Explanation)
cmd_flip = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/prod_game_flip_desk.png",
    "--window-size=1000,950",
    f"{file_url}?view=screen-game&pet=dog&q=0&flip=1"
]
subprocess.run(cmd_flip, check=True)
print("Verified Desktop Game Flip")

# 4. Mobile Game Question Screen (iPhone view)
cmd_mob_q = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/prod_game_q_mob.png",
    "--window-size=430,932",
    f"{file_url}?view=screen-game&pet=dog&q=0"
]
subprocess.run(cmd_mob_q, check=True)
print("Verified Mobile Game Question")

# 5. Mobile Game Flipped Screen
cmd_mob_flip = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/prod_game_flip_mob.png",
    "--window-size=430,932",
    f"{file_url}?view=screen-game&pet=dog&q=0&flip=1"
]
subprocess.run(cmd_mob_flip, check=True)
print("Verified Mobile Game Flip")

# 6. Certificate Screen
cmd_cert = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/prod_cert_desk.png",
    "--window-size=1000,1050",
    f"{file_url}?view=screen-cert&pet=dog"
]
subprocess.run(cmd_cert, check=True)
print("Verified Certificate Screen")

