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
    """Job handling class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)
        self.resource = Resources(state)
        self.state = state

    def get_job(self, job_str=None):
        """Retrieves the status or details of the specified job."""
        self.state.print_status(description="Retrieving job data...")

        status_data = self.info.read_status()

        if status_data is None:
            error = "ERROR: No job data available."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            return

        if job_str is None:
            jobs = status_data["jobs"]
        else:
            jobs = status_data["jobs"][job_str]

        self.state.print_status(endpoint_json=jobs, update_only=True)
        return jobs

    def set_job(self, job_str, status_message, value):
        """Initiates or modifies job with given parameters."""
        self.state.print_status(description=f"Marking job {job_str} as {value}% {status_message}.")

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
        """Marks job as completed and triggers any associated actions."""
        self.state.print_status(description=f"Marking job {job_str} as `complete`.")

        lua_code = f"""
            complete_job("{job_str}")
        """

        self.resource.lua(lua_code)
