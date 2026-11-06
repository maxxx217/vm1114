import subprocess
import os

base_dir = os.path.abspath('.')
file_url = f"file://{base_dir}/scratch/integrated_test.html"

# Select screen
cmd_sel = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/test_screen_select.png",
    "--window-size=1000,950",
    f"{file_url}?view=screen-select"
]
subprocess.run(cmd_sel, check=True)
print("Saved screenshots/test_screen_select.png")

# Cert screen
cmd_cert = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/test_screen_cert.png",
    "--window-size=1000,1050",
    f"{file_url}?view=screen-cert&pet=dog"
]
subprocess.run(cmd_cert, check=True)
print("Saved screenshots/test_screen_cert.png")

