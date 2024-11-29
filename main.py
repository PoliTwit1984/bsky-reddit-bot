import subprocess
import time

def run_scripts():
	# Run reddit-main.py
	print("Starting reddit script...")
	reddit_result = subprocess.run(['python', 'reddit-main.py'], capture_output=True, text=True)
	print(reddit_result.stdout)



	# Run bluesky-main.py
	print("Starting bluesky script...")
	bluesky_result = subprocess.run(['python', 'bluesky-main.py'], capture_output=True, text=True)
	print(bluesky_result.stdout)

if __name__ == '__main__':
	run_scripts()