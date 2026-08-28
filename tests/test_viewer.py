from __future__ import annotations

from ifcx.payload import PreparedPayload
from ifcx.viewer import IFCViewer


def _metadata():
    return {
        "model": {"element_count": 2},
        "spatial": {"project_id": 1, "roots": []},
        "references": {
            "elements": {"10": {"container_id": 30}},
            "spatial_nodes": {"30": {"id": 30, "name": "Ground floor"}},
            "material_definitions": {},
        },
        "batches": {
            "opaque": {"vertex_count": 8, "triangle_count": 12},
            "transparent": {"vertex_count": 4, "triangle_count": 2},
        },
        "elements": [
            {
                "id": 10,
                "ifc_type": "IfcWall",
                "name": "External wall",
                "global_id": "wall-guid",
                "object_type": None,
            },
            {
                "id": 20,
                "ifc_type": "IfcSpace",
                "name": "Office",
                "global_id": "space-guid",
                "object_type": "Workspace",
            },
        ],
    }


def test_viewer_reads_bytes_once_and_restyles_without_retessellating(monkeypatch):
    build_calls = []
    style_calls = []

    def fake_build(data, **kwargs):
        build_calls.append((data, kwargs))
        return PreparedPayload(
            compressed=b"data",
            raw_size=12,
            metadata=_metadata(),
        )

    def fake_restyle(prepared, **kwargs):
        style_calls.append((prepared, kwargs))
        return PreparedPayload(
            compressed=b"styled-data",
            raw_size=16,
            metadata=prepared.metadata,
        )

    monkeypatch.setattr("ifcx.viewer.build_payload", fake_build)
    monkeypatch.setattr("ifcx.viewer.restyle_payload", fake_restyle)
    viewer = IFCViewer(b"ISO-10303-21;", title="Test")
    first = viewer.to_html(asset_mode="cdn")
    second = viewer.to_html(asset_mode="cdn")
    assert "Test" in first
    assert second == first
    assert len(build_calls) == 1

    viewer.set_color(10, "#ff0000")
    viewer.to_html(asset_mode="cdn")
    assert len(build_calls) == 1
    assert len(style_calls) == 1
    assert style_calls[-1][1]["initial_colors"] == {10: "#ff0000"}
    assert build_calls[-1][1]["include_properties"] is True
    assert build_calls[-1][1]["inherit_type_properties"] is True
    assert build_calls[-1][1]["include_attributes"] is True


def test_find_stats_and_python_styling(monkeypatch):
    calls = []

    def fake_build(data, **kwargs):
        calls.append(kwargs)
        return PreparedPayload(compressed=b"data", raw_size=12, metadata=_metadata())

    def fake_restyle(prepared, **kwargs):
        calls.append(kwargs)
        return PreparedPayload(compressed=b"styled", raw_size=12, metadata=prepared.metadata)

    monkeypatch.setattr("ifcx.viewer.build_payload", fake_build)
    monkeypatch.setattr("ifcx.viewer.restyle_payload", fake_restyle)
    viewer = IFCViewer(b"ISO-10303-21;")

    assert viewer.element_count == 2
    assert viewer.spatial["project_id"] == 1
    assert viewer.references["elements"]["10"]["container_id"] == 30
    assert viewer.element_references(10)["container_id"] == 30
    assert viewer.vertex_count == 12
    assert viewer.triangle_count == 14
    assert viewer.step_ids == (10, 20)
    assert viewer.find(ifc_type="IfcSpace") == [20]
    assert viewer.find(name_contains="external") == [10]
    assert viewer.element(10)["global_id"] == "wall-guid"

    viewer.color_by_type("IfcSpace", "#4f8cff66")
    viewer.isolate(20)
    viewer.to_html(asset_mode="cdn")
    assert calls[-1]["initial_colors"] == {20: "#4f8cff66"}
    assert calls[-1]["hidden_ids"] == {10}
