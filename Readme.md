# rustup-pypi

Unofficial [rustup](https://rustup.rs/) distribution for PyPI. Install rustup, and by extension Cargo and rustc, through
Python. Useful for example when writing Python modules in Rust or for platform-independent installation inst

Usage:

```shell
pip install rustup
```

or

```shell
uv pip install rustup
```

Install an initial toolchain, can be skipped if there's a `rust-toolchain.toml`:

```shell
rustup default stable
```

If you are a rust(up) team member and interested in this package, please DM me.

## Internals

rustup is the Rust toolchain's bootstrapping tool: You download rustup, and it installs Cargo, rustc, etc. in
`.cargo/bin`. Rustup can install arbitrary Rust toolchain versions and can switch per invocation, e.g.
`cargo +nightly build` transparently downloads and installs a nightly toolchain. It also reads a `rust-toolchain.toml`,
so if you have Rustup installed, you can build projects that use arbitrary Rust versions.

All Rust toolchain binaries are internally symlinks to `rustup[.exe]`. rustup reads the name of the binary it was
started as, selects the correct toolchain and launches the real e.g. `cargo[.exe]` inside the toolchain folder. On
Windows, junctions are used if symlinks fail
(https://github.com/rust-lang/rustup/blob/8b3aedcc599e9b6c6f3f1ece6a9a45dd4abc5ca4/src/utils/raw.rs#L121-L129).

Wheel cannot contain symlinks, and they don't support post-install scripts. Instead, we're using shim Python scripts
that `execv` into the real rustup binary.

## Building

Due to the conflict between the package being both builder and been built, the current build process for all binaries
is:

```bash
(cd src && python -m rustup.build_rustup_wheels)
```

Otherwise, building a single platform works the regular way:

```bash
uv build
```
