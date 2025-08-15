# PJI Law Reports - Modular Version

This is a modular refactoring of the original monolithic `app.py` file. The application has been broken down into logical modules for better maintainability, readability, and extensibility.

## Project Structure

```
Conversion_Call-Reports/
├── app.py                          # Original monolithic application
├── app_modular.py                  # New modular application entry point
├── modules/                        # Modular components
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Configuration and constants
│   ├── auth.py                    # Authentication handling
│   ├── data_manager.py            # Google Sheets and data operations
│   ├── batch_manager.py           # Batch management and metadata
│   ├── ui_manager.py              # User interface components
│   ├── visualizations.py          # Chart generation and plotting
│   └── utils.py                   # Common utility functions
└── README_MODULAR.md              # This documentation
```

## Module Descriptions

### `app_modular.py`
The main entry point for the modular application. It orchestrates the initialization and execution of all modules.

### `modules/config.py`
Contains all configuration constants and settings:
- Google Sheets tab names and fallbacks
- Calls processing configuration (allowed names, categories)
- Practice area definitions
- Attorney mappings and display overrides
- Intake specialist configurations
- Month mappings

### `modules/auth.py`
Handles user authentication:
- Google Sheets service account setup
- Streamlit authenticator configuration
- Login/logout functionality
- Authentication status checking

### `modules/data_manager.py`
Manages all data operations:
- Google Sheets connectivity
- Worksheet reading and writing
- Data caching and versioning
- Batch operations
- Data synchronization

### `modules/batch_manager.py`
Handles batch operations and metadata:
- Batch ID generation
- Metadata addition to dataframes
- Empty sheet creation with headers
- Master reset functionality
- Orphaned record management

### `modules/ui_manager.py`
Manages all user interface components:
- Admin sidebar rendering
- File upload sections
- Report rendering (calls, conversion, practice area, intake)
- Data filtering and display
- Debug section

### `modules/visualizations.py`
Handles chart generation and plotting:
- Plotly availability checking
- Calls report visualizations
- Conversion trend charts
- Chart configuration and styling

### `modules/utils.py`
Contains common utility functions:
- Date parsing and formatting
- File operations
- String normalization
- Data validation helpers
- HTML escaping

## Benefits of Modular Structure

### 1. **Maintainability**
- Each module has a single responsibility
- Easier to locate and fix issues
- Clear separation of concerns

### 2. **Readability**
- Smaller, focused files
- Clear module boundaries
- Better code organization

### 3. **Extensibility**
- Easy to add new features
- Modular design allows for independent development
- Clear interfaces between components

### 4. **Testing**
- Individual modules can be tested in isolation
- Easier to write unit tests
- Better test coverage

### 5. **Reusability**
- Utility functions can be reused across modules
- Configuration can be shared
- Common patterns are centralized

## Usage

### Running the Modular Application

```bash
streamlit run app_modular.py
```

### Development

To work on a specific module:

1. **Configuration Changes**: Edit `modules/config.py`
2. **Authentication**: Modify `modules/auth.py`
3. **Data Operations**: Work in `modules/data_manager.py`
4. **UI Components**: Update `modules/ui_manager.py`
5. **Visualizations**: Enhance `modules/visualizations.py`
6. **Utilities**: Add helpers to `modules/utils.py`

### Adding New Features

1. **New Report Type**: Add methods to `ui_manager.py`
2. **New Data Source**: Extend `data_manager.py`
3. **New Visualization**: Create functions in `visualizations.py`
4. **New Configuration**: Add constants to `config.py`

## Migration from Original App

The modular version maintains the same functionality as the original `app.py` but with better organization. Key differences:

1. **Imports**: The main app now imports from modules
2. **Initialization**: Each module handles its own initialization
3. **Error Handling**: More consistent error handling across modules
4. **Documentation**: Better docstrings and type hints

## Future Improvements

### Phase 1 (Current)
- ✅ Basic modular structure
- ✅ Configuration separation
- ✅ Authentication isolation
- ✅ Data management abstraction

### Phase 2 (Planned)
- [ ] Complete implementation of all report functionality
- [ ] Enhanced error handling
- [ ] Comprehensive logging
- [ ] Unit tests

### Phase 3 (Future)
- [ ] API endpoints for data access
- [ ] Database integration options
- [ ] Advanced caching strategies
- [ ] Performance optimizations

## Dependencies

The modular version uses the same dependencies as the original application:

```
streamlit
pandas
gspread
gspread-dataframe
google-auth
streamlit-authenticator
plotly
openpyxl
xlrd
pyyaml
```

## Configuration

The modular version uses the same Streamlit secrets configuration as the original:

```toml
# .streamlit/secrets.toml
[gcp_service_account]
# Google service account credentials

[master_store]
sheet_url = "your-google-sheet-url"

[auth_config]
config = "your-auth-config"
```

## Contributing

When contributing to the modular version:

1. **Follow the module structure**: Add new functionality to appropriate modules
2. **Use type hints**: All functions should have proper type annotations
3. **Add docstrings**: Document all public functions and classes
4. **Update configuration**: Add new constants to `config.py`
5. **Test thoroughly**: Ensure changes work across all modules

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all modules are in the `modules/` directory
2. **Configuration Issues**: Check that all constants are properly defined in `config.py`
3. **Authentication Problems**: Verify secrets configuration in Streamlit
4. **Data Loading Issues**: Check Google Sheets permissions and connectivity

### Debug Mode

The modular version includes debug sections that can be enabled for troubleshooting:

```python
# In ui_manager.py, debug sections are rendered when authentication is successful
if auth_status:
    ui_manager.render_debug_section(data_manager)
```

This modular structure provides a solid foundation for future development while maintaining all the functionality of the original application.
