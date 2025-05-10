from __future__ import annotations

import hashlib
from email.message import EmailMessage
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable
from zipfile import ZIP_DEFLATED, ZipFile

from httpx import AsyncClient


try:
    import tomllib  # pyright: ignore
except ModuleNotFoundError:
    # noinspection PyUnresolvedReferences
    import tomli as tomllib  # pyright: ignore


name = "rustup"
rustup_targets = {
    "aarch64-apple-darwin": "20ef5516c31b1ac2290084199ba77dbbcaa1406c45c1d978ca68558ef5964ef5",
    "aarch64-linux-android": "d2c26e0fc96afe1ea73e67519d3b61dd783b3dafff31928f10f70a9a12cdd820",
    "aarch64-pc-windows-msvc": "de9f7d29ccd39efa59a3dda3ec363b396e09b92681229b9b8f6aaa4c84285e9c",
    "aarch64-unknown-linux-gnu": "e3853c5a252fca15252d07cb23a1bdd9377a8c6f3efa01531109281ae47f841c",
    "aarch64-unknown-linux-musl": "a97c8f56d7462908695348dd8c71ea6740c138ce303715793a690503a94fc9a9",
    "arm-linux-androideabi": "17f6e2e4c37ba1f7340935e3e2da17208e96cf4329c6097ee1308f4e753ba93c",
    "arm-unknown-linux-gnueabi": "3ec755aaa801bdca4caba35cfe3d1657c9c117d87e2e4dd355ab98539115ad45",
    "arm-unknown-linux-gnueabihf": "231a2a004e6e446a1944f957d0eaed858fb9a549264db8dd00a30f491fc67eb8",
    "armv7-linux-androideabi": "353b56ef95c8624da678d4d95e67a07ad8b7e04eb6cad6c149ba43e205da908f",
    "armv7-unknown-linux-gnueabihf": "3b8daab6cc3135f2cd4b12919559e6adaee73a2fbefb830fadf0405c20231d61",
    "i686-apple-darwin": "0d4b45d8570a2dacf4a60e66d1271d61baa8df6938896075dd9521d67f4cef75",
    "i686-linux-android": "bd30e87240a9bc30297cbf2d703f2fdebcb0d2d966285100a64182b41104ea19",
    "i686-pc-windows-gnu": "e9722e3109f857dae0d55dcaf39172abab077530ec02cb9117865d02da1996d9",
    "i686-pc-windows-msvc": "d33375f474f105e529ff3225529a8d6a79a8a4e23f6eab88fba427889e538f34",
    "i686-unknown-linux-gnu": "a5db2c4b29d23e9b318b955dd0337d6b52e93933608469085c924e0d05b1df1f",
    "loongarch64-unknown-linux-gnu": "9861495ee3d7c5fd868635623188a1d6d7919ef6005b4aa9101eb67197fe6d93",
    "loongarch64-unknown-linux-musl": "d1f51ba7113063122a351848bfadd72a8f8ef00621f7991f11cf99ffd86b7373",
    "mips-unknown-linux-gnu": "d06121ac0e196c4d7c0d3b3e8f1910fe757338ea1531f077c70c98e8b3747ccc",
    "mips64-unknown-linux-gnuabi64": "631ed18bfccfba20405ac6d94b9aaee17fb31415ffbc60007f08bbef324fc427",
    "mips64el-unknown-linux-gnuabi64": "644cec63e594707a6098585038cf47e28546c2abe0dde7149cde71d79a0be674",
    "mipsel-unknown-linux-gnu": "13be3b14c23ff04b26a9b187602728ff640724ebe25a5a855c9d3481ad2317af",
    "powerpc-unknown-linux-gnu": "59de648702bfa4ba749e955160ecc3700631bfd2ebb7513a35d041ec2014ad8d",
    "powerpc64-unknown-linux-gnu": "d63e99aee6b38817b4605cbd4d15edb20c5952ff5c5cc527ce7daa396b138b6e",
    "powerpc64le-unknown-linux-gnu": "acd89c42b47c93bd4266163a7b05d3f26287d5148413c0d47b2e8a7aa67c9dc0",
    "powerpc64le-unknown-linux-musl": "08423383d36362d93f8d85f208aa5004a7cef77b69b29fb779ba03ed0544e4f1",
    "s390x-unknown-linux-gnu": "726b7fd5d8805e73eab4a024a2889f8859d5a44e36041abac0a2436a52d42572",
    "x86_64-apple-darwin": "9c331076f62b4d0edeae63d9d1c9442d5fe39b37b05025ec8d41c5ed35486496",
    "x86_64-linux-android": "bddef146c98a299498d8eaa173b1f3064d1feef6a2bc42530dad2df935d00bdd",
    "x86_64-pc-windows-gnu": "ccbfd951d8024856043b3a0c3903a59f39937bce8d3074768b0d3da55f21e817",
    "x86_64-pc-windows-msvc": "88d8258dcf6ae4f7a80c7d1088e1f36fa7025a1cfd1343731b4ee6f385121fc0",
    "x86_64-unknown-freebsd": "4d9fef2e40731489f3186c61a0f178d54d79864fe3d34791edf5b17f70074956",
    "x86_64-unknown-illumos": "42828b1c55ee5c4370337d389318aa2f90d904030b5cfc991a493756763faa7b",
    "x86_64-unknown-linux-gnu": "20a06e644b0d9bd2fbdbfd52d42540bdde820ea7df86e92e533c073da0cdd43c",
    "x86_64-unknown-linux-musl": "e6599a1c7be58a2d8eaca66a80e0dc006d87bbcf780a58b7343d6e14c1605cb2",
    "x86_64-unknown-netbsd": "631eba46df7d84418c75135fbc5b448cfcb30442e1fce5899d4d35eeab56eba5",
}


# Target for which we can upload wheels to PyPI
# https://github.com/pypi/warehouse/blob/0093be2a41b135995c567915012596c6f0d66e6b/warehouse/forklift/legacy.py#L116-L132
# glibc 2.17 is good enough
pypi_targets = {
    "aarch64-apple-darwin": "macosx_11_0_arm64",
    "aarch64-pc-windows-msvc": "win_arm64",
    "aarch64-unknown-linux-gnu": "manylinux_2_17_aarch64",
    "aarch64-unknown-linux-musl": "musllinux_2_17_aarch64",
    # TODO: abi or abihf?
    "arm-unknown-linux-gnueabi": "linux_armv6l",
    "armv7-unknown-linux-gnueabihf": "manylinux_2_17_armv7l",
    "i686-pc-windows-msvc": "win32",
    "i686-unknown-linux-gnu": "manylinux_2_17_i686",
    "powerpc64-unknown-linux-gnu": "manylinux_2_17_ppc64",
    "powerpc64le-unknown-linux-gnu": "manylinux_2_17_ppc64le",
    "powerpc64le-unknown-linux-musl": "musllinux_2_17_ppc64le",
    "s390x-unknown-linux-gnu": "manylinux_2_17_s390x",
    "x86_64-apple-darwin": "macosx_10_12_x86_64",
    "x86_64-pc-windows-msvc": "win_amd64",
    "x86_64-unknown-linux-gnu": "manylinux_2_17_x86_64",
    "x86_64-unknown-linux-musl": "musllinux_2_17_x86_64",
}


@lru_cache
def get_version() -> str:
    """The version of rustup is the version of this package."""
    pyproject_toml = tomllib.loads(
        Path(__file__).parent.parent.parent.joinpath("pyproject.toml").read_text()
    )
    version = pyproject_toml["project"]["version"]
    if pyproject_toml["project"]["name"] != "rustup":
        raise ValueError("`project.name` in pyproject.toml must be rustup")

    return version


def make_message(headers: Iterable[tuple[str, str | list[str]]], payload=None):
    msg = EmailMessage()
    for key, value in headers:
        if isinstance(value, list):
            for value_part in value:
                msg[key] = value_part
        else:
            msg[key] = value
    if payload:
        msg.set_payload(payload)
    return msg


def exe_suffix_for_target(target: str) -> str:
    if target.split("-")[2] == "windows":
        return ".exe"
    else:
        return ""


async def download_binary(client: AsyncClient, target: str, output_dir: Path) -> str:
    exe_suffix = exe_suffix_for_target(target)
    url = f"https://static.rust-lang.org/rustup/archive/{get_version()}/{target}/rustup-init{exe_suffix}"
    output_path = output_dir.joinpath(f"rustup-init-{target}{exe_suffix}")

    async with client.stream("GET", url) as response:
        response.raise_for_status()
        with output_path.open("wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)

    return target


def get_dist_info_dir() -> str:
    return f"rustup-{get_version()}.dist-info"


def write_metadata(write_file: Callable[[str, str], None], tag: str) -> tuple[str, str]:
    """Split out for prepare_metadata_for_build_wheel"""
    dist_info_dir = get_dist_info_dir()
    wheel = [
        ("Wheel-Version", "1.0"),
        ("Generator", "rustup-pypi rustup.build_rustup_wheels"),
        ("Root-Is-Purelib", "false"),
        ("Tag", tag),
    ]
    wheel = make_message(wheel).as_string()
    write_file(f"{dist_info_dir}/WHEEL", wheel)
    metadata1 = [
        ("Metadata-Version", "2.4"),
        ("Name", name),
        ("Version", get_version()),
        ("Project-URL", "Source Code, https://github.com/konstin/rustup-pypi"),
        # Captures both the Python code and rustup
        ("License-Expression", "MIT OR Apache-2.0"),
    ]
    metadata = make_message(
        metadata1, Path(__file__).parent.parent.parent.joinpath("Readme.md").read_text()
    ).as_string()
    write_file(f"{dist_info_dir}/METADATA", metadata)
    return metadata, wheel


def write_wheel(
    binary_dir: Path, sha256: str, dist_dir: Path, target_triple: str, pypi_target: str
) -> str:
    tag = f"py3-none-{pypi_target}"
    wheel_basename = f"rustup-{get_version()}-{tag}.whl"

    exe_suffix = exe_suffix_for_target(target_triple)
    binary_path = binary_dir.joinpath(f"rustup-init-{target_triple}{exe_suffix}")

    with ZipFile(dist_dir.joinpath(wheel_basename), "w", ZIP_DEFLATED) as fp:  # noqa: F821
        scripts_dir = f"rustup-{get_version()}.data/scripts"
        # Not rustup-init, but rustup, we want the installed binary
        fp.write(binary_path, f"{scripts_dir}/rustup{exe_suffix}")

        dist_info_dir = get_dist_info_dir()
        metadata, wheel = write_metadata(fp.writestr, tag)
        record = [
            (
                f"{scripts_dir}/rustup{exe_suffix}",
                f"sha256={sha256}",
                binary_dir.stat().st_size,
            ),
            (
                f"{dist_info_dir}/WHEEL",
                f"sha256={hashlib.sha256(wheel.encode()).hexdigest()}",
                len(wheel.encode()),
            ),
            (
                f"{dist_info_dir}/METADATA",
                f"sha256={hashlib.sha256(metadata.encode()).hexdigest()}",
                len(metadata.encode()),
            ),
            (
                f"{dist_info_dir}/RECORD",
                "",
                "",
            ),
        ]
        record = "\n".join(
            f"{file_name},{file_hash},{size}" for file_name, file_hash, size in record
        )
        fp.writestr(f"{dist_info_dir}/RECORD", record)

    return wheel_basename
