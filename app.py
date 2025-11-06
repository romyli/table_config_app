"""
Databricks App - Table Configuration Editor (Main Page)
Streamlit app for viewing and selecting table configurations
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.database import fetch_table_list, get_connection
from utils.config import CATALOG, SCHEMA, TABLE

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Table Config Editor", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")


def main():
    """
    Main application logic - Table list view
    """
    st.title("⚙️ Table Configuration Editor")
    st.markdown(f"**Catalog:** `{CATALOG}` | **Schema:** `{SCHEMA}` | **Table:** `{TABLE}`")

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    # Sidebar
    with st.sidebar:
        st.header("🔧 Actions")

        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_resource.clear()
            st.session_state.current_page = 0
            st.rerun()

        st.divider()

        st.header("ℹ️ Information")
        st.markdown(
            """
        This app allows you to:
        - View all table configurations
        - Click on "View →" to edit details
        - Edit configuration fields
        - Modify DataSchema fields
        
        **Note:** Changes are immediately saved to Databricks.
        """
        )

        # Show connection status
        st.divider()
        conn = get_connection()
        if conn:
            st.success("✅ Connected to Databricks")
        else:
            st.error("❌ Not connected")

    # Main content - List View
    st.header("📊 Table Configurations")

    df = fetch_table_list()

    if df is not None and not df.empty:
        # st.info(f"📋 Total tables: {len(df)}") #to remove

        # Display summary table without DataSchema (it's too long)
        display_df = df[["TableKey", "SourceSystem", "TableName"]].copy()

        # Get distinct pipeline names for dropdown
        distinct_pipelines = sorted(display_df["SourceSystem"].dropna().unique().tolist())
        pipeline_options = ["All"] + distinct_pipelines

        # Create a container for the table
        st.markdown("**Click on a row to view and edit the DataSchema:**")

        # Display column headers
        col1, col2, col3, col4 = st.columns([2, 3, 3, 1])
        with col1:
            st.markdown("**Source System**")
        with col2:
            st.markdown("**Table Key**")
        with col3:
            st.markdown("**Table Name**")
        with col4:
            st.markdown("**Action**")

        # Create three columns for the search inputs
        # search_col1, search_col2, search_col3, search_col4 = st.columns([2, 3, 3, 1])

        with col1:
            pipeline_search = st.selectbox("Source System", options=pipeline_options, index=0, key="pipeline_search", label_visibility="collapsed")

        with col2:
            tablekey_search = st.text_input("Table Key", placeholder="Filter by table key...", key="tablekey_search", label_visibility="collapsed")

        with col3:
            tablename_search = st.text_input("Table Name", placeholder="Filter by table name...", key="tablename_search", label_visibility="collapsed")

        # Filter the dataframe based on search terms
        filtered_df = display_df.copy()
        active_filters = []

        # Track filter state to reset pagination when filters change
        current_filters = f"{pipeline_search}|{tablekey_search}|{tablename_search}"
        if "last_filters" not in st.session_state:
            st.session_state.last_filters = current_filters
        elif st.session_state.last_filters != current_filters:
            st.session_state.current_page = 0
            st.session_state.last_filters = current_filters

        if pipeline_search and pipeline_search != "All":
            filtered_df = filtered_df[filtered_df["SourceSystem"] == pipeline_search]
            active_filters.append(f"Source System: '{pipeline_search}'")

        if tablekey_search:
            filtered_df = filtered_df[filtered_df["TableKey"].astype(str).str.contains(tablekey_search, case=False, na=False)]
            active_filters.append(f"Table Key: '{tablekey_search}'")

        if tablename_search:
            filtered_df = filtered_df[filtered_df["TableName"].astype(str).str.contains(tablename_search, case=False, na=False)]
            active_filters.append(f"Table Name: '{tablename_search}'")

        # Pagination setup
        ROWS_PER_PAGE = 10
        total_rows = len(filtered_df)
        total_pages = (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE  # Ceiling division

        # Reset to first page if current page is out of bounds
        if st.session_state.current_page >= total_pages and total_pages > 0:
            st.session_state.current_page = 0

        # Show filtered count if any search is active
        if active_filters:
            st.caption(f"Showing {len(filtered_df)} of {len(display_df)} tables (Filters: {', '.join(active_filters)})")

        # Display table with click functionality
        if not filtered_df.empty:
            # Calculate start and end indices for current page
            start_idx = st.session_state.current_page * ROWS_PER_PAGE
            end_idx = min(start_idx + ROWS_PER_PAGE, total_rows)

            # Slice the dataframe for current page
            page_df = filtered_df.iloc[start_idx:end_idx]

            # Show pagination info
            st.caption(f"Showing rows {start_idx + 1}-{end_idx} of {total_rows} tables")

            # Display rows for current page
            for idx, row in page_df.iterrows():
                col1, col2, col3, col4 = st.columns([2, 3, 3, 1])

                with col1:
                    st.text(row["SourceSystem"])
                with col2:
                    st.text(row["TableKey"])
                with col3:
                    st.text(row["TableName"])
                with col4:
                    if st.button("View →", key=f"view_{row['TableKey']}", use_container_width=True):
                        # Navigate to edit page with query parameter
                        st.query_params["table_key"] = row["TableKey"]
                        st.session_state.selected_TableKey = row["TableKey"]
                        st.switch_page("pages/1_Edit_Config.py")

            # Pagination controls
            if total_pages > 1:
                st.divider()
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("⏮️ First", disabled=(st.session_state.current_page == 0), use_container_width=True):
                        st.session_state.current_page = 0
                        st.rerun()

                with col2:
                    if st.button("◀️ Previous", disabled=(st.session_state.current_page == 0), use_container_width=True):
                        st.session_state.current_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(
                        f"<div style='text-align: center; padding-top: 5px;'>Page {st.session_state.current_page + 1} of {total_pages}</div>",
                        unsafe_allow_html=True,
                    )

                with col4:
                    if st.button("Next ▶️", disabled=(st.session_state.current_page >= total_pages - 1), use_container_width=True):
                        st.session_state.current_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last ⏭️", disabled=(st.session_state.current_page >= total_pages - 1), use_container_width=True):
                        st.session_state.current_page = total_pages - 1
                        st.rerun()
        else:
            st.warning(f"⚠️ No tables found matching the selected filters")

        # Export option
        st.divider()
        # with st.expander("📥 Export Data"):
        #     csv = df.to_csv(index=False)
        #     st.download_button(label="Download Full Config as CSV", data=csv, file_name=f"{TABLE}_export.csv", mime="text/csv")

    elif df is not None and df.empty:
        st.warning("⚠️ No table configurations found.")
    else:
        st.error("Failed to load data. Please check your connection.")


if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ["DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        st.info(
            """
        Please create a `.env` file with the following variables:
        ```
        DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
        DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
        DATABRICKS_TOKEN=your-personal-access-token
        ```
        """
        )
    else:
        main()
