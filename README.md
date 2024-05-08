# parallel-corpus

[![PyPI version](https://badge.fury.io/py/parallel-corpus.svg)](https://pypi.org/project/parallel-corpus)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parallel-corpus)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/parallel-corpus)](https://pypi.org/project/parallel-corpus/)

[![Maturity badge - level 2](https://img.shields.io/badge/Maturity-Level%202%20--%20First%20Release-yellowgreen.svg)](https://github.com/spraakbanken/getting-started/blob/main/scorecard.md)
[![Stage](https://img.shields.io/pypi/status/parallel-corpus)](https://pypi.org/project/parallel-corpus/)

[![Codecov](https://codecov.io/gh/spraakbanken/parallel-corpus-py/coverage.svg)](https://codecov.io/gh/spraakbanken/parallel-corpus-py)
[![CI(release)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/release.yml/badge.svg)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/release.yml)
[![CI(check)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/check.yml/badge.svg)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/check.yml)
[![CI(test)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/test.yml/badge.svg)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/test.yml)
[![CI(scheduled)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/scheduled.yml/badge.svg)](https://github.com/spraakbanken/parallel-corpus-py/actions/workflows/scheduled.yml)

Parallel corpus as a graph.

Ported from [Graph in spraakbanken/swell-editor](https://github.com/spraakbanken/swell-editor).

## Install

To install `parallel-corpus` in the current environment:

```shell
pip install parallel-corpus
```

To add `parallel-corpus` to a [PDM](https://pdm-project.org) project:

```shell
pdm add parallel-corpus
```

To add `parallel-corpus` manually to `pyproject.toml`:

```toml
[project]
dependencies = ["parallel-corpus>=0.1.2"]
```

## Usage

```python
first = "Jonathan saknades ."

# Initialize graph with source and target equal.
g = graph.init(first)

second = "Jonat han saknades ."

# Update target with new text.
gm = graph.set_target(g, second)

# The graph will now contain a edge from 'Jonathan' and both 'Jonat' and 'han'.
print(f"{gm.edges=}")

```

## Changelog

This project keeps a [changelog](./CHANGELOG.md).

## Development

This project uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

Tools used:

- [pdm](https://pdm-project.org) for project management.
- [pre-commit](https://pre-commit.com/) for pre-commit checking
  - runs ruff linter
  - runs ruff formatter
  - checks that commit message is according conventional commits.
  - install hooks with `pre-commit install`.
- [git-cliff](https://github.com/orhun/git-cliff) for changelog updates.
- [bump-my-version](https://github.com/callowayproject/bump-my-version) for version bumping.
- [syrupy](https://github.com/tophat/syrupy) for snapshot testing.
