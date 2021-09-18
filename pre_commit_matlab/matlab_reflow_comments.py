import argparse
import textwrap
import typing as t
from collections import deque
from pathlib import Path


def _n_leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip())


def _dump_buffer(f: t.TextIO, buffer: deque, line_length: int, indent_level: int) -> deque:
    """
    Reflow the buffered line(s) to the specified line length, preserving the indent level.

    The buffer is cleared & returned after the new line(s) are written.
    """
    reflowed_src = textwrap.fill(
        "".join(buffer),
        width=line_length,
        initial_indent=f"{' '*indent_level}%",  # Don't include the initial leading space
        subsequent_indent=f"{' '*indent_level}% ",
        break_on_hyphens=False,
    )
    reflowed_src = f"{reflowed_src}\n"
    f.write(reflowed_src)

    buffer.clear()
    return buffer


def _write_line(
    f: t.TextIO, line: str, buffer: deque, line_length: int, indent_level: int
) -> deque:
    """
    Write the provided source line after checking for buffered comments to empty.

    The buffer is cleared & returned after the new line(s) are written.
    """
    if buffer:
        buffer = _dump_buffer(f, buffer, line_length, indent_level)
    f.write(f"{line}\n")

    return buffer


def process_file(
    file: Path, line_length: int, ignore_indented: bool, alternate_capital_handling: bool
) -> None:
    """
    Reflow comments (`%`) in the provided MATLAB file (`*.m`) to the specified line length.

    Blank comment lines are passed back into the reformatted source code.

    If `ignore_indented` is `True`, comments that contain inner indentation of at least two spaces
    is passed back into the reformatted source code as-is. Leading whitespace in the line is not
    considered.

    For example:
        * `%  This is indented`
        * `%    This is indented`
        * `% This is not indented`
        * `    % This is not indented`

    If `alternate_capital_handling` is `True`, if the line buffer has contents then a line beginning
    with a capital letter is treated as the start of a new comment block.

    For example:
        % This is a comment line
        % This is a second comment line that will not be reflowed into the previous line
    """
    src = file.read_text().splitlines()
    with file.open("w") as f:
        buffer: deque = deque()
        indent_level = 0  # Number of leading spaces
        for line in src:
            lstripped_line = line.lstrip()
            if lstripped_line.startswith("%"):
                # Comment line
                if not buffer:
                    # New buffer, set the indentation level for the incoming block
                    indent_level = _n_leading_spaces(line)

                # Count the inner level of indentation of the comment itself to use for both the
                # empty comment line check and the ignore indent check
                # Only strip leading percent sign so inline percentages aren't mangled
                uncommented_line = lstripped_line.replace("%", "", 1).rstrip()
                inner_indent = _n_leading_spaces(uncommented_line)

                if inner_indent == 0:
                    # Blank line, write straight out
                    buffer = _write_line(f, line, buffer, line_length, indent_level)
                    continue

                if ignore_indented and inner_indent >= 2:
                    # Inner indented comment, write straight out
                    buffer = _write_line(f, line, buffer, line_length, indent_level)
                    continue

                # `uncommented_line` is likely to start with leading whitespace that we don't care
                # about for this check
                if alternate_capital_handling and uncommented_line.lstrip()[0].isupper():
                    # Comment line starts with a capital letter
                    # We want to treat this as the start of a new comment block, so if there is an
                    # existing buffer, dump it before adding the current line into a fresh buffer
                    if buffer:
                        buffer = _dump_buffer(f, buffer, line_length, indent_level)

                # If we're here, then we have a line eligible for reflowing so add it to the buffer
                buffer.append(uncommented_line)
                continue

            # Non-comment line, write straight out
            buffer = _write_line(f, line, buffer, line_length, indent_level)
        else:
            # EOF, Dump any remaining comments in the buffer (file ends in comments)
            if buffer:
                buffer = _dump_buffer(f, buffer, line_length, indent_level)


def main(argv: t.Optional[t.Sequence[str]] = None) -> None:  # pragma: no cover  # noqa: D103
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", type=Path)
    parser.add_argument("--line-length", type=int, default=78)
    parser.add_argument("--ignore-indented", type=bool, default=True)
    parser.add_argument("--alternate-capital-handling", type=bool, default=False)
    args = parser.parse_args(argv)

    for file in args.filenames:
        process_file(file, args.line_length, args.ignore_indented, args.alternate_capital_handling)


if __name__ == "__main__":  # pragma: no cover
    main()
