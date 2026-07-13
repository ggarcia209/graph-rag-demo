"""YAML schema loader for ontology definitions.

Loads a YAML file, validates it against the Pydantic OntologySchema model,
and returns a fully typed schema instance.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from src.schema.models import OntologySchema


def load_schema(path: str | Path) -> OntologySchema:
    """Load and validate an ontology schema from a YAML file.

    Args:
        path: Path to the YAML schema file.

    Returns:
        A validated OntologySchema instance.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        ValueError: If the YAML is malformed or fails Pydantic validation.
    """
    schema_path = Path(path)

    if not schema_path.exists():
        raise FileNotFoundError(f"load_schema: schema file not found: {schema_path}")

    if not schema_path.is_file():
        raise ValueError(f"load_schema: path is not a file: {schema_path}")

    try:
        raw = schema_path.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"load_schema: failed to read file: {e}") from e

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise ValueError(f"load_schema: invalid YAML: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(
            f"load_schema: expected a YAML mapping at top level, got {type(data).__name__}"
        )

    try:
        schema = OntologySchema.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"load_schema: schema validation failed: {e}") from e

    return schema
