## this python script will be loaded by main.py at the time specified in cron.json
## this script should contains logic that decide whether to run the task or not and return the task id if it should be run
## task id is a string defined in task-definition.json

def task_id():
    if should_run_task():
        return "example-task"
    return None

def should_run_task():
    return True