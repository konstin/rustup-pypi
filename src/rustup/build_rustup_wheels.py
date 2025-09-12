from __future__ import annotations

import asyncio
import subprocess
from argparse import ArgumentParser
from pathlib import Path

from ._build_wheels import download_all_binaries, build_wheels

from functools import lru_cache


@lru_cache
def git_root() -> Path:
    return Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .decode()
        .strip()
    )


async def main():
    parser = ArgumentParser()
    parser.add_argument("--binary-dir", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    binary_dir = args.binary_dir or git_root().joinpath("binaries")
    out_dir = args.out_dir or git_root().joinpath("dist")

    await download_all_binaries(binary_dir)
    build_wheels(binary_dir, out_dir)


if __name__ == "__main__":
    asyncio.run(main())
