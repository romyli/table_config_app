"""
TableConfig class for managing table configuration operations
"""

import json
import pandas as pd
from utils.database import fetch_table_config as db_fetch_table_config


class TableConfig:
    """
    Class to manage table configuration including schema parsing and key management
    """

    def __init__(self, table_key):
        """
        Initialize TableConfig with a table key

        Args:
            table_key: The unique identifier for the table
        """
        self.table_key = table_key
        self._config = None
        self._dataschema = []
        self._dataschema_str = ""
        self._displayed_schema = []
        self._primary_keys = []
        self._scd_join_keys = []
        self._scd_sequence_keys = []
        self._load_config()

    def _load_config(self):
        """Load configuration from database"""
        self._config = db_fetch_table_config(self.table_key)

        if self._config:
            # Get and parse primary keys, SCD join keys, and SCD sequence keys
            self._primary_keys = self.parse_key_list("PrimaryKeys")
            self._scd_join_keys = self.parse_key_list("ScdJoinKeys")
            self._scd_sequence_keys = self.parse_key_list("ScdSequenceKeys")

            # Parse DataSchema (store both raw string and parsed list)
            self._dataschema_str = self._config.get("DataSchema", "")
            self._dataschema = self._parse_dataschema(self._dataschema_str)

    def parse_key_list(self, key_name):
        """
        Parse a configuration key (PrimaryKeys, ScdJoinKeys, etc.) into a list

        Args:
            key_name: Name of the key field to parse

        Returns:
            List of key values
        """
        if not self._config:
            return []

        value = self._config.get(key_name, "")

        try:
            if isinstance(value, str) and value.startswith("["):
                parsed = json.loads(value)
            else:
                parsed = str(value).split(",")
            return [k.strip() for k in parsed if k.strip()]
        except:
            return [k.strip() for k in str(value).split(",") if k.strip()]

    def _parse_dataschema(self, dataschema_str):
        """
        Parse DataSchema string (JSON or other format) into a structured format.
        Returns a list of dictionaries representing fields.

        Args:
            dataschema_str: DataSchema string to parse

        Returns:
            List of field dictionaries
        """
        if not dataschema_str:
            return []

        try:
            # Try parsing as JSON
            schema = json.loads(dataschema_str)

            # If it's a dict with fields
            if isinstance(schema, dict) and "fields" in schema:
                self._displayed_schema = schema["fields"]
                return schema["fields"]
            return []
        except json.JSONDecodeError:
            # If not JSON, try to parse as comma-separated key:value pairs
            raise ValueError("Invalid DataSchema string")

    @staticmethod
    def schema_to_dataframe(schema_fields, primary_keys=None, scd_join_keys=None, scd_sequence_keys=None):
        """
        Convert schema fields to a pandas DataFrame for display.
        Extracts metadata fields into separate columns.
        Adds configuration columns for PrimaryKey, ScdJoinKey, ScdSequenceKey.

        Args:
            schema_fields: List of field dictionaries
            primary_keys: List of field names that are primary keys
            scd_join_keys: List of field names that are SCD join keys
            scd_sequence_keys: List of field names that are SCD sequence keys

        Returns:
            pandas DataFrame with schema and configuration columns
        """
        if not schema_fields:
            # Return empty DataFrame with all standard columns
            return pd.DataFrame(
                columns=["Source Name", "Target Name", "Data Type", "Nullable", "Is Primary Key", "Is SCD Join Key", "Is SCD Sequence Key", "Comment"]
            )

        # Convert to sets for faster lookup
        primary_keys_set = set(primary_keys or [])
        scd_join_keys_set = set(scd_join_keys or [])
        scd_sequence_keys_set = set(scd_sequence_keys or [])

        rows = []
        all_metadata_keys = set()

        # First pass: collect all metadata keys from all fields
        for field in schema_fields:
            if isinstance(field, dict):
                metadata = field.get("metadata", {})
                if isinstance(metadata, dict):
                    all_metadata_keys.update(metadata.keys())

        # Build rows with all metadata fields
        for field in schema_fields:
            if isinstance(field, dict):
                row = {
                    "Data Type": field.get("type", ""),
                    "Nullable": field.get("nullable", True),
                }
                # Get metadata
                metadata = field.get("metadata", {})
                if not isinstance(metadata, dict):
                    metadata = {}
                target_name = metadata.get("target_name", "")
                # Add Comment column first (always present, from metadata.comment)
                row["Comment"] = metadata.get("comment", "")

                # Add source_name and target_name columns
                row["Source Name"] = metadata.get("source_name", "")
                row["Target Name"] = target_name
                row["Is Primary Key"] = metadata.get("is_primary_key", "")

                row["Is SCD Join Key"] = True if target_name in scd_join_keys_set else False
                row["Is SCD Sequence Key"] = True if target_name in scd_sequence_keys_set else False

                # Add all other metadata fields as separate columns, preserving types
                for key in sorted(all_metadata_keys):
                    if key not in ["comment", "source_name", "target_name", "is_primary_key"]:  # Comment is already added as a top-level column
                        metadata_col = f"metadata.{key}"
                        value = metadata.get(key, "")
                        # Preserve the original type (boolean, number, string)
                        row[metadata_col] = value if value != "" else ""

                rows.append(row)

        return pd.DataFrame(rows)

    @staticmethod
    def dataframe_to_schema(df, original_schema_fields=None):
        """
        Convert edited DataFrame back to schema format.
        Reconstructs metadata from separate columns.
        Extracts configuration fields (Primary Keys, SCD Join Keys, SCD Sequence Keys).
        Merges with original schema fields to preserve non-editable metadata.

        Args:
            df: pandas DataFrame with edited schema
            original_schema_fields: List of original field dictionaries to preserve non-editable metadata

        Returns:
            tuple: (fields, primary_keys_list, scd_join_keys_list, scd_sequence_keys_list)
        """
        # Create a lookup of original fields by target_name
        original_fields_map = {}
        if original_schema_fields:
            for field in original_schema_fields:
                if isinstance(field, dict):
                    metadata = field.get("metadata", {})
                    if isinstance(metadata, dict):
                        target_name = metadata.get("target_name", field.get("name", ""))
                        original_fields_map[target_name] = field

        fields = []
        primary_keys = []
        scd_join_keys = []
        scd_sequence_keys = []

        for _, row in df.iterrows():
            field_name = row["Target Name"]

            # Start with the original field if it exists, to preserve all metadata
            if field_name in original_fields_map:
                field = json.loads(json.dumps(original_fields_map[field_name]))  # Deep copy
            else:
                # New field, create from scratch
                field = {
                    "name": field_name,
                    "type": row["Data Type"],
                    "nullable": True,
                    "metadata": {},
                }

            # Update with edited values from the DataFrame
            field["type"] = row["Data Type"]
            field["nullable"] = bool(row["Nullable"]) if not isinstance(row["Nullable"], str) else str(row["Nullable"]).lower() == "true"

            # Ensure metadata dict exists
            if "metadata" not in field:
                field["metadata"] = {}

            # Update editable metadata fields
            if "Source Name" in row and pd.notna(row["Source Name"]) and row["Source Name"]:
                field["metadata"]["source_name"] = row["Source Name"]

            if "Target Name" in row and pd.notna(row["Target Name"]) and row["Target Name"]:
                field["metadata"]["target_name"] = row["Target Name"]

            if "Comment" in row and pd.notna(row["Comment"]) and row["Comment"]:
                field["metadata"]["comment"] = row["Comment"]
            elif "Comment" in row and (not pd.notna(row["Comment"]) or not row["Comment"]):
                # Remove comment if it was cleared
                if "comment" in field["metadata"]:
                    del field["metadata"]["comment"]

            if "Is Primary Key" in row and pd.notna(row["Is Primary Key"]):
                field["metadata"]["is_primary_key"] = bool(row["Is Primary Key"])

            # Add other metadata fields that start with "metadata." (if any were displayed)
            for col in df.columns:
                if col.startswith("metadata.") and pd.notna(row[col]):
                    metadata_key = col.replace("metadata.", "")
                    value = row[col]
                    # Only add non-empty values (but keep boolean False and numeric 0)
                    if value is not None and (isinstance(value, (bool, int, float)) or value != ""):
                        field["metadata"][metadata_key] = value

            fields.append(field)

            # Extract configuration flags
            if "Is Primary Key" in row and row["Is Primary Key"]:
                primary_keys.append(field_name)
            if "Is SCD Join Key" in row and row["Is SCD Join Key"]:
                scd_join_keys.append(field_name)
            if "Is SCD Sequence Key" in row and row["Is SCD Sequence Key"]:
                scd_sequence_keys.append(field_name)

        return {"fields": fields}, json.dumps(primary_keys), json.dumps(scd_join_keys), json.dumps(scd_sequence_keys)

    @property
    def config(self):
        """Get the raw configuration dictionary"""
        return self._config

    @property
    def is_loaded(self):
        """Check if configuration was successfully loaded"""
        return self._config is not None

    @property
    def source_system(self):
        """Get the source system name"""
        return self._config.get("SourceSystem", "") if self._config else ""

    @property
    def table_name(self):
        """Get the table name"""
        return self._config.get("TableName", "") if self._config else ""

    @property
    def schema_fields(self):
        """Get parsed schema fields"""
        return self._dataschema or []

    @property
    def dataschema_str(self):
        """Get raw DataSchema string"""
        return self._dataschema_str

    def get_field_names(self):
        """
        Get list of field names from the schema

        Returns:
            List of field names
        """
        if not self._dataschema:
            return []
        return [field.get("name", "") for field in self._dataschema if isinstance(field, dict) and field.get("name")]

    @property
    def primary_keys(self):
        """Get list of primary keys"""
        return self._primary_keys

    @property
    def scd_join_keys(self):
        """Get list of SCD join keys"""
        return self._scd_join_keys

    @property
    def scd_sequence_keys(self):
        """Get list of SCD sequence keys"""
        return self._scd_sequence_keys

    def get_schema_dataframe(self):
        """
        Get schema as a pandas DataFrame with configuration columns

        Returns:
            pandas DataFrame with schema and configuration columns
        """
        if not self._dataschema:
            return pd.DataFrame(
                columns=["Source Name", "Target Name", "Data Type", "Nullable", "Is Primary Key", "Is SCD Join Key", "Is SCD Sequence Key", "Comment"]
            )

        return self.schema_to_dataframe(
            self._dataschema, primary_keys=self.primary_keys, scd_join_keys=self.scd_join_keys, scd_sequence_keys=self.scd_sequence_keys
        )

    def convert_dataframe_to_schema(self, df):
        """
        Convert edited DataFrame back to schema format and extract configuration keys.
        Preserves all original metadata fields that weren't displayed in the UI.

        Args:
            df: pandas DataFrame with edited schema

        Returns:
            tuple: (schema_fields, primary_keys, scd_join_keys, scd_sequence_keys)
        """
        # Pass the original schema fields to preserve non-editable metadata
        return self.dataframe_to_schema(df, self._dataschema)

    def get_value(self, key, default=""):
        """
        Get a value from config with optional default

        Args:
            key: Configuration key name
            default: Default value if key not found

        Returns:
            Value from config or default
        """
        return self._config.get(key, default) if self._config else default

    def refresh(self):
        """Reload configuration from database"""
        self._load_config()

    def __repr__(self):
        """String representation of TableConfig"""
        if self.is_loaded:
            return f"TableConfig(table_key='{self.table_key}', source_system='{self.source_system}', table_name='{self.table_name}')"
        return f"TableConfig(table_key='{self.table_key}', loaded=False)"
