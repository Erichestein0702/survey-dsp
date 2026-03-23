# Survey DSP - Data Processing Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. What is this?

This is a **Data Processing Platform** designed specifically for surveying engineering.

**DSP** = Data Surveying Processing

It transforms complex surveying calculations into a simple "Import-Calculate-Export" three-step workflow. No programming skills required - just click your way through professional calculations.

### 6 Core Modules

| Module | Problem Solved | Typical Use Cases |
|--------|----------------|-------------------|
| **IDW Interpolation** | Estimate unknown points from known points | Calculate elevation of points to be surveyed from control points, supports n=4,5,6 comparative analysis |
| **GPS Elevation Fitting** | Build height anomaly models | Fit regional elevation variation patterns using known points, compare three methods to select the optimal one |
| **Time System Conversion** | Unify time formats | Convert between GPS time, Gregorian calendar, Julian day, and day of year; supports batch file processing |
| **Polygon Area** | Calculate enclosed area | Calculate triangle areas using Heron's formula and summarize |
| **Coordinate Transformation** | Convert between coordinate systems | Convert between XYZ spatial coordinates and latitude/longitude, supports multiple ellipsoid parameters |
| **Landslide Monitoring** | Deformation trend analysis | Two-dimensional deformation analysis with multi-period monitoring data, calculate deformation velocity and strain |

---

## 2. Why build this?

### Pain Points of Traditional Methods

Surveying work often requires processing large amounts of data:
- Known point data needs to estimate unknown points
- Different coordinate systems need to be converted
- Monitoring data needs deformation trend analysis
- Time formats need unified conversion

Traditional approaches involve **manual calculation** or using **scattered tools**, which have the following issues:
- Calculation process is tedious and error-prone
- Different functions require switching between different software
- Data formats are inconsistent, conversion is troublesome
- Results are difficult to save and share

### Advantages of This Platform

| Comparison | Traditional Method | This Platform |
|------------|-------------------|---------------|
| Operation Mode | Manual calculation / Multiple software switching | One-stop operation |
| Error Risk | High (manual calculation) | Low (automatic calculation) |
| Data Format | Inconsistent across software | Unified format standards |
| Result Saving | Manual organization required | One-click export report |
| Learning Curve | Need to master multiple tools | Intuitive interface, easy to get started |

---

## 3. How to use?

### Step 1: Install Environment

1. Make sure **Python 3.8 or higher** is installed
2. Open command line, navigate to project directory
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Step 2: Launch Program

Run in the project directory:
```
python run_ui.py
```

After launch, the main interface will display with a navigation sidebar on the left and operation area on the right.

### Step 3: Import Data

Interface operation logic:

| Button | Function |
|--------|----------|
| **Browse** | Select file, automatically fill in path |
| **Load** | Load data based on the path in the path field |
| **Manual Input** | Input data directly without file dependency |

> **Tip**: Import and Load are separate operations. First use "Browse" to select a file, then use "Load" to display data. This makes it easy to modify paths or reload data.

### Step 4: Calculate and Export

1. Click **Start Calculation**
2. View calculation results and graphics
3. Use export buttons to save results:

| Export Format | Purpose |
|---------------|---------|
| **Markdown** | Generate calculation report, suitable for archiving and sharing |
| **CSV** | Export raw data, suitable for Excel processing |
| **Image** | Save visualization results, suitable for report illustrations |

---

## Data Format Requirements

For detailed format specifications, please refer to [Data Import Format Requirements](./导入文件格式要求.md)

**Basic Principles**:
- Text files: One record per line, fields separated by spaces
- Excel files: First row contains column headers, headers must meet requirements
- Comment lines supported: Lines starting with `#` will be ignored

---

## FAQ

### Q: Program crashes immediately after launch?
A: Please check if all dependencies are correctly installed. Run `pip install -r requirements.txt` to reinstall.

### Q: Blank display after importing data?
A: Please check if the data format meets requirements. Refer to the "Data Import Format Requirements" document.

### Q: Abnormal calculation results?
A: Please verify input data is correct, especially coordinate units (degrees/radians) and elevation units (meters).

### Q: How to view detailed calculation process information?
A: Log files are located in the `logs/` directory, recording all operations and error information for troubleshooting.

---

## Directory Structure

```
SurveyDSP/
├── common/                 # Common components
├── logs/                   # Log directory (records operations and errors)
├── module1_IDW/            # IDW interpolation module
├── module2_GPS_Elevation/  # GPS elevation fitting module
├── module3_TimeSystem/     # Time system conversion module
├── module4_Area/           # Polygon area module
├── module5_Cord/           # Coordinate transformation module
├── module6_Slide/          # Landslide monitoring module
├── reports/                # Report output directory
├── test_data/              # Test data (ready to use)
├── ui/                     # UI components
├── run_ui.py               # Program entry point
├── ellipsoid_config.json   # Ellipsoid parameter configuration
└── 导入文件格式要求.md      # Data format specification
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

Special thanks to Professor Pu, the instructor of the Surveying Comprehensive Practice, for guidance and support!

---

**Version**: v1.4.0  
**Maintainer**: erichestein  
**Last Updated**: 2026-03-13
