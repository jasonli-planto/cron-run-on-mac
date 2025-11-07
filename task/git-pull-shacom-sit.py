## this python script defines the logic of the task
## it will be run im case of the task id is returned by the cron-event script

import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    logger.info("Running example task")
    repo_dir = os.path.expanduser("~/work/shacom-backend")
    # Pull the latest changes from origin/sit into local sit branch
    # Then run the "./build-scripts/build-container-only.sh" script with "iads" argument
    # Then run the "apptest" command
    # Find the latest build container image file which pattern is "be-iads-.*\.tar\.gz" in the repo_dir
    # Then run the "scp-sit <image-file-path>" script to upload the image to the SIT server
    return True