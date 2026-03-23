# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-03-14

### Added

- IDW Interpolation Module: Support for n=4,5,6 neighboring points comparative analysis
- GPS Elevation Fitting Module: Plane fitting, four-parameter fitting, and quadratic surface fitting methods
- Time System Conversion Module: Conversion between Gregorian calendar, Julian day, and GPS time
- Polygon Area Calculation Module: Shoelace formula + triangulation double verification
- Coordinate Transformation Module: XYZ/BLH/NEU coordinate conversion, supporting 7 ellipsoid parameters
- Landslide Monitoring Module: Displacement velocity, strain calculation, anomaly warning
- PyQt6 Graphical User Interface
- Unified data import/export functionality
- Complete logging system
- Matrix calculation engine (supports ill-conditioned matrix processing)
- Ellipsoid parameter configuration file

### Features

- Automatic file encoding detection (UTF-8, GBK, GB2312, etc.)
- Automatic delimiter recognition (space, Tab, comma)
- Markdown report export
- CSV data export
- PNG/PDF image export
- Debug manager

### Documentation

- README.md project documentation
- DATA_FORMAT.md data format specification
- ALGORITHM.md system design documentation

---

## Future Releases

Stay tuned for updates in future versions!
