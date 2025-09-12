#!python

import subprocess
import sys
import os
from os.path import dirname, abspath, join, exists


def _shim(proxy: str) -> None:
    parent = dirname(abspath(__file__))
    # Ensure `rustup` is on PATH
    if parent not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] = os.pathsep.join(
            [parent, *os.environ["PATH"].split(os.pathsep)]
        )
    rustup = join(parent, "rustup")
    if not exists(rustup):
        raise RuntimeError(f"rustup binary does not exist: {rustup}")
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
