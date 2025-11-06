"""
Edit Configuration Page - Detail view for editing table configurations
"""

import streamlit as st
import pandas as pd
import json
from utils.database import update_table_config, update_DataSchema, fetch_table_list
from utils.table_config import TableConfig
from utils.config import CATALOG, SCHEMA, TABLE

# Page configuration
st.set_page_config(page_title="Edit Table Config", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

st.title("📝 Edit Table Configuration")

# Fetch all tables for dropdown options first
all_tables_df = fetch_table_list()

if all_tables_df is None or all_tables_df.empty:
    st.error("❌ Failed to load table list. Please check your database connection.")
    if st.button("⬅️ Back to Table List"):
        st.switch_page("app.py")
    st.stop()

# Get TableKey from query params or session state
query_params = st.query_params
table_key = query_params.get("table_key", None)

if not table_key and "selected_TableKey" in st.session_state:
    table_key = st.session_state.selected_TableKey

# Sidebar with navigation and info
with st.sidebar:
    st.header("🔧 Actions")

    if st.button("⬅️ Back to Table List", use_container_width=True):
        st.switch_page("app.py")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.divider()

    st.header("ℹ️ Table Information")
    st.markdown(f"**Catalog:** `{CATALOG}`")
    st.markdown(f"**Schema:** `{SCHEMA}`")
    st.markdown(f"**Table:** `{TABLE}`")

    st.divider()

    st.markdown(
        """
    ### Quick Guide
    - Select a table from the dropdowns
    - Edit configuration fields
    - Modify schema fields
    - Add/remove fields dynamically
    - Changes are saved immediately
    """
    )

# Get unique source systems
source_systems = sorted(all_tables_df["SourceSystem"].dropna().unique().tolist())

# Load config if table is selected
table_config = None
if table_key:
    table_config = TableConfig(table_key)
    if not table_config.is_loaded:
        st.error(f"❌ Failed to load configuration for table: {table_key}")
        table_key = None  # Reset to allow selection
        table_config = None

# Current values from config or defaults
current_source_system = table_config.source_system if table_config else (source_systems[0] if source_systems else "")
current_table_key = table_config.table_key if table_config else ""
current_table_name = table_config.table_name if table_config else ""

# Main content
st.header("🔍 Select Table to Edit")

if not table_key:
    st.info("💡 No table selected. Please select a table from the dropdowns below.")

# Table selection dropdowns
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    selected_source_system = st.selectbox(
        "Source System",
        options=source_systems,
        index=source_systems.index(current_source_system) if current_source_system in source_systems else 0,
        key="source_system_selector",
        help="Select the source system to filter tables",
    )

# Filter tables by selected source system
filtered_tables = all_tables_df[all_tables_df["SourceSystem"] == selected_source_system]
table_keys = filtered_tables["TableKey"].tolist()
table_names = filtered_tables["TableName"].tolist()

# Create a mapping for display
table_options = [f"{key} - {name}" for key, name in zip(table_keys, table_names)]
current_option = f"{current_table_key} - {current_table_name}"

# Determine default index - use current if in filtered list, otherwise 0
if selected_source_system == current_source_system and current_option in table_options:
    default_index = table_options.index(current_option)
else:
    default_index = 0

with col2:
    selected_table_option = st.selectbox(
        "Table Key - Table Name", options=table_options, index=default_index, key="table_selector", help="Select the table to edit"
    )

with col3:
    # Extract the selected table key from the option
    selected_table_key = selected_table_option.split(" - ")[0] if selected_table_option else ""
    if selected_table_key:
        # Navigate button or info
        if selected_table_key != current_table_key:
            # Add matching label for alignment
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)  # Match label height
            if st.button("🔄 Load This Table", use_container_width=True, type="primary"):
                st.query_params["table_key"] = selected_table_key
                st.session_state.selected_TableKey = selected_table_key
                st.rerun()
        else:
            # Use container with markdown for better alignment
            st.markdown('<p style="margin-top: 33px; margin-bottom: 0;">✓ Currently viewing</p>', unsafe_allow_html=True)
st.divider()

# Show current editing table info or prompt to select
if table_config:
    st.caption(f"Currently editing: **{current_source_system}** / **{current_table_key}** / **{current_table_name}**")
else:
    st.caption("Click '🔄 Load This Table' to start editing the selected table")

st.divider()

# Only show configuration editor if a table is loaded
if not table_config:
    st.info("👆 Please select a table above to view and edit its configuration")
    st.stop()

# Display current configuration keys
st.subheader("🔑 Current Configuration Keys")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Primary Keys**")
    current_pk_list = table_config.primary_keys
    print("current_pk_list", type(current_pk_list))
    if current_pk_list:
        for pk in current_pk_list:
            st.markdown(f"• `{pk}`")
    else:
        st.caption("_No primary keys set_")

with col2:
    st.markdown("**SCD Join Keys**")
    current_scd_join_list = table_config.scd_join_keys
    if current_scd_join_list:
        for key in current_scd_join_list:
            st.markdown(f"• `{key}`")
    else:
        st.caption("_No SCD join keys set_")

with col3:
    st.markdown("**SCD Sequence Keys**")
    current_scd_seq_list = table_config.scd_sequence_keys
    if current_scd_seq_list:
        for key in current_scd_seq_list:
            st.markdown(f"• `{key}`")
    else:
        st.caption("_No SCD sequence keys set_")

st.divider()

# Display DataSchema editor
st.subheader("🔧 Data Schema")
st.info("💡 Check the boxes in each row to mark fields as Primary Keys, SCD Join Keys, or SCD Sequence Keys. These will be saved when you save the schema.")

if table_config.dataschema_str:
    # Get schema as DataFrame with configuration columns
    schema_df = table_config.get_schema_dataframe()

    if not schema_df.empty:
        st.markdown("**Edit the schema fields below:**")

        # Show info about metadata fields if present
        metadata_cols = [col for col in schema_df.columns if col.startswith("metadata.")]
        if metadata_cols:
            st.info(f"💡 This schema includes {len(metadata_cols)} metadata field(s): {', '.join([col.replace('metadata.', '') for col in metadata_cols])}")
        else:
            st.info("💡 Add rows to add new fields, delete rows to remove fields, edit cells to modify field definitions.")

        # Build column configuration dynamically
        column_config = {
            "Source Name": st.column_config.TextColumn(
                "Source Name",
                help="Original field name in the source system",
                required=False,
            ),
            "Target Name": st.column_config.TextColumn(
                "Target Name",
                help="Target field name in the destination",
                required=True,
            ),
            "Data Type": st.column_config.SelectboxColumn(
                "Data Type",
                help="Data type of the field",
                options=[
                    "string",
                    "integer",
                    "long",
                    "double",
                    "float",
                    "boolean",
                    "date",
                    "timestamp",
                    "decimal",
                    "array",
                    "struct",
                    "map",
                ],
                required=True,
            ),
            "Nullable": st.column_config.CheckboxColumn(
                "Nullable",
                help="Can this field contain null values?",
                required=True,
            ),
            "Is Primary Key": st.column_config.CheckboxColumn(
                "Is Primary Key",
                help="Mark this field as part of the primary key",
                width="small",
            ),
            "Is SCD Join Key": st.column_config.CheckboxColumn(
                "Is SCD Join Key",
                help="Mark this field as an SCD join key",
                width="small",
            ),
            "Is SCD Sequence Key": st.column_config.CheckboxColumn(
                "Is SCD Sequence Key",
                help="Mark this field as an SCD sequence key",
                width="small",
            ),
            "Comment": st.column_config.TextColumn(
                "Comment",
                help="Description or comment for this field",
                width="large",
            ),
        }

        # Add configuration for metadata columns with automatic type detection
        for col in schema_df.columns:
            if col.startswith("metadata."):
                metadata_key = col.replace("metadata.", "")

        # Editable dataframe for schema
        edited_schema_df = st.data_editor(
            schema_df[
                [
                    "Source Name",
                    "Target Name",
                    "Data Type",
                    "Nullable",
                    "Is Primary Key",
                    "Is SCD Join Key",
                    "Is SCD Sequence Key",
                    "Comment",
                ]
            ],
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="schema_editor",  # Allow adding/deleting rows
        )

        # Save button
        col1, col2, col3 = st.columns([1, 1, 4])

        with col1:
            if st.button("💾 Save Schema Changes", type="primary", use_container_width=True):
                # Convert edited dataframe back to schema format
                # This now returns a tuple: (fields, primary_keys, scd_join_keys, scd_sequence_keys)
                new_dataschema, primary_keys, scd_join_keys, scd_sequence_keys = table_config.convert_dataframe_to_schema(edited_schema_df)

                # Update DataSchema
                schema_updated = update_DataSchema(table_config.table_key, new_dataschema)

                # Update configuration keys
                config_updates = {
                    "PrimaryKeys": ",".join(primary_keys) if primary_keys else None,
                    "ScdJoinKeys": ",".join(scd_join_keys) if scd_join_keys else None,
                    "ScdSequenceKeys": ",".join(scd_sequence_keys) if scd_sequence_keys else None,
                }
                config_updated = update_table_config(table_config.table_key, config_updates)

                if schema_updated and config_updated:
                    st.success("✅ Schema and configuration updated successfully!")
                    st.cache_resource.clear()
                    st.rerun()
                elif schema_updated:
                    st.warning("⚠️ Schema updated, but configuration keys failed to update")
                    st.cache_resource.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to update schema")

        with col2:
            if st.button("↩️ Reset", use_container_width=True):
                st.rerun()

        # Show raw JSON and schema statistics
        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Fields", len(schema_df))
        with col2:
            nullable_count = schema_df["Nullable"].sum() if "Nullable" in schema_df.columns else 0
            st.metric("Nullable Fields", nullable_count)
        with col3:
            has_comment = schema_df["Comment"].notna().sum() if "Comment" in schema_df.columns else 0
            st.metric("With Comments", has_comment)
        with col4:
            metadata_cols_count = len([col for col in schema_df.columns if col.startswith("metadata.")])
            st.metric("Metadata Fields", metadata_cols_count)

        st.divider()
        with st.expander("🔍 View Raw JSON Schema"):
            st.code(json.dumps(table_config.schema_fields, indent=2), language="json")

    else:
        st.warning("⚠️ Could not parse DataSchema. Showing raw value:")
        st.text_area("Raw Dataschema", table_config.dataschema_str, height=200, disabled=True)

else:
    st.warning("⚠️ No DataSchema defined for this table.")

    # Allow adding a new schema
    if st.button("➕ Add Schema Fields"):
        # Create empty schema with one field and configuration columns
        empty_df = pd.DataFrame(
            [
                {
                    "Field Name": "new_field",
                    "Data Type": "string",
                    "Nullable": True,
                    "Is Primary Key": False,
                    "Is SCD Join Key": False,
                    "Is SCD Sequence Key": False,
                    "Comment": "",
                }
            ]
        )

        edited_schema_df = st.data_editor(
            empty_df,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="new_schema_editor",
            column_config={
                "Field Name": st.column_config.TextColumn("Field Name", required=True),
                "Data Type": st.column_config.SelectboxColumn(
                    "Data Type",
                    options=[
                        "string",
                        "integer",
                        "long",
                        "double",
                        "float",
                        "boolean",
                        "date",
                        "timestamp",
                        "decimal",
                        "array",
                        "struct",
                        "map",
                    ],
                    required=True,
                ),
                "Nullable": st.column_config.CheckboxColumn("Nullable", required=True),
                "Is Primary Key": st.column_config.CheckboxColumn("Is Primary Key", width="small"),
                "Is SCD Join Key": st.column_config.CheckboxColumn("Is SCD Join Key", width="small"),
                "Is SCD Sequence Key": st.column_config.CheckboxColumn("Is SCD Sequence Key", width="small"),
                "Comment": st.column_config.TextColumn("Comment"),
            },
        )

        if st.button("💾 Save New Schema", type="primary"):
            new_dataschema, primary_keys, scd_join_keys, scd_sequence_keys = table_config.convert_dataframe_to_schema(edited_schema_df)

            # Update DataSchema
            schema_updated = update_DataSchema(table_config.table_key, new_dataschema)

            # Update configuration keys if any
            if primary_keys or scd_join_keys or scd_sequence_keys:
                config_updates = {
                    "PrimaryKeys": ",".join(primary_keys) if primary_keys else None,
                    "ScdJoinKeys": ",".join(scd_join_keys) if scd_join_keys else None,
                    "ScdSequenceKeys": ",".join(scd_sequence_keys) if scd_sequence_keys else None,
                }
                update_table_config(table_config.table_key, config_updates)

            if schema_updated:
                st.success("✅ Schema created successfully!")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.error("❌ Failed to create schema")
