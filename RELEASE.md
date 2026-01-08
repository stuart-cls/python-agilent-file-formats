# Release

Tag the release, mark as a Release on github and the package will be published to pypi.

## Manually

Everything is in `pyproject.toml`:

```
python -m build
twine upload dist/*
```