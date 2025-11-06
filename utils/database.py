"""
Database utility functions for Databricks connectivity and operations
"""

import streamlit as st
import pandas as pd
from databricks import sql
import os
import json
from dotenv import load_dotenv
from utils.config import FULL_TABLE_NAME

# Load environment variables
load_dotenv()


@st.cache_resource
def get_connection():
    """
    Create a connection to Databricks SQL warehouse.
    Uses environment variables for credentials.
    """
    try:
        connection = sql.connect(
            server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"), http_path=os.getenv("DATABRICKS_HTTP_PATH"), access_token=os.getenv("DATABRICKS_TOKEN")
        )
        return connection
    except Exception as e:
        st.error(f"❌ Failed to connect to Databricks: {str(e)}")
        st.info("Please check your .env file has the correct credentials")
        return None


def fetch_table_list():
    """
    Fetch TableKey, SourceSystem, and TableName from the configuration table.
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = f"SELECT TableKey, SourceSystem, TableName, DataSchema FROM {FULL_TABLE_NAME} ORDER BY SourceSystem, TableName"
        cursor.execute(query)

        # Fetch data and column names
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()

        cursor.close()

        # Convert to pandas DataFrame
        df = pd.DataFrame(data, columns=columns)
        return df

    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return None


def fetch_table_config(TableKey):
    """
    Fetch full configuration for a specific table.
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = f"SELECT * FROM {FULL_TABLE_NAME} WHERE TableKey = '{TableKey}'"
        cursor.execute(query)

        # Fetch data and column names
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchone()

        cursor.close()

        if data:
            return dict(zip(columns, data))
        return None

    except Exception as e:
        st.error(f"❌ Error fetching table config: {str(e)}")
        return None


def get_table_schema():
    """
    Get the schema information for the table.
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = f"DESCRIBE {FULL_TABLE_NAME}"
        cursor.execute(query)

        schema_data = cursor.fetchall()
        cursor.close()

        # Parse schema information
        schema_df = pd.DataFrame(schema_data, columns=["col_name", "data_type", "comment"])
        return schema_df

    except Exception as e:
        st.error(f"❌ Error fetching schema: {str(e)}")
        return None


def update_DataSchema(TableKey, new_schema):
    """
    Update the DataSchema for a specific table.

    Args:
        TableKey: The table key to identify the row
        new_schema: New schema (as list of field dicts or JSON string)
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Convert schema to JSON string if it's not already
        if isinstance(new_schema, (list, dict)):
            schema_str = json.dumps(new_schema)
        else:
            schema_str = new_schema

        # Build UPDATE query
        query = f"""
        UPDATE {FULL_TABLE_NAME}
        SET DataSchema = '{schema_str}'
        WHERE TableKey = '{TableKey}'
        """

        cursor.execute(query)
        cursor.close()

        return True

    except Exception as e:
        st.error(f"❌ Error updating DataSchema: {str(e)}")
        return False


def update_table_config(TableKey, updates):
    """
    Update multiple fields for a specific table.

    Args:
        TableKey: The table key to identify the row
        updates: Dictionary with field names and their new values
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Build SET clause from updates dictionary
        set_clauses = []
        for field, value in updates.items():
            if value is None:
                set_clauses.append(f"{field} = NULL")
            elif isinstance(value, (list, dict)):
                # Convert to JSON string for complex types
                value_str = json.dumps(value).replace("'", "''")
                set_clauses.append(f"{field} = '{value_str}'")
            else:
                # Escape single quotes in string values
                value_str = str(value).replace("'", "''")
                set_clauses.append(f"{field} = '{value_str}'")

        set_clause = ", ".join(set_clauses)

        # Build UPDATE query
        query = f"""
        UPDATE {FULL_TABLE_NAME}
        SET {set_clause}
        WHERE TableKey = '{TableKey}'
        """

        cursor.execute(query)
        cursor.close()

        return True

    except Exception as e:
        st.error(f"❌ Error updating table config: {str(e)}")
        return False


def insert_row(row_data):
    """
    Insert a new row into the table.

    Args:
        row_data: Dictionary with column-value pairs
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        columns = ", ".join(row_data.keys())
        values = ", ".join([f"'{v}'" for v in row_data.values()])

        query = f"""
        INSERT INTO {FULL_TABLE_NAME} ({columns})
        VALUES ({values})
        """

        cursor.execute(query)
        conn.commit()
        cursor.close()

        return True

    except Exception as e:
        st.error(f"❌ Error inserting data: {str(e)}")
        return False


def delete_row(row_identifier):
    """
    Delete a row from the table.

    Args:
        row_identifier: Dictionary with column-value pairs to identify the row
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        where_conditions = " AND ".join([f"{k} = '{v}'" for k, v in row_identifier.items()])

        query = f"""
        DELETE FROM {FULL_TABLE_NAME}
        WHERE {where_conditions}
        """

        cursor.execute(query)
        conn.commit()
        cursor.close()

        return True

    except Exception as e:
        st.error(f"❌ Error deleting data: {str(e)}")
        return False
