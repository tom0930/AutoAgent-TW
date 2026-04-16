import win32job
import win32api
import win32con
import logging

logger = logging.getLogger("Utils.Win32Job")

class Win32JobManager:
    """
    Manages a Windows Job Object to ensure strict process lifecycle.
    Any process assigned to this job will be killed when the job object is closed.
    """
    _instance = None

    def __init__(self, name="Antigravity_Process_Job"):
        try:
            self.job = win32job.CreateJobObject(None, name)
            
            # Configure job to kill all children on close
            info = win32job.QueryInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation)
            info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            win32job.SetInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation, info)
            
            logger.info(f"Initialized Windows Job Object: {name}")
        except Exception as e:
            logger.error(f"Failed to create Job Object: {e}")
            self.job = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def assign_process(self, process_handle):
        """Assigns a process (by handle) to the job object."""
        if not self.job:
            return
        try:
            win32job.AssignProcessToJobObject(self.job, process_handle)
        except Exception as e:
            logger.warning(f"Failed to assign process to Job Object: {e}")

    def add_pid(self, pid: int):
        """Assigns a process (by PID) to the job object."""
        if not self.job:
            return
        try:
            # Get handle from PID
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            win32job.AssignProcessToJobObject(self.job, handle)
            win32api.CloseHandle(handle)
        except Exception as e:
            logger.warning(f"Failed to add PID {pid} to Job Object: {e}")

# Global Job for the entire session
process_job = Win32JobManager.get_instance()
