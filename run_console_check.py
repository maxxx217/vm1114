import subprocess

cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--dump-dom",
    "scratch/integrated_test.html"
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("DOM Length:", len(res.stdout))
print("zy-w count in DOM:", res.stdout.count("zy-w"))

cmd2 = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless=new",
    "--disable-gpu",
    "--screenshot=screenshots/test_welcome_with_zy.png",
    "--window-size=1000,900",
    "scratch/integrated_test.html"
]
subprocess.run(cmd2, check=True)
print("Saved screenshots/test_welcome_with_zy.png")
