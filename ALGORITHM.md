# DSP Algorithm Documentation

This document details the mathematical principles, algorithm workflows, and implementation details of each module in the Survey DSP project.

**DSP** = Data Surveying Processing

## Table of Contents

1. [Module 1: Inverse Distance Weighting (IDW) Interpolation](#module-1-inverse-distance-weighting-idw-interpolation)
2. [Module 2: GPS Elevation Fitting](#module-2-gps-elevation-fitting)
3. [Module 3: Time System Conversion](#module-3-time-system-conversion)
4. [Module 4: Polygon Area Calculation](#module-4-polygon-area-calculation)
5. [Module 5: Coordinate Transformation](#module-5-coordinate-transformation)
6. [Module 6: Landslide Deformation Velocity and Strain Calculation](#module-6-landslide-deformation-velocity-and-strain-calculation)
7. [Common Components](#common-components)

---

## Module 1: Inverse Distance Weighting (IDW) Interpolation

### 1. Objective

Interpolate the elevation of unknown points from known sample points.

### 2. Mathematical Principles

#### 2.1 Distance Calculation

Calculate the planar distance from unknown point Q(x,y) to each known sample point Pᵢ(xᵢ,yᵢ):

$$d_i = \sqrt{(x - x_i)^2 + (y - y_i)^2}$$

#### 2.2 Weight Calculation

$$W_i = \frac{1}{d_i^p}$$

Where p is the power exponent, typically p = 2.

#### 2.3 Weighted Average

$$H_Q = \frac{\sum_{i=1}^{n} W_i \cdot H_i}{\sum_{i=1}^{n} W_i}$$

Where:
- $H_Q$: Elevation of the interpolation point
- $H_i$: Elevation of known sample points
- $W_i$: Weight values

### 3. Algorithm Workflow

```
1. Read known sample point data (point ID, X, Y, elevation)
2. Read interpolation point data (point ID, X, Y)
3. For each interpolation point:
   3.1 Calculate distances dᵢ to all known points
   3.2 Calculate weights Wᵢ = 1/dᵢᵖ
   3.3 Calculate elevation by weighted average H_Q = Σ(Wᵢ×Hᵢ)/ΣWᵢ
4. Output interpolation results
```

### 4. Implementation Notes

- **Zero Distance Handling**: When the interpolation point coincides with a known point, directly return that known point's elevation
- **Power Exponent Selection**: Default p=2, adjustable based on data characteristics
- **Search Radius**: Maximum search radius can be set to reduce computation

### 5. Data Format

**Input Format**:
```
# Known sample points
# Format: Point_ID X Y Elevation
P01 100.0 200.0 50.5
P02 150.0 250.0 52.3
P03 200.0 300.0 55.1

# Interpolation points
# Format: Point_ID X Y
Q01 120.0 220.0
Q02 180.0 280.0
```

---

## Module 2: GPS Elevation Fitting

### 1. Objective

Use known point height anomaly values to fit a model and estimate height anomalies for unknown points.

### 2. Mathematical Principles

#### 2.1 Height Anomaly Definition

$$\zeta = h - H$$

Where:
- $h$: Geodetic height from GPS measurement
- $H$: Normal height from leveling

#### 2.2 Fitting Models

**Plane Fitting Model**:

$$\zeta = a_0 + a_1 X + a_2 Y$$

Applicable scenarios: Small flat areas (< 10km²)

**Quadratic Surface Fitting Model**:

$$\zeta = a_0 + a_1 X + a_2 Y + a_3 X^2 + a_4 XY + a_5 Y^2$$

Applicable scenarios: Medium-sized areas (10-100km²) with some terrain variation

#### 2.3 Least Squares Solution

Error equation:

$$V = AX - L$$

Normal equation:

$$A^T A X = A^T L$$

Solution:

$$X = (A^T A)^{-1} A^T L$$

### 3. Accuracy Assessment

**Standard Error**:

$$\sigma = \sqrt{\frac{\sum v^2}{n - k}}$$

Where n is the number of known points, k is the number of parameters.

### 4. Algorithm Workflow

```
1. Read known point data (X, Y, ζ)
2. Build design matrix A and observation vector L
3. Solve normal equation (A^T A)X = A^T L
4. Calculate residuals V = AX - L
5. Evaluate model accuracy σ = √[Σv²/(n-k)]
6. Select optimal model (minimum σ)
```

---

## Module 3: Time System Conversion

### 1. Objective

Convert between Gregorian calendar (year, month, day), Julian Day (JD), and GPS time.

### 2. Mathematical Principles

#### 2.1 Gregorian to Julian Day (JD)

If month M ≤ 2:
- Y = Y - 1
- M = M + 12

Calculate Julian Day:

$$JD = \lfloor 365.25Y \rfloor + \lfloor 30.6001(M+1) \rfloor + D + 1720981.5 + \frac{UT}{24}$$

Where:
- Y: Year
- M: Month
- D: Day
- UT: Universal Time (hours)

#### 2.2 Julian Day to GPS Week/Seconds of Week

GPS time origin: JD₀ = 2444244.5 (1980-01-06 00:00:00 UT)

$$Week = \lfloor \frac{JD - JD_0}{7} \rfloor$$

$$Seconds = (JD - JD_0 - Week \times 7) \times 86400$$

#### 2.3 GPS Week/Seconds to Julian Day

$$JD = JD_0 + Week \times 7 + \frac{Seconds}{86400}$$

#### 2.4 Julian Day to Gregorian

Convert Julian Day to year, month, day, hour, minute, second through inverse calculation.

### 3. Algorithm Workflow

```
Gregorian → Julian Day:
1. Handle month (if M≤2, Y=Y-1, M=M+12)
2. Calculate JD = ⌊365.25Y⌋ + ⌊30.6001(M+1)⌋ + D + 1720981.5 + UT/24

Julian Day → GPS Time:
1. Calculate GPS origin JD₀ = 2444244.5
2. Week = ⌊(JD - JD₀)/7⌋
3. Seconds = (JD - JD₀ - Week×7) × 86400

GPS Time → Julian Day:
1. JD = JD₀ + Week×7 + Seconds/86400

Julian Day → Gregorian:
1. Calculate year, month, day, hour, minute, second through inverse algorithm
```

### 4. Data Format

```
# Gregorian time
# Format: Year Month Day Hour Minute Second
2026 3 11 14 30 0.0

# Julian Day
2460745.104167

# GPS week and seconds of week
# Format: Week Seconds
2300 345678.5
```

---

## Module 4: Polygon Area Calculation

### 1. Objective

Calculate the area of a polygon formed by multiple coordinate points.

### 2. Mathematical Principles

#### 2.1 Shoelace Formula

$$Area = \frac{1}{2} \left| \sum_{i=1}^{n} (x_i y_{i+1} - x_{i+1} y_i) \right|$$

Where $x_{n+1} = x_1, y_{n+1} = y_1$.

#### 2.2 Triangulation Method (Auxiliary Verification)

Using the polygon centroid as origin, decompose polygon into n triangles:

$$S = \sum_{i=1}^{n} S_{\triangle O P_i P_{i+1}}$$

Single triangle area (Heron's formula):

$$S_{\triangle} = \sqrt{p(p-a)(p-b)(p-c)}$$

Where $p = (a+b+c)/2$.

### 3. Algorithm Workflow

```
1. Read polygon vertex coordinates
2. Check point order (ensure clockwise or counterclockwise)
3. Calculate area using shoelace formula
4. Verify with triangulation method (optional)
5. Output area result
```

### 4. Precision Control

- Area calculation precision: 10⁻⁶ m²
- Double verification difference threshold: 10⁻⁶ m²

---

## Module 5: Coordinate Transformation

### 1. Objective

Convert between spatial rectangular coordinates (XYZ), geodetic coordinates (BLH), and topocentric coordinates (NEU).

### 2. Mathematical Principles

#### 2.1 Ellipsoid Parameters (WGS-84)

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Semi-major axis | a | 6378137.0 m |
| Flattening | f | 1/298.257223563 |
| First eccentricity squared | e² | 2f - f² |

#### 2.2 XYZ → BLH

**Longitude**:

$$L = \arctan2(Y, X)$$

**Latitude Iteration**:

$$p = \sqrt{X^2 + Y^2}$$

$$\theta = \arctan\left(\frac{Z \cdot a}{p \cdot b}\right)$$

$$B = \arctan\left(\frac{Z + e'^2 b \sin^3\theta}{p - e^2 a \cos^3\theta}\right)$$

Iterate until $|B_{new} - B_{old}| < 10^{-10}$

**Geodetic Height**:

$$N = \frac{a}{\sqrt{1 - e^2 \sin^2 B}}$$

$$H = \frac{p}{\cos B} - N$$

#### 2.3 BLH → XYZ

$$X = (N + H) \cos B \cos L$$

$$Y = (N + H) \cos B \sin L$$

$$Z = [N(1 - e^2) + H] \sin B$$

#### 2.4 XYZ → NEU

$$\begin{bmatrix} N \\ E \\ U \end{bmatrix} = R \begin{bmatrix} X - X_0 \\ Y - Y_0 \\ Z - Z_0 \end{bmatrix}$$

Where R is the rotation matrix based on reference point (B, L).

### 3. Precision Control

- Latitude iteration convergence threshold: 10⁻¹⁰ rad
- Coordinate transformation precision: 10⁻⁶ m

---

## Module 6: Landslide Deformation Velocity and Strain Calculation

### 1. Objective

Analyze the rate of displacement over time at monitoring points and deformation between point pairs.

### 2. Mathematical Principles

#### 2.1 Deformation Velocity

$$V = \frac{\sqrt{\Delta X^2 + \Delta Y^2 + \Delta Z^2}}{\Delta t}$$

Where Δt is the actual observation interval in days.

#### 2.2 Relative Strain

$$\varepsilon = \frac{S_{t+1} - S_t}{S_t}$$

Where S is the spatial Euclidean distance between two monitoring points:

$$S = \sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2 + (Z_2 - Z_1)^2}$$

### 3. Algorithm Workflow

```
1. Read multi-period monitoring data
2. Group by monitoring point
3. For each monitoring point:
   3.1 Calculate displacement for each period
   3.2 Calculate deformation velocity
4. For each monitoring point pair:
   4.1 Calculate distance S for each period
   4.2 Calculate relative strain ε
5. Generate analysis report
```

### 4. Data Format

```
# Monitoring point time series data
# Format: Point_ID Period X Y Z
M01 1 3548000.123 526000.456 1200.000
M01 2 3548000.125 526000.458 1199.995
M02 1 3548200.234 526100.567 1210.000
M02 2 3548200.236 526100.569 1209.998
```

---

## Common Components

### 1. Matrix Operation Engine

- Normal equation solving
- Condition number calculation
- Ill-conditioned matrix detection
- SVD decomposition

### 2. Data Parser

- Supported formats: TXT, CSV
- Automatic encoding detection (UTF-8/GBK)
- Comment line filtering (lines starting with #)

### 3. Logging System

- Log levels: DEBUG/INFO/WARNING/ERROR
- Output methods: Console + File

---

## Appendix

### A. Constant Definitions

```python
# WGS-84 ellipsoid parameters
WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563
WGS84_E2 = 2 * WGS84_F - WGS84_F ** 2

# GPS time origin
GPS_JD0 = 2444244.5  # 1980-01-06

# Numerical precision
ITERATION_THRESHOLD = 1e-10
```

### B. References

1. Kong Xiangyuan, Guo Jiming. Fundamentals of Geodesy[M]. Wuhan University Press, 2010.
2. Hofmann-Wellenhof B, et al. GNSS – Global Navigation Satellite Systems[M]. Springer, 2008.

---

**Document Version**: v1.0.0  
**Last Updated**: 2026-03-11  
**Maintainer**: erichestein
