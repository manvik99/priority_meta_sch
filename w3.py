import os
import time
import subprocess
import psutil
# Get the current process ID
pid = os.getpid()
priority = 4

# Specify the file where the PID will be written
file_path = "/home/manviknanda/uiuc/cs537/priority_meta_sch/test/w3.txt"

# Write the PID to the file
with open(file_path, "w") as file:
    file.write(str(pid))

# Define the directory for temporary files
directory = os.path.join(os.getcwd(), "process_updates")
os.makedirs(directory, exist_ok=True)

# Write "Start" state to a unique file
start_file = os.path.join(directory, f"process_{pid}_start.txt")
with open(start_file, "w") as f:
    f.write(f"{pid},{priority},S")

start_time = time.time()

# Simulate a workload
result = 1
M = 8000
for i in range(1, M):
    for j in range(1, M):
        result = result * 1

# Write "Remove" state to a unique file
end_file = os.path.join(directory, f"process_{pid}_end.txt")
with open(end_file, "w") as f:
    f.write(f"{pid},{priority},R")

print(f"PID:{pid},ProcessPriority:{priority},ProcessTime:{round(time.time() - start_time, 2)}s")
