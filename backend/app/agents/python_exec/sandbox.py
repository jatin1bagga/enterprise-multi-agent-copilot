import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import psutil

from app.core.config import get_settings

# NOTE: we deliberately do not enforce a strict import allowlist here. An earlier version
# overrode builtins.__import__ to block anything outside a small allowlist, but pandas/
# matplotlib/plotly all trigger transitive stdlib imports (e.g. matplotlib importing `_io`)
# that got blocked too, breaking the libraries themselves. Since this sandbox already isn't a
# real security boundary against adversarial code (subprocess isolation + timeout + memory
# watchdog only protects server stability, not against a user deliberately asking for
# malicious code - see architecture notes), a leaky import allowlist added friction without
# adding real safety. Isolation instead comes from: a fresh scratch cwd, `-I` interpreter
# isolation, a wall-clock timeout, and the RSS memory watchdog below.
_PREAMBLE = """
import matplotlib
matplotlib.use("Agg")

DATA_PATH = {data_path!r}
"""


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    returncode: int
    output_files: list[Path]
    timed_out: bool
    killed_for_memory: bool


def _watch_memory(proc: subprocess.Popen, limit_mb: int, stop_event: threading.Event, killed_flag: list[bool]) -> None:
    try:
        ps_proc = psutil.Process(proc.pid)
    except psutil.NoSuchProcess:
        return
    while not stop_event.is_set():
        try:
            rss_mb = ps_proc.memory_info().rss / (1024 * 1024)
            if rss_mb > limit_mb:
                killed_flag[0] = True
                proc.kill()
                return
        except psutil.NoSuchProcess:
            return
        time.sleep(0.2)


def run_in_sandbox(code: str, data_path: str | None) -> SandboxResult:
    settings = get_settings()
    sandbox_root = _ensure_sandbox_dir(settings)

    with tempfile.TemporaryDirectory(dir=sandbox_root) as tmpdir:
        workdir = Path(tmpdir)
        script_path = workdir / "script.py"
        preamble = _PREAMBLE.format(data_path=data_path)
        script_path.write_text(preamble + "\n\n" + code, encoding="utf-8")

        proc = subprocess.Popen(
            [sys.executable, "-I", str(script_path)],
            cwd=str(workdir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        killed_flag = [False]
        stop_event = threading.Event()
        watchdog = threading.Thread(
            target=_watch_memory,
            args=(proc, settings.sandbox_memory_limit_mb, stop_event, killed_flag),
            daemon=True,
        )
        watchdog.start()

        timed_out = False
        try:
            stdout, stderr = proc.communicate(timeout=settings.sandbox_timeout_seconds)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            timed_out = True
        finally:
            stop_event.set()
            watchdog.join(timeout=1)

        output_files = [
            workdir / name for name in ("output.png", "output_table.csv") if (workdir / name).exists()
        ]

        persisted_files = []
        for f in output_files:
            dest = settings.artifact_abs_dir / f"{workdir.name}_{f.name}"
            dest.write_bytes(f.read_bytes())
            persisted_files.append(dest)

        return SandboxResult(
            stdout=stdout,
            stderr=stderr,
            returncode=proc.returncode,
            output_files=persisted_files,
            timed_out=timed_out,
            killed_for_memory=killed_flag[0],
        )


def _ensure_sandbox_dir(settings) -> Path:
    path = settings.artifact_abs_dir / "sandbox_runs"
    path.mkdir(parents=True, exist_ok=True)
    return path
