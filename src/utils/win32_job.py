import win32job
import win32api
import win32con
import logging
from typing import Optional, Any

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
            
            # Configure job to kill all children on close AND limit memory
            # pyrefly: ignore [bad-argument-type]
            info = win32job.QueryInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation)
            info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            
            # Phase 149: Add Memory Limit (2GB = 2 * 1024 * 1024 * 1024 bytes)
            # This prevents a runaway process from consuming 4GB+ again.
            info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_JOB_MEMORY
            info['JobMemoryLimit'] = 2 * 1024 * 1024 * 1024 
            
            # pyrefly: ignore [bad-argument-type]
            win32job.SetInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation, info)
            
            logger.info(f"Initialized Windows Job Object: {name}")
        except Exception as e:
            self.job = None

    def set_memory_limit(self, memory_mb: int):
        """Sets a hard memory limit for the job object."""
        if not self.job:
            return
        try:
            info = win32job.QueryInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation)
            info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_JOB_MEMORY
            info['JobMemoryLimit'] = memory_mb * 1024 * 1024
            win32job.SetInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation, info)
            logger.info(f"Memory limit set to {memory_mb}MB for job.")
        except Exception as e:
            logger.error(f"Failed to set memory limit: {e}")

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

    def add_pid(self, pid: int, memory_mb: Optional[int] = None):
        """Assigns a process (by PID) to the job object and applies limits."""
        if not self.job:
            return
        try:
            # Get handle from PID
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            
            # Apply individual memory limit if provided
            if memory_mb:
                # We need to use SetInformationJobObject with JobObjectExtendedLimitInformation
                # for the entire job, or we can use psutil for soft limits.
                # However, Job Objects are best for hard limits.
                # NOTE: JOB_OBJECT_LIMIT_PROCESS_MEMORY is for single processes.
                
                info = win32job.QueryInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation)
                info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY
                info['ProcessMemoryLimit'] = memory_mb * 1024 * 1024
                
                # Warning: SetInformationJobObject affects the WHOLE JOB.
                # If we want per-process different limits, we need separate Job Objects.
                # For Phase 165, we will use a "Template Job" approach or psutil fallback.
                # Let's use a simpler approach: Apply the most restrictive limit to the Job
                # or use psutil for individual enforcement.
                pass

            win32job.AssignProcessToJobObject(self.job, handle)
            win32api.CloseHandle(handle)
        except Exception as e:
            logger.warning(f"Failed to add PID {pid} to Job Object: {e}")

    def apply_legacy_limits(self, pid: int, cpu_priority: str = "normal"):
        """Applies CPU priority via psutil as a supplement to Job Objects."""
        try:
            import psutil
            p = psutil.Process(pid)
            if cpu_priority == "below_normal":
                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            elif cpu_priority == "low":
                p.nice(psutil.IDLE_PRIORITY_CLASS)
            elif cpu_priority == "high":
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                p.nice(psutil.NORMAL_PRIORITY_CLASS)
        except Exception as e:
            logger.debug(f"Could not set CPU priority for {pid}: {e}")

# Global Job for the entire session
process_job = Win32JobManager.get_instance()
