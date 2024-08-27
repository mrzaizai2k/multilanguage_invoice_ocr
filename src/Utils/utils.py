import sys
sys.path.append("")

from functools import wraps
import time
from datetime import datetime
import os
import psutil
import yaml
import shutil
import subprocess

from dotenv import load_dotenv
load_dotenv()


def convert_ms_to_hms(ms):
    seconds = ms / 1000
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    seconds = round(seconds, 2)
    
    return f"{int(hours)}:{int(minutes):02d}:{seconds:05.2f}"

def measure_memory_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info()[0]
        rt = func(*args, **kwargs)
        mem_end = process.memory_info()[0]
        diff_MB = (mem_end - mem_start) / (1024 * 1024)  # Convert bytes to megabytes
        print('Memory usage of %s: %.2f MB' % (func.__name__, diff_MB))
        return rt
    return wrapper


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        time_delta = convert_ms_to_hms(total_time*1000)

        print(f'{func.__name__.title()} Took {time_delta}')
        return result
    return timeit_wrapper

def is_file(path:str):
    return '.' in path

def check_path(path):
    # Extract the last element from the path
    last_element = os.path.basename(path)
    if is_file(last_element):
        # If it's a file, get the directory part of the path
        folder_path = os.path.dirname(path)

        # Check if the directory exists, create it if not
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Create new folder path: {folder_path}")
        return path
    else:
        # If it's not a file, it's a directory path
        # Check if the directory exists, create it if not
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Create new path: {path}")
        return path

def read_config(path = 'config/config.yaml'):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def is_gpu_available():
    # FIXME we are assuming nvidia-smi is installed on systems with GPU(s)
    if shutil.which('nvidia-smi') is None:
        return False

    try:
        command = "nvidia-smi --list-gpus | wc -l"
        gpus = subprocess.check_output(command, shell=True, text='utf8')
        return int(gpus) > 0

    except Exception:
        return False
    
def run_command( command, stdout_callback=None, stderr_callback=None):
    """
    Run a system command and optionally process its output.
    
    Args:
        command (list): The command to run as a list of strings.
        stdout_callback (callable, optional): Function to process stdout lines.
        stderr_callback (callable, optional): Function to process stderr lines.
    
    Returns:
        int: The return code of the command.
    """
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )

    for stdout_line in process.stdout:
        if stdout_callback:
            stdout_callback(stdout_line.strip())
        print(stdout_line.strip())

    for stderr_line in process.stderr:
        if stderr_callback:
            stderr_callback(stderr_line.strip())
        print(stderr_line.strip(), file=sys.stderr)

    process.wait()

    return 

def progress_callback(progress, task_id):
    def _func(line, **kwargs):
        if line.startswith('progress:'):
            completed, total = map(int, line[len('progress:'):].strip().split('/'))
            total = total if total >= 0 else None
            progress.update(task_id, completed=completed, total=total)

        print(line, end='', **kwargs)
    return _func
    
if __name__ == "__main__":
    print("Has GPU?", is_gpu_available())