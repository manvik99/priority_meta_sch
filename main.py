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
    def __init__(self, directory):
       self.directory = directory

    def on_modified(self, event):
        if event.src_path.endswith(".txt"):
            threading.Thread(target=self.process_file, args=(event.src_path,)).start()

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
                logging.info("Successfully deleted process %d from the list.", process_id)
            else:
                logging.warning("Process %d not found in the list for deletion.", process_id)


    def process_file(self, file_path):
        # READ FROM THE FILE
        try:
            with open(file_path, "r") as file:
                process_id, process_priority, process_state = file.read().strip().split(",")
        except:
            logging.error("Invalid Process Command in file: %s", file_path)
            return

        process_id = int(process_id)
        process_priority = int(process_priority)
        process = Process(process_id, process_priority, process_state) # Create a Process Object

        process_psutil = psutil.Process(process_id)
        value = f'Process Priorty: {process_priority} ' +'Niceness of ' + f'{process_id}: ' +str(process_psutil.nice())
        logging.info(value)
        if process_priority == 1:
            if process_state == 'S':
                with process_list_lock:
                    if process in process_list:
                        return
                    process_list.append(process)
                logging.info('scheduling process %d ; priority: %d', process_id, process_priority)
                self.update_nice_schedule_process(process_id, -20) #Update Process Priority
                # Decrease priority for all other process
                logging.info('increasing niceness of all other processes....')
                with process_list_lock:
                    for process in process_list:
                        if process.process_id != process_id:
                            self.update_nice_schedule_process(process.process_id, 19)

            if process_state == 'R':
                # Remove the process.
                self.delete_process(process_id)
                # Update the priority for all other Processes
                logging.info('restoring niceness of all other processes....')
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
                    if process in process_list:
                        return
                    process_list.append(process)
                logging.info('scheduling process %d ; priority: %d', process_id, process_priority)
                if process.process_priority == 2:
                    self.update_nice_schedule_process(process.process_id, -10)
                elif process.process_priority == 3:
                    self.update_nice_schedule_process(process.process_id, 0)
                else:
                    self.update_nice_schedule_process(process.process_id, 10)

            if process_state == 'R':
                # Remove the process.
                self.delete_process(process_id)
        os.remove(file_path)
if __name__ == "__main__":
    logging.basicConfig(filename="main.log", level=logging.INFO)
    logging.info("\n\n#######################################################")
    updates_directory = os.path.join(os.getcwd(), "process_updates")
    os.makedirs(updates_directory, exist_ok=True)

    # Create the event handler and observer
    event_handler = WriteHandler(updates_directory)
    observer = Observer()
    observer.schedule(event_handler, updates_directory, recursive=False)
    observer.start()

    # Keep the observer running
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
