# Smart Parking Lot Management System

A comprehensive parking management system built with Python and Tkinter, featuring advanced validations, VIP parking, blacklist management, and detailed reporting capabilities.

## Features

### Core Functionality
- **Multi-Vehicle Support**: Cars, Bikes, Trucks, and Custom vehicles
- **Real-time Parking Management**: Park and remove vehicles with instant updates
- **Slot Management**: Multi-level parking with configurable slots per level
- **Fee Calculation**: Dynamic pricing based on vehicle type and duration

### Enhanced Features
- **Input Validation**: Comprehensive validation for vehicle numbers and types
- **VIP Parking**: Reserved slots and priority queuing for VIP customers
- **Blacklist Management**: Block problematic vehicles from parking
- **Waiting Queue**: Separate queues for VIP and regular customers
- **Real-time Statistics**: Live occupancy rates and parking analytics
- **Receipt Generation**: Professional parking receipts with all details

### Reporting & Analytics
- **Daily Reports**: Revenue and vehicle breakdown by day
- **Monthly Reports**: Comprehensive monthly analysis with peak days
- **Peak Hour Analysis**: Identify busy periods for better management
- **Long-term Parking Alerts**: Track vehicles parked beyond threshold
- **Data Export**: Export data to CSV and JSON formats

### Administrative Features
- **Data Backup**: Automated backup system for all parking data
- **Data Integrity Checks**: Validate data consistency and report issues
- **Configuration Management**: Customizable settings via config file
- **Log Management**: Automatic cleanup of old logs

## Installation

1. **Clone or download the project files**
2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python gui.py
   ```

## File Structure

```
Parking Management System/
├── gui.py              # Main GUI application with all enhanced features
├── Oel.py              # Core parking system classes
├── utils.py            # Utility functions and maintenance tools
├── config.json         # Configuration settings
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules for version control
├── icon.ico           # Application icon
├── parking_log.json   # Parking history logs (excluded from git)
├── parking_receipts.json # Active parking receipts (excluded from git)
├── blacklist.json     # Blacklisted vehicles (excluded from git)
├── test_system.py     # Comprehensive test suite
└── README.md          # This documentation
```

## Configuration

The system can be customized through `config.json`:

### Parking Lot Settings
- `total_levels`: Number of parking levels
- `slots_per_level`: Slots per level
- `vip_slots`: Pre-reserved VIP slots

### Pricing Configuration
- Base fees and hourly rates for each vehicle type
- Customizable pricing for different vehicle categories

### Validation Rules
- Vehicle number length limits
- Custom type validation parameters

### Feature Toggles
- Enable/disable VIP parking
- Enable/disable blacklist functionality
- Configure automatic updates and alerts

## Usage Guide

### Basic Operations

1. **Park a Vehicle**:
   - Select vehicle type from dropdown
   - Enter vehicle number (validated in real-time)
   - Optionally specify preferred slot
   - Check VIP parking if applicable
   - Click "Park Vehicle"

2. **Remove a Vehicle**:
   - Enter vehicle number
   - Click "Remove Vehicle"
   - Receipt will be generated automatically

3. **Check Vehicle Status**:
   - Enter vehicle number
   - Click "Check Status"
   - View detailed parking information

### Advanced Features

1. **VIP Parking**:
   - Check "VIP Parking" checkbox when parking
   - VIP vehicles get priority in queues
   - Can use reserved slots

2. **Blacklist Management**:
   - Access through "Manage Blacklist" button
   - Add, remove, or view blacklisted vehicles
   - Blacklisted vehicles cannot park

3. **Queue Management**:
   - System automatically queues vehicles when full
   - Separate VIP and regular queues
   - Automatic processing when slots become available

## Validation Rules

### Vehicle Numbers
- 3-15 characters in length
- Only letters, numbers, and hyphens allowed
- Automatically converted to uppercase
- Real-time validation during input

### Custom Vehicle Types
- 2-20 characters in length
- Only letters and spaces allowed
- Automatically formatted to title case

### Slot IDs
- Format: L{level}-S{slot} (e.g., L1-S5)
- Must exist in the parking lot
- Cannot be occupied when reserving

## Data Management

### Backup System
```bash
python utils.py backup
```
Creates timestamped backups of all data files.

### Data Export
```bash
python utils.py export
```
Exports parking logs to CSV format.

### Data Cleanup
```bash
python utils.py clean 30
```
Removes logs older than 30 days.

### Reports
```bash
python utils.py report 2024 12
```
Generates monthly report for December 2024.

### Data Validation
```bash
python utils.py validate
```
Checks data integrity and reports issues.

## Error Handling

The system includes comprehensive error handling:
- **Validation Errors**: Clear messages for invalid inputs
- **System Errors**: Graceful handling of file operations
- **Data Errors**: Recovery from corrupted data files
- **UI Errors**: User-friendly error messages

## Security Features

- **Input Sanitization**: All inputs are validated and sanitized
- **Data Validation**: Comprehensive checks prevent data corruption
- **Error Logging**: System errors are logged for debugging
- **Backup Protection**: Automatic backups prevent data loss

## Performance Features

- **Real-time Updates**: Statistics update every 10 seconds
- **Efficient Querying**: Optimized data structures for fast lookups
- **Memory Management**: Automatic cleanup of old data
- **Responsive UI**: Non-blocking operations for better user experience

## Troubleshooting

### Common Issues

1. **Application won't start**:
   - Check if all dependencies are installed
   - Verify Python version compatibility
   - Check if icon.ico file exists

2. **Data not saving**:
   - Check file permissions in the directory
   - Ensure sufficient disk space
   - Verify JSON file formats

3. **Vehicle already parked error**:
   - Check if vehicle is actually parked
   - Use "Check Status" to verify
   - Remove vehicle first if needed

### Log Files

- Check `parking_log.json` for historical data
- Check `parking_receipts.json` for active parkings
- Use `utils.py validate` to check data integrity

## Development

### Version Control Setup

1. **Initialize Git Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Enhanced Parking Management System"
   ```

2. **Files Excluded from Git**:
   - Data files (`parking_log.json`, `parking_receipts.json`, `blacklist.json`)
   - Backup files and exports
   - Python cache files (`__pycache__/`, `*.pyc`)
   - IDE files (`.vscode/`, `.idea/`)
   - Virtual environments
   - Log and temporary files

3. **Recommended Git Workflow**:
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature
   
   # Make changes and commit
   git add .
   git commit -m "Add new feature"
   
   # Merge back to main
   git checkout main
   git merge feature/new-feature
   ```

### Adding New Features

1. **New Vehicle Types**:
   - Extend the Vehicle base class in `Oel.py`
   - Add to GUI dropdown options
   - Update validation logic

2. **New Pricing Models**:
   - Modify `calculate_fee` methods
   - Update configuration options
   - Add to admin interface

3. **New Reports**:
   - Add methods to `ParkingManager` class
   - Create GUI buttons and handlers
   - Add to utils.py for command-line access

### Code Structure

- **Oel.py**: Core business logic and data models
- **gui.py**: User interface and interaction handling (enhanced version with all features)
- **utils.py**: Maintenance tools and utilities
- **config.json**: Configuration and settings

## License

This project is developed for educational purposes. Feel free to modify and distribute as needed.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Validate your data using the built-in tools
3. Review the configuration settings
4. Check log files for error details

## Version History

- **v2.0** (Current): Enhanced version with validations, VIP parking, blacklist, and advanced features
- **v1.0**: Basic parking management with core functionality

---

**Developed by Ghulam Murtaza**  
Enhanced Parking Management System with comprehensive features and validations.
