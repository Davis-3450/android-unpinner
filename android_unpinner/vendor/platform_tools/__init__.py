import logging
import shlex
import subprocess
import sys
from pathlib import Path

device: str | None = None
here = Path(__file__).absolute().parent

if sys.platform == "win32":
    adb_binary = here / "win32" / "adb.exe"
elif sys.platform == "darwin":
    adb_binary = here / "darwin" / "adb"
else:
    adb_binary = here / "linux" / "adb"


def adb(cmd: str) -> subprocess.CompletedProcess[str]:
    """Helper function to call adb and capture stdout."""
    parts = [str(adb_binary)]
    if device:
        parts += ["-s", device]
        logging.debug(f"Using device: {device}")

    parts += shlex.split(cmd)  # note, might break on windows

    try:
        proc = subprocess.run(
            parts, shell=True, check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        logging.debug(f"cmd={parts}\n{e.stdout=}\n{e.stderr=}")
        raise
    logging.debug(f"cmd={parts}\n{proc.stdout=}\n{proc.stderr=}")
    return proc


def set_device(device_serial: str | None) -> None:
    """Set the target device for all adb commands."""
    global device
    device = device_serial
