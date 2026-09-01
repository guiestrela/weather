#!/usr/bin/env python3
"""Small boundary helper for untrusted HTTP and local state data."""

import os
import pathlib
import subprocess
import sys
import tempfile

MAX_RESPONSE = 256 * 1024
MAX_STATE = 64 * 1024
STATE_NAMES = {"weather.json", "weather-panel.json"}


def state_dir():
    home_value = os.environ.get("HOME", "")
    if not home_value:
        raise OSError("HOME is not set")
    home = pathlib.Path(home_value).resolve()
    home_info = os.stat(home)
    if not pathlib.Path(home).is_dir() or home_info.st_uid != os.getuid():
        raise OSError("unsafe home directory")
    path = home / ".local" / "state" / "omarchy" / "settings"
    current = home
    for part in path.relative_to(home).parts:
        current = current / part
        info = os.lstat(current) if current.exists() or current.is_symlink() else None
        if info and not pathlib.Path(current).is_dir() or info and pathlib.Path(current).is_symlink():
            raise OSError("state path is not a directory")
        if info and info.st_uid != os.getuid():
            raise OSError("state directory is not owned by the user")
    return path


def state_path(name):
    if name not in STATE_NAMES:
        raise ValueError("invalid state name")
    directory = state_dir()
    path = directory / name
    if path.is_symlink():
        raise OSError("state file is a symlink")
    return path


def read_state(name):
    path = state_path(name)
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        if not stat_is_regular(info.st_mode) or info.st_uid != os.getuid():
            raise OSError("unsafe state file")
        if info.st_size > MAX_STATE:
            raise OSError("state file is too large")
        data = os.read(fd, MAX_STATE + 1)
    finally:
        os.close(fd)
    if len(data) > MAX_STATE:
        raise OSError("state file is too large")
    sys.stdout.buffer.write(data)


def stat_is_regular(mode):
    return (mode & 0o170000) == 0o100000


def write_state(name, data):
    path = state_path(name)
    if len(data) > MAX_STATE:
        raise OSError("state data is too large")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    fd, temporary = tempfile.mkstemp(prefix="." + name + ".", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
        os.close(fd)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def fetch(url, timeout, limit):
    limit = min(max(int(limit), 1), MAX_RESPONSE)
    process = subprocess.Popen(
        ["curl", "-fsS", "--max-time", str(timeout), url],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    data = process.stdout.read(limit + 1)
    if len(data) > limit:
        process.kill()
        process.wait()
        return 2
    process.wait()
    if process.returncode != 0:
        return process.returncode
    sys.stdout.buffer.write(data)
    return 0


def main():
    try:
        if sys.argv[1] == "read" and len(sys.argv) == 3:
            read_state(sys.argv[2])
            return 0
        if sys.argv[1] == "write" and len(sys.argv) == 4:
            write_state(sys.argv[2], sys.argv[3].encode())
            return 0
        if sys.argv[1] == "fetch" and len(sys.argv) == 4:
            return fetch(sys.argv[2], sys.argv[3], MAX_RESPONSE)
    except (OSError, ValueError, IndexError):
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
