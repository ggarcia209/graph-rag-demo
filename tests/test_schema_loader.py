"""Tests for the ontology schema loader and Pydantic models."""

from __future__ import annotations

import os
import tempfile

import pytest
import yaml

from src.schema.loader import load_schema
from src.schema.models import (
    EdgeTypeDefinition,
    NodeTypeDefinition,
    OntologySchema,
    PropertyDefinition,
    TraversalPattern,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_SCHEMA = {
    "name": "test_schema",
    "version": "1.0",
    "description": "A minimal test schema",
    "graph_name": "test_graph",
    "node_types": {
        "Person": {
            "description": "A person entity",
            "properties": {
                "id": {"type": "string", "required": True},
                "name": {"type": "string", "required": True},
                "bio": {"type": "string", "embeddable": True},
            },
        },
        "Company": {
            "description": "A company entity",
            "properties": {
                "id": {"type": "string", "required": True},
                "name": {"type": "string", "required": True},
            },
        },
    },
    "edge_types": {
        "WORKS_AT": {
            "source": "Person",
            "target": "Company",
            "description": "Employment relationship",
            "properties": {
                "confidence": {"type": "float"},
            },
        },
    },
    "traversal_patterns": {
        "person_company": {
            "description": "Find where a person works",
            "pattern": "(p:Person)-[:WORKS_AT]->(c:Company)",
        },
    },
}


def _write_yaml(data: dict, path: str) -> None:
    """Write a dict to a YAML file."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


# ---------------------------------------------------------------------------
# PropertyDefinition tests
# ---------------------------------------------------------------------------


class TestPropertyDefinition:
    """Tests for PropertyDefinition model."""

    def test_defaults(self) -> None:
        prop = PropertyDefinition(type="string")
        assert prop.type == "string"
        assert prop.required is False
        assert prop.embeddable is False
        assert prop.description == ""
        assert prop.values == []

    def test_all_fields(self) -> None:
        prop = PropertyDefinition(
            type="enum",
            required=True,
            embeddable=False,
            description="Status field",
            values=["ACTIVE", "INACTIVE"],
        )
        assert prop.type == "enum"
        assert prop.required is True
        assert prop.values == ["ACTIVE", "INACTIVE"]


# ---------------------------------------------------------------------------
# NodeTypeDefinition tests
# ---------------------------------------------------------------------------


class TestNodeTypeDefinition:
    """Tests for NodeTypeDefinition model."""

    def test_embeddable_fields(self) -> None:
        node = NodeTypeDefinition(
            description="Test node",
            properties={
                "id": PropertyDefinition(type="string", required=True),
                "name": PropertyDefinition(type="string", required=True),
                "bio": PropertyDefinition(type="string", embeddable=True),
                "summary": PropertyDefinition(type="string", embeddable=True),
            },
        )
        assert sorted(node.embeddable_fields()) == ["bio", "summary"]

    def test_required_fields(self) -> None:
        node = NodeTypeDefinition(
            properties={
                "id": PropertyDefinition(type="string", required=True),
                "name": PropertyDefinition(type="string", required=True),
                "bio": PropertyDefinition(type="string"),
            },
        )
        assert sorted(node.required_fields()) == ["id", "name"]

    def test_empty_properties(self) -> None:
        node = NodeTypeDefinition()
        assert node.embeddable_fields() == []
        assert node.required_fields() == []


# ---------------------------------------------------------------------------
# EdgeTypeDefinition tests
# ---------------------------------------------------------------------------


class TestEdgeTypeDefinition:
    """Tests for EdgeTypeDefinition model."""

    def test_required_source_target(self) -> None:
        edge = EdgeTypeDefinition(source="Person", target="Company")
        assert edge.source == "Person"
        assert edge.target == "Company"
        assert edge.properties == {}

    def test_missing_source_raises(self) -> None:
        with pytest.raises(Exception):
            EdgeTypeDefinition(target="Company")  # type: ignore[call-arg]

    def test_missing_target_raises(self) -> None:
        with pytest.raises(Exception):
            EdgeTypeDefinition(source="Person")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# TraversalPattern tests
# ---------------------------------------------------------------------------


class TestTraversalPattern:
    """Tests for TraversalPattern model."""

    def test_valid_pattern(self) -> None:
        tp = TraversalPattern(
            description="Test pattern",
            pattern="(a:Event)-[:CAUSES]->(b:Event)",
        )
        assert tp.pattern == "(a:Event)-[:CAUSES]->(b:Event)"

    def test_missing_pattern_raises(self) -> None:
        with pytest.raises(Exception):
            TraversalPattern(description="No pattern")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# OntologySchema tests
# ---------------------------------------------------------------------------


class TestOntologySchema:
    """Tests for OntologySchema model."""

    def test_validate_node_label(self) -> None:
        schema = OntologySchema.model_validate(MINIMAL_SCHEMA)
        assert schema.validate_node_label("Person") is True
        assert schema.validate_node_label("Company") is True
        assert schema.validate_node_label("NonExistent") is False

    def test_validate_edge_type(self) -> None:
        schema = OntologySchema.model_validate(MINIMAL_SCHEMA)
        assert schema.validate_edge_type("WORKS_AT") is True
        assert schema.validate_edge_type("UNKNOWN") is False

    def test_get_embeddable_node_types(self) -> None:
        schema = OntologySchema.model_validate(MINIMAL_SCHEMA)
        embeddable = schema.get_embeddable_node_types()
        assert "Person" in embeddable
        assert embeddable["Person"] == ["bio"]
        # Company has no embeddable fields
        assert "Company" not in embeddable

    def test_missing_name_raises(self) -> None:
        data = {**MINIMAL_SCHEMA}
        del data["name"]
        with pytest.raises(Exception):
            OntologySchema.model_validate(data)

    def test_missing_graph_name_raises(self) -> None:
        data = {**MINIMAL_SCHEMA}
        del data["graph_name"]
        with pytest.raises(Exception):
            OntologySchema.model_validate(data)


# ---------------------------------------------------------------------------
# Schema loader tests
# ---------------------------------------------------------------------------


class TestLoadSchema:
    """Tests for the load_schema function."""

    def test_load_valid_schema(self, tmp_path: str) -> None:
        path = os.path.join(str(tmp_path), "valid.yaml")
        _write_yaml(MINIMAL_SCHEMA, path)

        schema = load_schema(path)
        assert schema.name == "test_schema"
        assert schema.graph_name == "test_graph"
        assert len(schema.node_types) == 2
        assert len(schema.edge_types) == 1
        assert len(schema.traversal_patterns) == 1

    def test_load_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="schema file not found"):
            load_schema("/nonexistent/path/schema.yaml")

    def test_load_invalid_yaml(self, tmp_path: str) -> None:
        path = os.path.join(str(tmp_path), "bad.yaml")
        with open(path, "w") as f:
            f.write(":\n  :\n    - :\n      bad: [yaml: content")

        with pytest.raises(ValueError, match="invalid YAML"):
            load_schema(path)

    def test_load_non_mapping_yaml(self, tmp_path: str) -> None:
        path = os.path.join(str(tmp_path), "list.yaml")
        with open(path, "w") as f:
            f.write("- item1\n- item2\n")

        with pytest.raises(ValueError, match="expected a YAML mapping"):
            load_schema(path)

    def test_load_schema_validation_error(self, tmp_path: str) -> None:
        path = os.path.join(str(tmp_path), "incomplete.yaml")
        # Missing required 'name' and 'graph_name'
        _write_yaml({"version": "1.0"}, path)

        with pytest.raises(ValueError, match="schema validation failed"):
            load_schema(path)

    def test_load_directory_raises(self, tmp_path: str) -> None:
        with pytest.raises(ValueError, match="path is not a file"):
            load_schema(str(tmp_path))

    def test_load_gdelt_schema(self) -> None:
        """Verify the real GDELT schema file loads without error."""
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "schemas",
            "gdelt_markets.yaml",
        )
        if not os.path.exists(schema_path):
            pytest.skip("GDELT schema file not found")

        schema = load_schema(schema_path)
        assert schema.name == "gdelt_markets"
        assert schema.graph_name == "gdelt_markets"
        assert len(schema.node_types) == 6
        assert "Event" in schema.node_types
        assert "Organization" in schema.node_types
        assert "Commodity" in schema.node_types
        assert len(schema.edge_types) > 0
        assert len(schema.traversal_patterns) > 0
