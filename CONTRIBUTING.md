# Contributing to Survey DSP

Thank you for considering contributing to the Survey DSP Data Processing Platform!

## How to Contribute

### Reporting Bugs

If you find a bug, please submit a report via [GitHub Issues](../../issues). Before submitting:

1. Search existing issues to confirm the problem hasn't been reported
2. Use the Bug Report template and include:
   - Operating system and Python version
   - Steps to reproduce
   - Expected behavior and actual behavior
   - Relevant logs or screenshots

### Proposing New Features

New feature suggestions are welcome! Please submit via [GitHub Issues](../../issues) and include:

1. Feature description
2. Use cases
3. Possible implementation ideas

### Submitting Code

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your code changes
4. Ensure code style consistency
5. Commit changes: `git commit -m 'Add some feature'`
6. Push branch: `git push origin feature/your-feature-name`
7. Submit a Pull Request

## Code Standards

### Python Code Style

- Follow PEP 8 coding conventions
- Use 4 spaces for indentation
- Add docstrings to functions and classes
- Use snake_case for variables, PascalCase for classes

### Commit Message Standards

- Use clear and concise commit messages
- Recommended format: `<type>: <description>`
- Types include: `feat` (new feature), `fix` (bug fix), `docs` (documentation), `refactor` (refactoring), `test` (testing)

## Development Environment Setup

```bash
# Clone repository
git clone https://github.com/your-username/survey-dsp.git
cd survey-dsp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_all_modules.py

# Launch application
python run_ui.py
```

## Project Structure

```
survey-dsp/
├── common/           # Common components (logger, parser, matrix engine, etc.)
├── module1_IDW/      # IDW interpolation module
├── module2_GPS_Elevation/  # GPS elevation fitting module
├── module3_TimeSystem/     # Time system conversion module
├── module4_Area/     # Area calculation module
├── module5_Cord/     # Coordinate transformation module
├── module6_Slide/    # Landslide monitoring module
├── ui/               # User interface
├── test_data/        # Test data
└── logs/             # Log directory
```

## Contact

If you have questions, please contact the maintainer: erichestein

---

Thank you again for your contribution!
