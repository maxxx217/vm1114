import subprocess
import os

base_dir = os.path.abspath('.')
file_url = f"file://{base_dir}/scratch/integrated_test.html"

# Run Chrome with JS to click toggle button and take screenshot
js_toggle = """
document.getElementById('btn-zhuyin-toggle').click();
"""
cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=2000",
    "--screenshot=screenshots/test_toggle_off_desk.png",
    "--window-size=1000,950",
    f"{file_url}?view=screen-game&pet=dog&q=0"
]

# We can simulate toggle by testing with localStorage or appending JS
