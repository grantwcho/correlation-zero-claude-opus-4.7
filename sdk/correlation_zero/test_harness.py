import sys
from pathlib import Path

from .validator import main as validate_main


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    repo_dir = Path(argv[0]).resolve() if argv else Path.cwd()
    return validate_main([str(repo_dir)])


if __name__ == "__main__":
    raise SystemExit(main())
