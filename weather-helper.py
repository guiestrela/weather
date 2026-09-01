#!/usr/bin/env python3
"""Small boundary helper for untrusted HTTP and local state data."""

import os
import pathlib
import secrets
import subprocess
import sys

MAX_RESPONSE = 256 * 1024
MAX_STATE = 64 * 1024
STATE_NAMES = {"weather.json", "weather-panel.json"}


def _check_directory(fd, label):
    info = os.fstat(fd)
    if not stat_is_directory(info.st_mode) or info.st_uid != os.getuid():
        raise OSError("unsafe " + label)
    return fd


def _open_directory(parent_fd, name, create):
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        if not create:
            raise
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
        fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        _check_directory(fd, "state directory")
        os.fchmod(fd, 0o700)
        return fd
    except BaseException:
        os.close(fd)
        raise


def state_dir():
    home_value = os.environ.get("HOME", "")
    if not home_value:
        raise OSError("HOME is not set")
    home = pathlib.Path(home_value).resolve()
    home_fd = os.open(
        home,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
    )
    current_fd = home_fd
    try:
        _check_directory(home_fd, "home directory")
        for part in (".local", "state", "omarchy", "settings"):
            next_fd = _open_directory(current_fd, part, create=True)
            os.close(current_fd)
            current_fd = next_fd
        result_fd = current_fd
        current_fd = -1
        return result_fd
    except BaseException:
        if current_fd != -1:
            os.close(current_fd)
        raise


def state_path(name):
    if name not in STATE_NAMES:
        raise ValueError("invalid state name")
    return name


def validate_target(directory_fd, name):
    try:
        info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat_is_regular(info.st_mode) or info.st_uid != os.getuid():
        raise OSError("unsafe state target")
    if info.st_size > MAX_STATE:
        raise OSError("state target is too large")


def read_state(name):
    name = state_path(name)
    directory_fd = state_dir()
    try:
        try:
            fd = os.open(
                name,
                os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=directory_fd,
            )
        except FileNotFoundError:
            return
        try:
            info = os.fstat(fd)
            if not stat_is_regular(info.st_mode) or info.st_uid != os.getuid():
                raise OSError("unsafe state file")
            if info.st_size > MAX_STATE:
                raise OSError("state file is too large")
            # Repair legacy user-owned state files before exposing their contents.
            os.fchmod(fd, 0o600)
            data = os.read(fd, MAX_STATE + 1)
        finally:
            os.close(fd)
    finally:
        os.close(directory_fd)
    if len(data) > MAX_STATE:
        raise OSError("state file is too large")
    sys.stdout.buffer.write(data)


def stat_is_regular(mode):
    return (mode & 0o170000) == 0o100000


def stat_is_directory(mode):
    return (mode & 0o170000) == 0o040000


def write_state(name, data):
    name = state_path(name)
    if len(data) > MAX_STATE:
        raise OSError("state data is too large")
    directory_fd = state_dir()
    fd = -1
    temporary = None
    try:
        validate_target(directory_fd, name)
        for _ in range(100):
            temporary = "." + name + "." + secrets.token_hex(16)
            try:
                fd = os.open(
                    temporary,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                    0o600,
                    dir_fd=directory_fd,
                )
                break
            except FileExistsError:
                temporary = None
        else:
            raise OSError("could not create temporary state file")
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
        os.replace(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        temporary = None
        os.close(fd)
        fd = -1
        os.fsync(directory_fd)
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        if temporary:
            try:
                os.unlink(temporary, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)


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
