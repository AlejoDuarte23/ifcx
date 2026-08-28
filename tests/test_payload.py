from __future__ import annotations

import gzip
import json
import struct

import numpy as np

from ifcx.payload import (
    MAGIC,
    SECTION_ORDER,
    build_payload_from_documents,
    restyle_payload,
)


def fake_documents():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype="<f8",
    )
    faces = np.array([[0, 1, 2], [0, 2, 3]], dtype="<u4")
    geometry = {
        "up_axis": "Z",
        "units": "m",
        "elements": {
            42: {
                "ifc_type": "IfcSlab",
                "global_id": "abc",
                "name": "Floor",
                "color": [0.2, 0.4, 0.8, 1.0],
                "vertices": vertices.tobytes(),
                "faces": faces.tobytes(),
            }
        },
    }
    entities = {
        "entity_count": 1,
        "length_unit_scale": 1.0,
        "plane_angle_to_radians": 1.0,
        "entities": {
            42: {
                "description": "Test slab",
                "object_type": None,
                "attributes": [
                    {"name": "PredefinedType", "value": "FLOOR", "value_type": "IFCENUM"}
                ],
                "property_sets": [
                    {
                        "name": "Pset_SlabCommon",
                        "properties": [
                            {"name": "IsExternal", "value": "False", "value_type": "IFCBOOLEAN"}
                        ],
                    }
                ],
                "quantity_sets": [],
                "placement": None,
            },
            99: {
                "ifc_type": "IfcSlabType",
                "name": "Standard floor type",
                "object_type": None,
            },
        },
    }
    return geometry, entities


def unpack_container(compressed: bytes):
    raw = gzip.decompress(compressed)
    assert raw[:8] == MAGIC
    metadata_length = struct.unpack_from("<I", raw, 8)[0]
    offset = 12
    metadata = json.loads(raw[offset : offset + metadata_length])
    offset = (offset + metadata_length + 3) & ~3
    sections = {}
    for name in SECTION_ORDER:
        length = struct.unpack_from("<I", raw, offset)[0]
        offset += 4
        sections[name] = raw[offset : offset + length]
        offset = (offset + length + 3) & ~3
    return raw, metadata, sections


def test_payload_contains_geometry_and_properties():
    geometry, entities = fake_documents()
    spatial = {
        "project_id": 1,
        "element_to_container": {42: 2},
        "element_to_storey": {42: 2},
        "roots": [
            {
                "express_id": 1,
                "ifc_type": "IfcProject",
                "name": "Test project",
                "children": [
                    {
                        "express_id": 2,
                        "ifc_type": "IfcBuildingStorey",
                        "name": "Ground floor",
                        "children": [],
                        "elements": [42],
                        "referenced_elements": [],
                    }
                ],
                "elements": [],
                "referenced_elements": [],
            }
        ],
    }
    relationships = {
        "edges": [
            {
                "relationship_id": 100,
                "relationship_type": "IfcRelDefinesByType",
                "relating_id": 99,
                "related_id": 42,
            }
        ]
    }
    materials = {
        "definitions": {
            77: {
                "source_definition_id": 77,
                "resolved_definition_id": 77,
                "material_type": "Material",
                "name": "Concrete",
                "category": "Concrete",
            }
        },
        "element_materials": {42: [{"definition_id": 77, "inherited_from_type": 99}]},
    }
    payload = build_payload_from_documents(
        geometry,
        entities,
        spatial_doc=spatial,
        relationships_doc=relationships,
        materials_doc=materials,
    )
    raw, metadata, sections = unpack_container(payload.compressed)

    assert payload.raw_size == len(raw)
    assert metadata["model"]["element_count"] == 1
    assert metadata["model"]["world_origin"] == [1.0, 0.5, 0.0]
    assert metadata["spatial"]["roots"][0]["children"][0]["elements"] == [42]
    references = metadata["references"]
    assert references["elements"]["42"]["container_id"] == 2
    assert references["elements"]["42"]["storey_id"] == 2
    assert references["elements"]["42"]["relationships"][0]["target_id"] == 99
    assert references["referenced_entities"]["99"]["name"] == "Standard floor type"
    assert references["elements"]["42"]["materials"][0]["definition_id"] == 77
    assert references["material_definitions"]["77"]["name"] == "Concrete"
    element = metadata["elements"][0]
    assert element["id"] == 42
    assert element["ifc_type"] == "IfcSlab"
    assert element["property_sets"][0]["name"] == "Pset_SlabCommon"
    assert len(sections["opaque_positions"]) == 4 * 3 * 4
    assert len(sections["opaque_indices"]) == 2 * 3 * 4
    assert sections["transparent_positions"] == b""


def test_initial_color_and_hidden_state_are_separate():
    geometry, entities = fake_documents()
    payload = build_payload_from_documents(
        geometry,
        entities,
        initial_colors={42: "#ff0000"},
        hidden_ids=[42],
    )
    _, metadata, _ = unpack_container(payload.compressed)
    element = metadata["elements"][0]
    assert element["configured_color"] == [255, 0, 0, 255]
    assert element["display_color"] == [255, 0, 0, 0]


def test_color_channels_accept_normalized_and_mixed_alpha():
    geometry, entities = fake_documents()
    normalized = build_payload_from_documents(
        geometry,
        entities,
        initial_colors={42: (1.0, 0.5, 0.0, 0.25)},
    )
    _, metadata, _ = unpack_container(normalized.compressed)
    assert metadata["elements"][0]["configured_color"] == [255, 128, 0, 64]

    mixed = build_payload_from_documents(
        geometry,
        entities,
        initial_colors={42: (255, 0, 0, 0.5)},
    )
    _, metadata, _ = unpack_container(mixed.compressed)
    assert metadata["elements"][0]["configured_color"] == [255, 0, 0, 128]


def test_transparent_initial_override_uses_transparent_batch():
    geometry, entities = fake_documents()
    payload = build_payload_from_documents(
        geometry,
        entities,
        initial_colors={42: "#4f8cff66"},
    )
    _, metadata, sections = unpack_container(payload.compressed)
    assert metadata["elements"][0]["batch"] == "transparent"
    assert sections["opaque_positions"] == b""
    assert len(sections["transparent_positions"]) == 4 * 3 * 4


def test_restyle_patches_colors_without_moving_geometry_batches():
    geometry, entities = fake_documents()
    base = build_payload_from_documents(geometry, entities)
    styled = restyle_payload(
        base,
        initial_colors={42: "#4f8cff66"},
        hidden_ids=[42],
    )
    _, metadata, sections = unpack_container(styled.compressed)
    element = metadata["elements"][0]
    assert element["batch"] == "opaque"
    assert element["configured_color"] == [79, 140, 255, 102]
    assert element["display_color"] == [79, 140, 255, 0]
    colors = np.frombuffer(sections["opaque_colors"], dtype=np.uint8).reshape(-1, 4)
    assert np.all(colors == [79, 140, 255, 0])
    assert sections["transparent_colors"] == b""
