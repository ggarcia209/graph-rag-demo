"""Tests for the MCP server layer — factory, tool registration, and response models."""

import os

import pytest
from pydantic import ValidationError

from src.mcp_server.models import RetrievalResult, SchemaInfo
from src.mcp_server.server import (
    _list_schema_files,
    _load_schema_by_name,
    _resolve_schemas_dir,
    create_mcp_server,
)

# ---------------------------------------------------------------------------
# Response model tests
# ---------------------------------------------------------------------------


class TestRetrievalResult:
    """Tests for the RetrievalResult Pydantic model."""

    def test_minimal_fields(self) -> None:
        result = RetrievalResult(
            node_label="Event",
            node_id="evt-001",
            content="Conflict in region X",
        )
        assert result.node_label == "Event"
        assert result.node_id == "evt-001"
        assert result.content == "Conflict in region X"
        assert result.evidence_text == ""
        assert result.score == 0.0
        assert result.traversal_path == []

    def test_all_fields(self) -> None:
        result = RetrievalResult(
            node_label="Company",
            node_id="cmp-042",
            content="Delta Air Lines",
            evidence_text="Crude oil price surge impacts fuel costs",
            score=0.95,
            traversal_path=["Event", "Commodity", "Company"],
        )
        assert result.score == 0.95
        assert result.traversal_path == ["Event", "Commodity", "Company"]

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            RetrievalResult(node_label="Event", node_id="evt-001")  # type: ignore[call-arg]


class TestSchemaInfo:
    """Tests for the SchemaInfo Pydantic model."""

    def test_minimal_fields(self) -> None:
        info = SchemaInfo(name="test_schema", graph_name="test_graph")
        assert info.name == "test_schema"
        assert info.description == ""
        assert info.graph_name == "test_graph"
        assert info.node_types == []
        assert info.edge_types == []
        assert info.traversal_patterns == []

    def test_all_fields(self) -> None:
        info = SchemaInfo(
            name="markets",
            description="Financial markets ontology",
            graph_name="markets_graph",
            node_types=["Event", "Company", "Commodity"],
            edge_types=["IMPACTS", "CONSUMES"],
            traversal_patterns=["impact_chain"],
        )
        assert len(info.node_types) == 3
        assert "IMPACTS" in info.edge_types

    def test_missing_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            SchemaInfo(graph_name="test_graph")  # type: ignore[call-arg]

    def test_missing_graph_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            SchemaInfo(name="test")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestSchemaHelpers:
    """Tests for schema directory helpers."""

    def test_resolve_schemas_dir_default(self) -> None:
        """Default schemas dir resolves to the repo-level schemas/ directory."""
        # Remove env override if set
        env_backup = os.environ.pop("SCHEMAS_DIR", None)
        try:
            result = _resolve_schemas_dir()
            assert os.path.isabs(result)
            assert result.endswith("schemas")
        finally:
            if env_backup is not None:
                os.environ["SCHEMAS_DIR"] = env_backup

    def test_resolve_schemas_dir_from_env(self, tmp_path: object) -> None:
        """SCHEMAS_DIR env var overrides the default."""
        custom = str(tmp_path)
        env_backup = os.environ.get("SCHEMAS_DIR")
        os.environ["SCHEMAS_DIR"] = custom
        try:
            assert _resolve_schemas_dir() == custom
        finally:
            if env_backup is not None:
                os.environ["SCHEMAS_DIR"] = env_backup
            else:
                del os.environ["SCHEMAS_DIR"]

    def test_list_schema_files(self) -> None:
        """Lists YAML files from the real schemas/ directory."""
        schemas_dir = _resolve_schemas_dir()
        if os.path.isdir(schemas_dir):
            names = _list_schema_files(schemas_dir)
            assert isinstance(names, list)
            # We know gdelt_markets.yaml exists
            assert "gdelt_markets" in names

    def test_load_schema_by_name(self) -> None:
        """Loads a schema by name from the real schemas/ directory."""
        schemas_dir = _resolve_schemas_dir()
        schema = _load_schema_by_name("gdelt_markets", schemas_dir)
        assert schema.name == "gdelt_markets"

    def test_load_schema_by_name_not_found(self) -> None:
        """Raises FileNotFoundError for a nonexistent schema."""
        schemas_dir = _resolve_schemas_dir()
        with pytest.raises(FileNotFoundError):
            _load_schema_by_name("nonexistent_schema", schemas_dir)


# ---------------------------------------------------------------------------
# Server factory tests
# ---------------------------------------------------------------------------


class TestCreateMcpServer:
    """Tests for the MCP server factory and tool registration."""

    def test_creates_server(self) -> None:
        server = create_mcp_server()
        assert server is not None
        assert server.name == "graph-rag"

    def test_custom_name(self) -> None:
        server = create_mcp_server(name="custom-rag")
        assert server.name == "custom-rag"

    def test_has_retrieve_tool(self) -> None:
        server = create_mcp_server()
        assert "retrieve" in server._tool_manager._tools

    def test_has_list_schemas_tool(self) -> None:
        server = create_mcp_server()
        assert "list_schemas" in server._tool_manager._tools

    def test_has_get_schema_info_tool(self) -> None:
        server = create_mcp_server()
        assert "get_schema_info" in server._tool_manager._tools

    def test_tool_count(self) -> None:
        """Server should have exactly 3 tools registered."""
        server = create_mcp_server()
        assert len(server._tool_manager._tools) == 3
