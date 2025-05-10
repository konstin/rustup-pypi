from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from uv_build import build_sdist, get_requires_for_build_sdist
from httpx import AsyncClient

from puccinialin import get_triple

from ._build_wheel import (
    download_binary,
    get_dist_info_dir,
    pypi_targets,
    rustup_targets,
    write_metadata,
    write_wheel,
)

__all__ = [
    "build_sdist",
    "get_requires_for_build_sdist",
    "build_wheel",
    "get_requires_for_build_wheel",
]


def get_requires_for_build_wheel(
    config_settings: dict[str, str] | None = None,
) -> list[str]:
    if config_settings:
        print("Warning: config_settings not supported", file=sys.stderr)

    return []


def prepare_metadata_for_build_wheel(metadata_directory: str) -> str:
    dist_info_dir = get_dist_info_dir()
    Path(metadata_directory).joinpath(dist_info_dir).mkdir(parents=True, exist_ok=True)

    def write_file(file_path: str, contents: str):
        Path(metadata_directory).joinpath(file_path).open("w").write(contents)

    write_metadata(write_file, metadata_directory)
    return dist_info_dir


async def _download_binary(binary_dir: Path, target_triple: str):
    async with AsyncClient() as client:
        await download_binary(client, target_triple, binary_dir)


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, str] | None = None,
    metadata_directory: str | None = None,
) -> str:
    if config_settings:
        print("Warning: config_settings not supported", file=sys.stderr)
    with TemporaryDirectory() as binary_dir:
        target_triple = get_triple(sys.stderr)
        asyncio.run(_download_binary(Path(binary_dir), target_triple))
        wheel_filename = write_wheel(
            Path(binary_dir),
            rustup_targets[target_triple],
            Path(wheel_directory),
            target_triple,
            pypi_targets[target_triple],
        )
    return wheel_filename
