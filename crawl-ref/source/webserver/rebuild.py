import os
import subprocess
from multiprocessing import Process, Queue
import logging

import config

_queue = Queue()

_REBUILD_LOG_DIR = "tmp/"


def _shed_privileges():
    os.setgid(1002)
    os.setuid(1002)


def _get_log_path_for_version(version, chroot=False):
    base = config.chroot if chroot else '/'
    return os.path.join(base, _REBUILD_LOG_DIR, version + ".log")


def _do_rebuild(version):
    if version == "git":
        command = ["update-trunk"]
    else:
        command = ["update-stable", version]
    argv = ["/home/crawl-dev/dgamelaunch-config/bin/dgl"] + command

    log_path = _get_log_path_for_version(version, chroot=True)
    print("rebuilding, logging to ", log_path)
    with open(log_path, "w", buffering=1) as log_file:
        subprocess.Popen(argv, stdout=log_file, stderr=log_file).wait()


def _rebuilder_main():
    _shed_privileges()
    while True:
        _do_rebuild(_queue.get())


def trigger_rebuild(version):
    print("Queueing rebuild: %s", version)
    _queue.put(version)


def start():
    """Forks a rebuilder subprocess outside of the chroot.
    """
    print("-------starting rebuilder-------")
    rebuilder_process = Process(target=_rebuilder_main)
    rebuilder_process.daemon = True
    rebuilder_process.start()
