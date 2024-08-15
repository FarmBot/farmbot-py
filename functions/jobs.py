"""
JobHandling class.
"""

# └── functions/jobs.py
#     ├── [BROKER] get_job()
#     ├── [BROKER] set_job()
#     └── [BROKER] complete_job()

from .imports import *
from .broker import BrokerConnect

from .information import Information
from .resources import Resources

class JobHandling():
    def __init__(self, token):
        self.token = token
        self.broker = BrokerConnect(token)
        self.info = Information(token)
        self.resource = Resources(token)

    def get_job(self, job_str):
        # Get all or single job by name
        status_data = self.info.read_status()

        if job_str is None:
            jobs = status_data["jobs"]
        else:
            jobs = status_data["jobs"][job_str]

        # Return job as json object: job[""]
        return jobs

    def set_job(self, job_str, status_message, value):
        lua_code = f"""
            local job_name = "{job_str}"
            set_job(job_name)

            -- Update the job\'s status and percent:
            set_job(job_name, {{
            status = "{status_message}",
            percent = {value}
            }})
        """

        self.resource.lua(lua_code)

    def complete_job(self, job_str):
        lua_code = f"""
            complete_job("{job_str}")
        """

        self.resource.lua(lua_code)
