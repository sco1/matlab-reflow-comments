[![GitHub release](https://img.shields.io/github/release/sco1/pre-commit-matlab.svg)](https://github.com/sco1/pre-commit-matlab/releases/latest)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sco1/pre-commit-matlab/main.svg)](https://results.pre-commit.ci/latest/github/sco1/pre-commit-matlab/main)
[![lint-and-test](https://github.com/sco1/pre-commit-matlab/actions/workflows/lint_test.yml/badge.svg?branch=main)](https://github.com/sco1/pre-commit-matlab/actions/workflows/lint_test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
# pre-commit-matlab
A collection of [pre-commit](https://pre-commit.com/) hooks for MATLAB

Ok... it's just one hook so far but maybe someday there will be more 😃!

## Using pre-commit-matlab with pre-commit
Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/sco1/pre-commit-matlab
    rev: v1.0.0
    hooks:
    -   id: matlab-reflow-comments
        args: [--line-length=100]
```

## Hooks
### `pre-commit-matlab`
Reflow comments (lines beginning with `%`) in MATLAB file(s) (`*.m`) to the specified line length.

Blank comment lines are passed back into the reformatted source code.

* Specify line length with `args: [--line-length=100]` (Default: `75`)
* Ignore comments with inner indentation `args: [--ignore-indented=True]` (Default: `True`)

If `ignore_indented` is `True`, comments that contain inner indentation of at least two spaces
is passed back into the reformatted source code as-is. Leading whitespace in the line is not
considered.

For example:
  ```matlab
  %  This is indented
  %    This is indented

  % This is not indented
      % This is not indented
  ```
