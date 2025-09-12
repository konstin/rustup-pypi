#!python

import shutil
import subprocess
import sys
import os


def _shim(proxy: str) -> None:
    rustup = shutil.which("rustup")
    if not rustup:
        raise RuntimeError("Could not find rustup binary in PATH")
    # Keep pretending we're the shim binary
    args = (proxy, *sys.argv[1:])

    # On Windows, `execv` creates a new process, changing the executable name.
    if os.name == "nt":
        sys.exit(
            subprocess.run(
                executable=rustup,
                args=args,
            ).returncode
        )

    os.execv(rustup, args)


if __name__ == "__main__":
    _shim(sys.argv[0])
