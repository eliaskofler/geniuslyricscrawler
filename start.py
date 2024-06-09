import subprocess
import time

def run_nodejs_file(file_path):
    while True:
        try:
            process = subprocess.Popen(['node', file_path])
            process.wait()
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Restarting the Node.js file...")
            time.sleep(3)

if __name__ == "__main__":
    nodejs_file_path = "index.js"
    run_nodejs_file(nodejs_file_path)