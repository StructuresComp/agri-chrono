"""Peak GPU memory of this process as seen by NVML (nvidia-smi), polled in a background thread; None without NVML."""
import importlib.util
import os
import threading


class PeakVRAM:
    def __init__(self, interval=1.0):
        self.peak = None
        if importlib.util.find_spec("pynvml") is None:
            return
        import pynvml
        pynvml.nvmlInit()
        self.nvml = pynvml
        self.handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(pynvml.nvmlDeviceGetCount())]
        self.peak = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(interval,), daemon=True)
        self._thread.start()

    def _used(self):
        pid = os.getpid()
        return sum(p.usedGpuMemory or 0 for h in self.handles
                   for p in self.nvml.nvmlDeviceGetComputeRunningProcesses(h) if p.pid == pid)

    def _run(self, interval):
        while not self._stop.wait(interval):
            self.peak = max(self.peak, self._used())

    def stop(self):
        """Peak in GiB (None without NVML or when the process is not visible to NVML, e.g. in a container)."""
        if self.peak is None:
            return None
        self._stop.set()
        self._thread.join()
        self.peak = max(self.peak, self._used())
        return self.peak / 2 ** 30 if self.peak else None
