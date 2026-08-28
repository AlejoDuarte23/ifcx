# IFCX

Python-first IFC viewer powered by IFClite geometry, `ifcx-core` references, and Three.js.

## Install

With uv:

```bash
uv add "ifcx @ git+https://github.com/AlejoDuarte23/ifcx.git@firstdraft"
```

With pip:

```bash
pip install "ifcx @ git+https://github.com/AlejoDuarte23/ifcx.git@firstdraft"
```

## Use

```python
from ifcx import IFCViewer

viewer = IFCViewer("building.ifc")
viewer.view(block=True)
```

The viewer includes element selection, properties and references, a model explorer,
visibility controls, coloring, and a browser API. The bundled frontend ships inside the
Python package, so users do not need Node.js.

## Develop

```bash
uv sync --extra dev
npm --prefix frontend install
npm --prefix frontend run build
uv run ruff format .
uv run ruff check .
uv run ty check
uv run pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for commit rules and integration tests.

## License

MIT. Third-party notices are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
