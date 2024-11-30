import subprocess
import time
import logging
import sys
import os

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_name):
    """Run a Python script and handle its output."""
    logger.info(f"Starting {script_name}...")
    
    try:
        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True
        )
        
        # Log stdout if there is any
        if result.stdout:
            for line in result.stdout.splitlines():
                logger.info(f"{script_name} output: {line}")
        
        # Log stderr if there is any
        if result.stderr:
            for line in result.stderr.splitlines():
                logger.error(f"{script_name} error: {line}")
        
        if result.returncode == 0:
            logger.info(f"{script_name} completed successfully")
            return True
        else:
            logger.error(f"{script_name} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"Error running {script_name}: {str(e)}")
        return False

def run_scripts():
    """Run both scripts in sequence."""
    try:
        # Run reddit-main.py
        if not run_script('reddit-main.py'):
            return False

        # Wait a bit to ensure files are written
        time.sleep(5)

        # Run bluesky-main.py
        if not run_script('bluesky-main.py'):
            return False

        return True

    except Exception as e:
        logger.error(f"Error in run_scripts: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_scripts()
    if not success:
        logger.error("Script execution failed")
        sys.exit(1)
    else:
        logger.info("All scripts completed successfully")
