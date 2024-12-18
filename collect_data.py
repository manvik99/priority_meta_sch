import os
import psutil
import time

# Directory where the process files are stored
process_files = ['/home/manviknanda/uiuc/cs537/priority_meta_sch/test/w0.txt',
                 '/home/manviknanda/uiuc/cs537/priority_meta_sch/test/w1.txt']

# List to store nice values
nice_values = []

# Timer variables
last_store_time = time.time()  # Record the time when we last stored values
start_time = time.time()  # Record the start time

def read_process_id_from_file(file_path):
    """
    Reads the process ID from the given file.
    Returns the process ID as an integer, or None if the file is empty or invalid.
    """
    try:
        with open(file_path, "r") as file:
            process_id = file.read().strip()
            if process_id.isdigit():
                return int(process_id)
            else:
                print(f"Invalid process ID in file: {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None

def get_process_nice_value(process_id):
    """
    Returns the nice value of the process with the given ID.
    Returns None if the process does not exist or cannot be accessed.
    """
    try:
        process = psutil.Process(process_id)
        return process.nice()
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"Error accessing process {process_id}: {e}")
    return None

def store_process_nice_values():
    """
    Periodically checks the process IDs from the w0, w1, and w2 files,
    stores their nice values in a list, and saves them to a file every 2 seconds.
    Exits after 20 seconds.
    """
    global last_store_time
    while True:
        # Check the process values every 0.2 seconds
        for file in process_files:
            process_id = read_process_id_from_file(file)
            if process_id:
                nice_value = get_process_nice_value(process_id)
                if nice_value is not None:
                    # Store the nice value along with the process ID
                    nice_values.append((process_id, nice_value))
                else:
                    print(f"Could not retrieve nice value for Process ID: {process_id}")
            else:
                print(f"Process ID could not be read from file: {file}")

        # Store values to a file every 2 seconds
        current_time = time.time()
        if current_time - last_store_time >= 2:  # 2 seconds have passed
            if nice_values:
                with open("stored_nice_values.txt", "a") as f:
                    for process_id, nice_value in nice_values:
                        f.write(f"Process ID: {process_id} - Nice Value: {nice_value}\n")
                nice_values.clear()  # Clear the list after saving
            last_store_time = current_time  # Update the time when we last stored values

        # Exit the loop after 15 seconds
        if current_time - start_time >= 40:
            print("40 seconds have passed, exiting the program.")
            break

        time.sleep(0.2)  # Sleep for 0.2 seconds before checking again

if __name__ == "__main__":
    store_process_nice_values()
