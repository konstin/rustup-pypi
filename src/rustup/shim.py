from __future__ import annotations

import os
import sys
from os.path import dirname, abspath, join, exists, splitext


def _shim(proxy: str) -> None:
    parent = dirname(abspath(sys.argv[0]))
    # Ensure `rustup` is on PATH
    if parent not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] = os.pathsep.join(
            [parent, *os.environ["PATH"].split(os.pathsep)]
        )

    # Read the exe suffix from the real argv, otherwise use a fallback
    if len(sys.orig_argv) > 1:
        exe_suffix = splitext(sys.orig_argv[1])[1]
    else:
        exe_suffix = ".exe" if sys.platform == "win32" else ""
    rustup = join(parent, f"rustup{exe_suffix}")
    if not exists(rustup):
        raise RuntimeError(f"rustup binary does not exist: {rustup}")
    # Keep pretending we're the shim binary
    args = (proxy, *sys.argv[1:])
    os.execv(rustup, args)


def init() -> None:
    _shim("rustup-init")


def cargo() -> None:
    _shim("cargo")


def cargo_clippy() -> None:
    _shim("cargo-clippy")


def cargo_fmt() -> None:
    _shim("cargo-fmt")


def cargo_miri() -> None:
    _shim("cargo-miri")


def clippy_driver() -> None:
    _shim("clippy-driver")


def rls() -> None:
    _shim("rls")


def rust_analyzer() -> None:
    _shim("rust-analyzer")


def rust_gdb() -> None:
    _shim("rust-gdb")


def rust_gdbgui() -> None:
    _shim("rust-gdbgui")


def rust_lldb() -> None:
    _shim("rust-lldb")


def rustc() -> None:
    _shim("rustc")


def rustdoc() -> None:
    _shim("rustdoc")


def rustfmt() -> None:
    _shim("rustfmt")
