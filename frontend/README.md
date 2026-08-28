# Frontend build

A published Python wheel should contain
`src/ifcx/static/viewer.bundle.js`. Build it once before creating the
wheel:

```bash
python -m ifcx.build_frontend
python -m build
```

The build uses esbuild and pins Three.js and three-mesh-bvh in
`frontend/package.json`. End users do not need Node.js. A source checkout
without the bundle can still run with `asset_mode="cdn"`; `asset_mode="auto"`
uses the local bundle when it exists and otherwise selects that CDN fallback.
