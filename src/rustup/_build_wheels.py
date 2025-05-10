from __future__ import annotations

import asyncio
from pathlib import Path

from httpx import AsyncClient
from tqdm import tqdm

from ._build_wheel import download_binary, pypi_targets, rustup_targets, write_wheel


async def download_all_binaries(binary_dir: Path):
    binary_dir.mkdir(exist_ok=True)
    binary_dir.joinpath(".gitignore").write_text("*\n")
    async with AsyncClient() as client:
        tasks = []
        for target_triple in pypi_targets:
            task = download_binary(client, target_triple, binary_dir)
            tasks.append(task)

        total = len(tasks)
        with tqdm(total=total, desc="Downloading binaries") as pbar:
            for coro in asyncio.as_completed(tasks):
                target = await coro
                pbar.update(1)
                pbar.set_postfix({"Last": target}, refresh=True)


def build_wheels(output_dir: Path, dist_dir: Path):
    dist_dir.mkdir(exist_ok=True)
    dist_dir.joinpath(".gitignore").write_text("*\n")
    for target_triple, pypi_target in pypi_targets.items():
        write_wheel(
            output_dir,
            rustup_targets[target_triple],
            dist_dir,
            target_triple,
            pypi_target,
        )
        print(f"Created wheel for {pypi_target}")
