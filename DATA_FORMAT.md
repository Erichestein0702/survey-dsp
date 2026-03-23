# Data Import Format Requirements

This document details the data file import format requirements for each module of the Survey DSP platform.

---

## General Notes

1. **File Encoding**: UTF-8 encoding recommended
2. **Delimiter**: Use space or Tab to separate fields
3. **Comment Lines**: Lines starting with `#` will be ignored
4. **Empty Lines**: Empty lines will be automatically skipped
5. **File Format**: Supports `.txt` and `.csv` text files

---

## Module 1: IDW Interpolation

### File Format

```
Point_ID X_Coordinate Y_Coordinate Elevation_Z
```

### Format Description

| Field | Type | Description |
|-------|------|-------------|
| Point_ID | String | Unique identifier for known or interpolation points |
| X_Coordinate | Float | X direction coordinate value (unit: meters) |
| Y_Coordinate | Float | Y direction coordinate value (unit: meters) |
| Elevation_Z | Float | Elevation value of known points (unit: meters) |

### Data Classification Rules

- **Known Points**: Rows containing 4 fields (Point_ID, X, Y, Z)
- **Interpolation Points**: Rows containing only 3 fields (Point_ID, X, Y)

### Example File

```
# Known sample points (4 fields)
P01 4302.047 3602.652 10.804
P02 4305.768 3598.683 10.855
P03 4310.610 3595.393 10.998
P04 4313.138 3595.086 12.038
P05 4316.843 3594.703 12.818

# Interpolation points (3 fields)
Q1 4310 3600
Q2 4330 3600
Q3 4310 3620
Q4 4330 3620
```

### Notes

- At least 4 known points are required for interpolation
- Point IDs cannot be duplicated
- Coordinate values should use numeric format, avoid scientific notation

---

## Module 2: GPS Elevation Fitting

### File Format

```
Point_ID X_Coordinate Y_Coordinate Height_Anomaly_Zeta
```

### Format Description

| Field | Type | Description |
|-------|------|-------------|
| Point_ID | String | Unique identifier for the point |
| X_Coordinate | Float | X direction coordinate value (unit: meters) |
| Y_Coordinate | Float | Y direction coordinate value (unit: meters) |
| Height_Anomaly_Zeta | Float | Height anomaly value (unit: meters) |

### Data Classification Rules

- **Known Points**: Data points where height anomaly Zeta is **not 0**
- **Unknown Points**: Data points where height anomaly Zeta **equals 0**

### Example File

```
# Known points (Zeta not 0)
1 46.0491 89.6995 -3.9739
2 40.8576 99.6299 -3.5376
3 38.4841 92.1108 -3.7673
4 17.0032 98.8406 -3.3261
5 22.1838 101.9830 -3.2858
6 19.0450 106.2452 -3.0561
7 46.5016 105.1646 -3.3998
8 32.3969 110.7557 -3.0036
9 27.9913 123.9794 -2.4262
10 43.8827 143.2226 -1.9400
11 23.8734 138.8852 -1.7396
12 25.5653 145.7765 -1.5224

# Unknown points (Zeta is 0)
13 36.3441 123.2001 0
14 34.5588 126.6291 0
15 34.9654 131.8336 0
16 30.5073 129.2705 0
17 38.5731 134.9822 0
18 31.7270 137.7843 0
```

### Notes

- At least 12 known points are required for elevation fitting
- Points with height anomaly value of 0 will be treated as unknown points
- Supports three fitting models: plane fitting, quadratic surface fitting, four-parameter surface fitting

---

## Module 3: Time System Conversion

### File Format

```
Year Month Day Hour Minute Second
```

### Format Description

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| Year | Integer | 1-9999 | Gregorian year |
| Month | Integer | 1-12 | Gregorian month |
| Day | Integer | 1-31 | Gregorian day |
| Hour | Integer | 0-23 | Hour |
| Minute | Integer | 0-59 | Minute |
| Second | Float | 0-60 | Second (decimals supported) |

### Example File

```
# Format: Year Month Day Hour Minute Second
2023 5 15 8 30 0
2024 2 28 14 45 30
2025 12 31 23 59 59
2026 3 11 15 30 0
```

### Conversion Results

The program will automatically calculate and output:
- Julian Day (JD)
- GPS Week / Seconds of Week
- Day of Year
- Work status indicator

---

## Module 4: Polygon Area Calculation

### File Format

```
Point_ID X_Coordinate Y_Coordinate
```

### Format Description

| Field | Type | Description |
|-------|------|-------------|
| Point_ID | String | Identifier for polygon vertex |
| X_Coordinate | Float | X direction coordinate value (unit: meters) |
| Y_Coordinate | Float | Y direction coordinate value (unit: meters) |

### Example File

```
# Polygon vertices in order
A 1213.045 1040.663
B 1401.734 1143.376
C 1434.466 1331.594
D 1385.811 1549.016
E 1351.343 1757.744
F 1119.667 1629.719
G 1064.570 1360.432
H 1072.567 1170.905
```

### Notes

- At least 3 vertices are required
- Vertex order affects area calculation (clockwise/counterclockwise)
- Program supports automatic sorting feature (recommended to enable)

---

## Module 5: Coordinate Transformation

### File Format

#### XYZ Coordinate Format

```
Point_ID X_Coordinate Y_Coordinate Z_Coordinate
```

#### BLH Coordinate Format (Excel Import)

| Column Name | Type | Description |
|-------------|------|-------------|
| B | Float | Geodetic latitude (unit: degrees) |
| L | Float | Geodetic longitude (unit: degrees) |
| H | Float | Geodetic height (unit: meters) |

### Format Description

| Field | Type | Description |
|-------|------|-------------|
| Point_ID | String | Identifier for coordinate point |
| X_Coordinate | Float | Spatial rectangular coordinate X (unit: meters) |
| Y_Coordinate | Float | Spatial rectangular coordinate Y (unit: meters) |
| Z_Coordinate | Float | Spatial rectangular coordinate Z (unit: meters) |

### Example File

```
# XYZ spatial rectangular coordinates
A -2422455.7116 5377816.7730 2434562.7366
B -2512351.4719 5369568.5389 2432435.1126
C -2478312.5649 5380268.2462 2425129.0941
D -2392240.9396 5397563.0493 2404757.8901
E -2476565.0023 5391602.9203 2392378.8893
F -2523062.3827 5389237.8430 2417327.0448
```

### NEU Conversion Notes

For XYZ to NEU conversion, additional reference station coordinates are required:
- Rover station coordinates: X, Y, Z
- Reference station coordinates: Ref_X, Ref_Y, Ref_Z

---

## Module 6: Landslide Monitoring

### File Format

```
Point_ID Num_Epochs
Epoch1 X1 Y1
Epoch2 X2 Y2
...
```

### Format Description

**Point ID Line**:
| Field | Type | Description |
|-------|------|-------------|
| Point_ID | String | Unique identifier for monitoring point |
| Num_Epochs | Integer | Number of observation epochs for this monitoring point |

**Coordinate Line**:
| Field | Type | Description |
|-------|------|-------------|
| Epoch | Integer | Observation epoch number (e.g., 1, 2, 3...) |
| X_Coordinate | Float | X direction coordinate value (unit: meters) |
| Y_Coordinate | Float | Y direction coordinate value (unit: meters) |

### Example File

```
# Monitoring point M01, 4 epochs of observation
M01 4
1 492.1373 973.2576
2 492.1377 973.2694
3 492.1421 973.2718
4 492.1436 973.2753

# Monitoring point M02, 4 epochs of observation
M02 4
1 427.5401 481.6885
2 427.5326 481.6854
3 427.5288 481.6845
4 427.5298 481.6887

# Monitoring point M03, 4 epochs of observation
M03 4
1 95.3324 156.7524
2 95.3287 156.7561
3 95.3217 156.7551
4 95.3296 156.7539
```

### Notes

- Each monitoring point requires at least 2 epochs of data to calculate deformation velocity
- Epoch numbers should be consecutive and start from 1
- Coordinate values should use the same coordinate system

---

## Excel File Import Notes

Some modules support Excel file import (.xlsx, .xls format):

### Module 2: GPS Elevation Fitting

Excel file must contain the following columns:
| Column Name | Required |
|-------------|----------|
| X | Yes |
| Y | Yes |
| Zeta | Yes |

### Module 4: Polygon Area

Excel file must contain the following columns:
| Column Name | Required |
|-------------|----------|
| X | Yes |
| Y | Yes |

### Module 5: Coordinate Transformation

Excel file must contain the following columns:
| Column Name | Required |
|-------------|----------|
| X | Yes |
| Y | Yes |
| Z | Yes |

### Module 6: Landslide Monitoring

Excel file must contain the following columns:
| Column Name | Required |
|-------------|----------|
| ID | Yes |
| Epoch | Yes |
| X | Yes |
| Y | Yes |
| Z | Yes |

---

## FAQ

### 1. File Encoding Issues

**Problem**: Garbled characters after import  
**Solution**: Ensure file is saved with UTF-8 encoding

### 2. Delimiter Issues

**Problem**: Data parsing failed  
**Solution**: Ensure space or Tab is used as delimiter, avoid commas

### 3. Numeric Format Issues

**Problem**: Numeric parsing error  
**Solution**:
- Use decimal point (.) not comma (,)
- Avoid adding spaces before or after numeric values
- Avoid using thousand separators

### 4. Duplicate Point ID Issues

**Problem**: Abnormal calculation results  
**Solution**: Ensure each point ID is unique and not duplicated

---

**Last Updated**: 2026-03-12  
**Version**: v1.0
