from __future__ import annotations

import asyncio
from argparse import ArgumentParser
from pathlib import Path

from ._build_wheels import download_all_binaries, build_wheels


async def main():
    parser = ArgumentParser()
    parser.add_argument("--binary-dir", default="binaries", type=Path)
    parser.add_argument("--out-dir", default="dist", type=Path)
    args = parser.parse_args()
    await download_all_binaries(args.binary_dir)
    build_wheels(args.binary_dir, args.out_dir)


if __name__ == "__main__":
    asyncio.run(main())
