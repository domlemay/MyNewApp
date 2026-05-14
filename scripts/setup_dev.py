#!/usr/bin/env python3
"""Quick dev environment setup script."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(cmd: list[str]) -> None:
    print(f"  > {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    print("Setting up MyNewApp development environment...\n")

    print("[1/3] Installing Python dependencies...")
    run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])

    print("[2/3] Installing pre-commit hooks...")
    try:
        run(["pre-commit", "install"])
    except Exception:
        print("  pre-commit not found, skipping hooks.")

    print("[3/3] Copying .env.example to .env...")
    env_example = ROOT / ".env.example"
    env_file = ROOT / ".env"
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())

    print("\nDone! Run: python -m mynewapp.main")


if __name__ == "__main__":
    main()
