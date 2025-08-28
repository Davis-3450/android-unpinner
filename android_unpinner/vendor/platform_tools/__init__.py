import logging
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

device: str | None = None
here = Path(__file__).absolute().parent

PLATFORM = sys.platform

if PLATFORM == "win32":
    adb_binary = here / "win32" / "adb.exe"
elif PLATFORM == "darwin":
    adb_binary = here / "darwin" / "adb"
else:
    adb_binary = here / "linux" / "adb"


def adb(cmd: str | Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Helper to call adb and capture stdout safely.

    - Accepts either a single command string (backwards-compatible) or a
      sequence of arguments (recommended when passing local paths that may
      contain spaces).

    - Special-cases strings starting with "shell " so everything after
      that is passed as a single argument, allowing the remote shell to
      handle pipes/quotes.
    """
    parts: list[str] = [str(adb_binary)]
    if device:
        parts += ["-s", device]
        logging.debug(f"Using device: {device}")

    if isinstance(cmd, (list, tuple)):
        parts += [str(x) for x in cmd]
    elif isinstance(cmd, str):
        if cmd.startswith("shell "):
            # Keep everything after "shell " intact so remote shell parses it
            parts += ["shell", cmd[len("shell ") :]]
        else:
            parts += shlex.split(cmd, posix=(PLATFORM != "win32"))
    else:
        raise TypeError("cmd must be a str or a sequence of str")

    try:
        proc = subprocess.run(parts, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logging.debug(f"cmd={parts}\n{e.stdout=}\n{e.stderr=}")
        raise
    logging.debug(f"cmd={parts}\n{proc.stdout=}\n{proc.stderr=}")
    return proc


def set_device(device_serial: str | None) -> None:
    """Set the target device for all adb commands."""
    global device
    device = device_serial
