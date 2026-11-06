import subprocess
import time
import json

# Run Chrome to dump DOM of welcome screen
cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--screenshot=screenshots/test_integrated_welcome.png",
    "--window-size=1000,900",
    "scratch/integrated_test.html"
]
subprocess.run(cmd, check=True)
print("Captured screenshots/test_integrated_welcome.png")

# Mobile view
cmd_mob = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--screenshot=screenshots/test_integrated_welcome_mob.png",
    "--window-size=430,932",
    "scratch/integrated_test.html"
]
subprocess.run(cmd_mob, check=True)
print("Captured screenshots/test_integrated_welcome_mob.png")

