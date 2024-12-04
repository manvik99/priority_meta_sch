import sys
import logging
import os
import threading
import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import deque
logger = logging.getLogger(__name__)

# Define the Process Class
process_list = deque()
process_list_lock = threading.Lock()

class Process:
    def __init__(self, process_id, process_priority, process_state):
        self.process_id = process_id
        self.process_priority = process_priority
        self.process_state = process_state
        # self.priority_list_lock = threading.Lock()

class WriteHandler(FileSystemEventHandler):
    def __init__(self, ready_process_file):
        self.ready_process_file = ready_process_file

    def on_modified(self, event):
        if event.src_path == self.ready_process_file:
            threading.Thread(target=self.on_modified_thread, args=(event,)).start()

    def update_nice_schedule_process(self, process_id, new_nice_value):
        try:
            process = psutil.Process(process_id)
            process.nice(new_nice_value)
        except psutil.NoSuchProcess:
            logging.info(f"No process found with PID {process_id}.")
        except psutil.AccessDenied:
            logging.info(f"Access denied to change nice value of process {process_id}.")
        except ValueError as e:
            logging.info(f"Invalid nice value: {e}")

    def delete_process(self, process_id):
        with process_list_lock:
            process_to_delete = None
            for process in process_list:
                if process.process_id == process_id:
                    process_to_delete = process
                    break
            if process_to_delete:
                process_list.remove(process_to_delete)

    def on_modified_thread(self, event):
        logging.info("Thread on_modified_thread: starting")

        # READ FROM THE FILE
        file = open(self.ready_process_file, "r+")
        process_id, process_priority, process_state = file.read().strip().split(",")
        process_id = int(process_id)
        process_priority = int(process_priority)
        process = Process(process_id, process_priority, process_state) # Create a Process Object

        if process_priority == 1:
            if process_state == 'S':
                with process_list_lock:
                    process_list.append(process)
                self.update_nice_schedule_process(process_id, -20) #Update Process Priority
                # Decrease priority for all other process
                with process_list_lock:
                    for process in process_list:
                        self.update_nice_schedule_process(process.process_id, 19)

            if process_state == 'R':
                # Remove the process.
                self.delete_process(process_id)
                # Update the priority for all other Processes
                with process_list_lock:
                    for process in process_list:
                        if process.process_priority == 2:
                            self.update_nice_schedule_process(process.process_id, -10)
                        elif process.process_priority == 3:
                            self.update_nice_schedule_process(process.process_id, 0)
                        else:
                            self.update_nice_schedule_process(process.process_id, 10)

        else:
            if process_state == 'S':
                with process_list_lock:
                    process_list.append(process)
                if process.process_priority == 2:
                    self.update_nice_schedule_process(process.process_id, -10)
                elif process.process_priority == 3:
                    self.update_nice_schedule_process(process.process_id, 0)
                else:
                    self.update_nice_schedule_process(process.process_id, 10)

            if process_state == 'R':
                # Remove the process.
                self.delete_process(process_id)
                print('in delete the process. ')

        for pro in process_list:
            print(pro.process_id,pro.process_state, os.getpriority(os.PRIO_PROCESS, pro.process_id) ,end=" ")
        print('#######')

if __name__ == "__main__":
    logging.basicConfig(filename='main.log', level=logging.INFO)
    ready_process_file = sys.argv[1] if len(sys.argv) > 1 else '/Users/manvik/uiuc/cs537/priority_meta_scheduler/process_list/ready_process.txt'
    ready_process_file_dir = os.path.dirname(ready_process_file)

    # Create the event_handler
    event_handler = WriteHandler(ready_process_file)
    observer = Observer()
    observer.schedule(event_handler, ready_process_file_dir, recursive=False)
    observer.start() # Start the observer

    # Continue the main thread.
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
