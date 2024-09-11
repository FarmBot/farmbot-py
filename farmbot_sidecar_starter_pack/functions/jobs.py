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

    def get_job(self, job_name=None):
        """Retrieves the status or details of the specified job."""
        self.state.print_status(description="Retrieving job data...")

        status_data = self.info.read_status()

        if status_data is None:
            error = "ERROR: No job data available."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            return

        if job_name is None:
            jobs = status_data["jobs"]
        else:
            jobs = status_data["jobs"][job_name]

        self.state.print_status(endpoint_json=jobs, update_only=True)
        return jobs

    def set_job(self, job_name, status, percent):
        """Initiates or modifies job with given parameters."""
        self.state.print_status(
            description=f"Marking job {job_name} as {percent}% {status}.")

        lua_code = f"""
            local job_name = "{job_name}"
            set_job(job_name)

            -- Update the job\'s status and percent:
            set_job(job_name, {{
            status = "{status}",
            percent = {percent}
            }})
        """

        self.resource.lua(lua_code)

    def complete_job(self, job_name):
        """Marks job as completed and triggers any associated actions."""
        self.state.print_status(
            description=f"Marking job {job_name} as `complete`.")

        lua_code = f"complete_job(\"{job_name}\")"

        self.resource.lua(lua_code)
