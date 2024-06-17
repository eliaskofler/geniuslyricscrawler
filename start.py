import subprocess
import time

def run_nodejs_file(file_path):
    try:
        process = subprocess.Popen(['node', file_path])
        print("Node.js process started.")
        time.sleep(600)
        print("Shutting down Node.js process...")
        process.kill()
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Restarting the Node.js file...")
        time.sleep(3)

if __name__ == "__main__":
    nodejs_file_path = "index.js"
    
    while True:
        run_nodejs_file(nodejs_file_path)
        print("Waiting for 10 seconds before restarting...")
        time.sleep(10)