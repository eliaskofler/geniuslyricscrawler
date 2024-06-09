import subprocess
import psutil
import time
import threading

def run_nodejs_file(file_path):
    process = None
    try:
        process = subprocess.Popen(['node', file_path])
        process.wait()
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Restarting the Node.js file...")
        time.sleep(3)

def monitor_memory_usage(process, nodejs_file_path):
    while True:
        # Get system memory usage
        memory_info = psutil.virtual_memory()
        # Convert from bytes to gigabytes
        memory_usage_gb = memory_info.used / (1024 ** 3)
        
        print(f"Memory usage: {memory_usage_gb:.2f} GB")
        
        # Check if memory usage exceeds 6.5 GB
        if memory_usage_gb > 3.5:
            print("Memory usage exceeds 6.5 GB. Restarting Node.js process...")
            # Terminate the Node.js process
            if process:
                process.terminate()
                # Wait for the process to terminate
                process.wait()
            else:
                print("No Node.js process found to terminate.")
            
            # Restart the Node.js file
            print("Restarting Node.js...")
            run_nodejs_file(nodejs_file_path)
        
        else:
            print("\n\n\n\n\n\n\n\n\nMemory usage is within limits.")
        
        time.sleep(60)  # Check memory usage every 60 seconds

if __name__ == "__main__":
    nodejs_file_path = "index.js"
    
    # Start monitoring memory usage in a separate thread
    process = None  # Initialize process variable
    memory_monitor_thread = threading.Thread(target=monitor_memory_usage, args=(process, nodejs_file_path))
    memory_monitor_thread.start()
    
    # Run the Node.js file
    run_nodejs_file(nodejs_file_path)