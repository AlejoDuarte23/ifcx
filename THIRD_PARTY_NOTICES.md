# Third-party notices

## IFClite / `ifclite-geom`

The Python runtime depends on `ifclite-geom`, distributed separately under the
Mozilla Public License 2.0. This project does not copy IFClite source files into
its own Python source. Keep the IFClite license and source notice when you
redistribute its wheel or native binary.

- Project: https://github.com/LTplus-AG/ifc-lite
- License: MPL-2.0

## `ifcx-core`

The Python runtime depends on `ifcx-core`, installed directly from its public
GitHub repository and distributed separately under the Mozilla Public License
2.0. Keep its license and source notice when redistributing its native wheel.

- Project: https://github.com/AlejoDuarte23/ifcx-core
- License: MPL-2.0

## Three.js

When the production JavaScript bundle is built, it contains Three.js. The CDN
fallback loads the same pinned package at runtime.

- Project: https://github.com/mrdoob/three.js
- Version pinned by `frontend/package.json`
- License: MIT
- Full license: `src/ifcx/static/licenses/THREE_LICENSE.txt`

## three-mesh-bvh

When the production JavaScript bundle is built, it contains three-mesh-bvh for
accelerated raycasting. The CDN fallback loads the same pinned package at
runtime.

- Project: https://github.com/gkjohnson/three-mesh-bvh
- Version pinned by `frontend/package.json`
- License: MIT
- Full license: `src/ifcx/static/licenses/THREE_MESH_BVH_LICENSE.txt`
