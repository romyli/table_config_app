# Table Configuration Editor

A Streamlit web application for viewing and managing table configurations stored in Databricks. This tool provides an intuitive interface for editing table schemas, managing primary keys, and handling Slowly Changing Dimension (SCD) configurations.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Main Features

- **Table Configuration Browser**
  - View all table configurations in a paginated list
  - Filter by Source System, Table Key, and Table Name
  - Real-time search and filtering capabilities
  - Pagination support (10 rows per page)

- **Interactive Schema Editor**
  - Edit DataSchema fields with an intuitive data editor
  - Add or remove schema fields dynamically
  - Modify field properties (name, data type, nullable, comments)
  - Visual representation of schema fields

- **Key Management**
  - Configure Primary Keys through UI checkboxes
  - Set SCD (Slowly Changing Dimension) Join Keys
  - Define SCD Sequence Keys
  - Automatic synchronization with schema changes

- **Data Type Support**
  - String, Integer, Long, Double, Float
  - Boolean, Date, Timestamp
  - Decimal, Array, Struct, Map

- **Metadata Preservation**
  - Preserves existing metadata during schema edits
  - Displays metadata fields as separate columns
  - Supports custom metadata fields

- **Real-time Updates**
  - Changes are immediately saved to Databricks
  - Automatic cache refresh after updates
  - Connection status monitoring

### User Interface Features

- Clean, modern UI built with Streamlit
- Wide layout for better data visibility
- Sidebar navigation with quick actions
- Inline help text and tooltips
- Success/error notifications
- Raw JSON schema viewer

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Databricks workspace** with SQL Warehouse access
- **Databricks personal access token**

### Databricks Requirements

- Access to a Databricks workspace
- SQL Warehouse configured and running
- Table with the following schema structure:
  - `TableKey` (identifier)
  - `SourceSystem` (source system name)
  - `TableName` (table name)
  - `DataSchema` (JSON schema definition)
  - `PrimaryKeys` (comma-separated or JSON array)
  - `ScdJoinKeys` (comma-separated or JSON array)
  - `ScdSequenceKeys` (comma-separated or JSON array)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd table_config_app
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Streamlit (web framework)
- Databricks SQL Connector (database connectivity)
- Pandas & NumPy (data processing)
- Python-dotenv (environment management)
- Plotly & Altair (visualization)
- OpenPyXL & XlsxWriter (Excel export support)
- Development tools (Black, Flake8, Pytest)

## ⚙️ Configuration

### 1. Environment Variables

Copy the template file and create your `.env` file:

```bash
cp env.template .env
```

### 2. Configure Databricks Connection

Edit the `.env` file with your Databricks credentials:

```bash
# Databricks SQL Warehouse Connection
DATABRICKS_SERVER_HOSTNAME=adb-1234567890123456.7.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Optional: Environment Configuration
ENVIRONMENT=dev
LOG_LEVEL=INFO
```

#### How to Get Databricks Credentials:

1. **Server Hostname & HTTP Path:**
   - Go to your Databricks workspace
   - Navigate to **SQL Warehouses**
   - Click on your warehouse
   - Go to **Connection Details** tab
   - Copy the Server hostname and HTTP path

2. **Access Token:**
   - In Databricks, click your username in the top right
   - Select **User Settings**
   - Go to **Access Tokens** tab
   - Click **Generate New Token**
   - Copy and save the token securely

### 3. Configure Target Table

Edit `utils/config.py` to point to your configuration table:

```python
CATALOG = "your_catalog"
SCHEMA = "your_schema"
TABLE = "your_table_config"
```

### 4. Security Notes

⚠️ **IMPORTANT:** Never commit the `.env` file to version control!

- The `.env` file contains sensitive credentials
- Add `.env` to your `.gitignore` file
- Use the `env.template` file as a reference
- Rotate your access tokens regularly

## 🚀 Usage

### Starting the Application

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

### Using the Table Configuration Editor

#### 1. Main Page - Browse Configurations

- **View All Tables:** The main page displays all table configurations
- **Filter Results:** Use the dropdowns and text inputs to filter tables
  - Source System dropdown
  - Table Key search
  - Table Name search
- **Navigate Pages:** Use pagination controls to browse through tables
- **View Details:** Click "View →" button to edit a specific table

#### 2. Edit Configuration Page

##### Selecting a Table

1. Choose a Source System from the dropdown
2. Select a table from the filtered list
3. Click "🔄 Load This Table" to edit

##### Editing Schema Fields

1. The data editor displays all schema fields with columns:
   - **Source Name:** Original field name from source
   - **Target Name:** Target field name (required)
   - **Data Type:** Select from supported types
   - **Nullable:** Check if field can be null
   - **Is Primary Key:** Mark as primary key
   - **Is SCD Join Key:** Mark as SCD join key
   - **Is SCD Sequence Key:** Mark as SCD sequence key
   - **Comment:** Field description

2. **Add Fields:** Click the "+" button in the data editor
3. **Remove Fields:** Click the "×" button on any row
4. **Edit Values:** Click any cell to edit directly

##### Saving Changes

1. Review your changes in the data editor
2. Click "💾 Save Schema Changes" to commit
3. Changes are immediately written to Databricks
4. Configuration keys (Primary Keys, SCD Keys) are automatically updated

##### Additional Actions

- **Reset:** Click "↩️ Reset" to discard changes
- **View Raw JSON:** Expand the "🔍 View Raw JSON Schema" section
- **Back to List:** Use the sidebar button to return to main page
- **Refresh Data:** Clear cache and reload from database

### Keyboard Shortcuts

While using Streamlit:
- `Ctrl/Cmd + R` - Rerun the app
- `Ctrl/Cmd + C` - Stop the server
- `C` - Clear cache
- `R` - Rerun

## 📁 Project Structure

```
table_config_app/
├── app.py                  # Main application entry point
├── pages/
│   └── 1_Edit_Config.py   # Edit configuration page
├── utils/
│   ├── __init__.py        # Package initializer
│   ├── config.py          # Configuration constants
│   ├── database.py        # Database operations
│   └── table_config.py    # TableConfig class
├── requirements.txt       # Python dependencies
├── env.template          # Environment template
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

### Module Descriptions

#### `app.py`
Main entry point and homepage of the application. Displays the table list with filtering, pagination, and navigation capabilities.

**Key Functions:**
- `main()`: Application entry point
- Renders table list view
- Handles filtering and pagination
- Manages connection status

#### `pages/1_Edit_Config.py`
Detail page for editing individual table configurations. Provides interactive schema editing with support for adding/removing fields.

**Key Features:**
- Table selection interface
- Schema editor with data_editor component
- Key management (Primary, SCD Join, SCD Sequence)
- Raw JSON viewer

#### `utils/config.py`
Central configuration file containing Databricks table references.

**Constants:**
- `CATALOG`: Databricks catalog name
- `SCHEMA`: Schema name
- `TABLE`: Configuration table name
- `FULL_TABLE_NAME`: Complete table reference

#### `utils/database.py`
Database connectivity and CRUD operations for Databricks SQL.

**Key Functions:**
- `get_connection()`: Establish Databricks connection
- `fetch_table_list()`: Retrieve all table configurations
- `fetch_table_config(TableKey)`: Get specific table config
- `update_DataSchema(TableKey, schema)`: Update schema
- `update_table_config(TableKey, updates)`: Update config fields

#### `utils/table_config.py`
TableConfig class for managing table configurations, schema parsing, and data transformations.

**Key Methods:**
- `__init__(table_key)`: Initialize and load config
- `get_schema_dataframe()`: Convert schema to DataFrame
- `convert_dataframe_to_schema(df)`: Convert DataFrame to schema
- `parse_key_list(key_name)`: Parse comma-separated keys
- Property accessors for keys and schema

## 🏗️ Architecture

### Data Flow

```
┌─────────────────┐
│   Streamlit UI  │
│   (Browser)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   app.py /      │
│   Edit_Config   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TableConfig    │
│  Class          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  database.py    │
│  (SQL Queries)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Databricks    │
│   SQL Warehouse │
└─────────────────┘
```

### Key Design Patterns

1. **Caching:** Uses `@st.cache_resource` for database connections
2. **Session State:** Manages pagination and selected tables
3. **Separation of Concerns:** UI, business logic, and data access are separated
4. **Configuration Management:** Centralized configuration in `utils/config.py`

### Schema Format

The application expects DataSchema to be stored as JSON with the following structure:

```json
{
  "fields": [
    {
      "name": "field_name",
      "type": "string",
      "nullable": true,
      "metadata": {
        "source_name": "source_field",
        "target_name": "target_field",
        "is_primary_key": false,
        "comment": "Field description"
      }
    }
  ]
}
```

## 🔨 Development

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Pytest** for testing

```bash
# Format code
black .

# Run linter
flake8 .

# Run tests (if available)
pytest
```

### Development Setup

1. Install development dependencies (included in requirements.txt)
2. Set `ENVIRONMENT=dev` in your `.env` file
3. Set `LOG_LEVEL=DEBUG` for verbose logging

### Adding New Features

When adding new features:

1. Follow the existing project structure
2. Add new pages in the `pages/` directory
3. Add utility functions in `utils/` modules
4. Update this README with new features
5. Test thoroughly with your Databricks environment

### Common Development Tasks

**Add a new data type:**
Edit the SelectboxColumn options in `pages/1_Edit_Config.py`:

```python
"Data Type": st.column_config.SelectboxColumn(
    "Data Type",
    options=["string", "integer", "your_new_type"],
    required=True,
)
```

**Modify table configuration:**
Edit `utils/config.py`:

```python
CATALOG = "new_catalog"
SCHEMA = "new_schema"
TABLE = "new_table"
```

**Add new schema columns:**
Extend the `schema_to_dataframe()` method in `utils/table_config.py`

## 🐛 Troubleshooting

### Common Issues

#### 1. Connection Failed

**Error:** `❌ Failed to connect to Databricks`

**Solutions:**
- Verify your `.env` file exists and contains correct credentials
- Check that your Databricks SQL Warehouse is running
- Ensure your access token hasn't expired
- Verify network connectivity to Databricks workspace

#### 2. Missing Environment Variables

**Error:** `❌ Missing required environment variables`

**Solutions:**
- Create a `.env` file from `env.template`
- Ensure all required variables are set
- Check for typos in variable names

#### 3. Table Not Found

**Error:** `Failed to load table list`

**Solutions:**
- Verify `CATALOG`, `SCHEMA`, and `TABLE` in `utils/config.py`
- Ensure your access token has read permissions
- Check that the table exists in your Databricks workspace

#### 4. Schema Update Failed

**Error:** `❌ Failed to update schema`

**Solutions:**
- Ensure your access token has write permissions
- Check that all required fields are filled
- Verify Target Name is provided for all fields
- Look at the console output for SQL error details

#### 5. Import Errors

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solutions:**
- Activate your virtual environment
- Run `pip install -r requirements.txt`
- Verify Python version is 3.8+

### Debug Mode

Enable debug mode for more detailed error messages:

```bash
# In .env file
LOG_LEVEL=DEBUG

# Run with Streamlit debug mode
streamlit run app.py --logger.level=debug
```

### Getting Help

If you encounter issues:

1. Check the Streamlit console output for error messages
2. Enable debug logging in your `.env` file
3. Verify your Databricks connection using the SQL connector directly
4. Check the [Streamlit documentation](https://docs.streamlit.io)
5. Review [Databricks SQL Connector docs](https://docs.databricks.com/dev-tools/python-sql-connector.html)

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the bug has already been reported
2. Include detailed steps to reproduce
3. Provide error messages and logs
4. Specify your environment (Python version, OS, etc.)

### Suggesting Features

1. Describe the feature and its use case
2. Explain how it would benefit users
3. Provide examples or mockups if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Code Review Process

- All submissions require review
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [Databricks SQL Connector](https://docs.databricks.com/dev-tools/python-sql-connector.html)
- Powered by [Pandas](https://pandas.pydata.org/)

## 📞 Contact

For questions or support, please:
- Open an issue in the repository
- Contact the development team
- Check the documentation

---

**Version:** 1.0.0  
**Last Updated:** November 2025  
**Status:** Active Development

---

## 🚀 Quick Start Summary

1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Configure** `.env` with Databricks credentials
4. **Run** the app: `streamlit run app.py`
5. **Browse** and edit your table configurations!

Happy configuring! 🎉

