"""
JobHandling class.
"""

# └── functions/jobs.py
#     ├── [BROKER] get_job()
#     ├── [BROKER] set_job()
#     └── [BROKER] complete_job()

from .broker import BrokerConnect

from .information import Information
from .resources import Resources

class JobHandling():
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)
        self.resource = Resources(state)

    def get_job(self, job_str):
        """Retrieves the status or details of the specified job."""

        status_data = self.info.read_status()

        if job_str is None:
            jobs = status_data["jobs"]
        else:
            jobs = status_data["jobs"][job_str]

        self.broker.state.print_status(endpoint_json=jobs)
        return jobs

    def set_job(self, job_str, status_message, value):
        """Initiates or modifies job with given parameters."""

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

        self.broker.state.print_status(description=f"Marked job {job_str} as {value}% complete.")
        return

    def complete_job(self, job_str):
        """Marks job as completed and triggers any associated actions."""

        lua_code = f"""
            complete_job("{job_str}")
        """

        self.resource.lua(lua_code)

        self.broker.state.print_status(description=f"Marked job {job_str} as `complete`.")
        return
