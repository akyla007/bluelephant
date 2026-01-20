import subprocess
import sys


def main() -> None:
    subprocess.check_call([sys.executable, "-m", "black", "backend", "frontend"])
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--reload",
            "--reload-dir",
            "backend",
        ]
    )


if __name__ == "__main__":
    main()
