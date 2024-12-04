import os
import time
import subprocess

# Get the current process ID
pid = os.getpid()
priority = 1

# Define the directory and file path
directory = "/Users/manvik/uiuc/cs537/priority_meta_scheduler/process_list"
file_path = os.path.join(directory, "ready_process.txt")

# Ensure the directory exists
os.makedirs(directory, exist_ok=True)

command = f'echo "{pid},{priority},S" > "{file_path}"'
subprocess.run(command, shell=True, check=True)

print(f"in dummy: Process ID: {pid}")
start_time = time.time()
result = 1
M = 7000
for i in range(1, M):
    for j in range(1,M):
        result = result*1

command = f'echo "{pid},{priority},R" > "{file_path}"'
subprocess.run(command, shell=True, check=True)
print(pid,':',time.time() - start_time)
