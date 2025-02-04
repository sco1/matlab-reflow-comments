import argparse
import subprocess
import sys
import typing as t
from pathlib import Path


def _try_find_mlint() -> Path:
    """
    Attempt to locate mlint on the system, raise if it cannot be located.

    If MATLAB is installed and on the system path, the mlint executable should be located in a child
    directory of the path returned by `which matlab` (or `where` on Windows).
    """
    if sys.platform == "win32":
        matlab_check = subprocess.run(["where", "matlab"], capture_output=True, text=True)
    else:
        matlab_check = subprocess.run(["which", "matlab"], capture_output=True, text=True)

    if matlab_check.returncode != 0:
        raise RuntimeError("MATLAB installation could not be located on system path")

    matlab_bin = Path(matlab_check.stdout.strip()).parent
    if sys.platform == "win32":
        mlint_candidates = list(matlab_bin.rglob("mlint.exe"))
        if not mlint_candidates:
            raise RuntimeError("Could not locate path to mlint.exe")

        mlint_path = mlint_candidates[0]  # Should only be one at this point
    else:
        raise NotImplementedError

    return mlint_path


def process_file(file: Path, mlint_path: Path) -> None:
    """
    Invoke mlint for the specified file.

    mlint seems to always use a return code of `0`, but will print the code analysis output to
    stderr.
    """
    mlint_exec = subprocess.run([mlint_path, file], capture_output=True, text=True)
    if mlint_exec.stderr:
        raise NotImplementedError


def main(argv: t.Optional[t.Sequence[str]] = None) -> None:  # pragma: no cover  # noqa: D103
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", type=Path)
    parser.add_argument("--mlint-path-override", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.mlint_path_override is not None:
        mlint_path = args.mlint_path_override
        if not mlint_path.exists():
            raise ValueError("Specified mlint override path does not exist.")
    else:
        mlint_path = _try_find_mlint()

    for file in args.filenames:
        process_file(file, mlint_path)


if __name__ == "__main__":  # pragma: no cover
    main()
