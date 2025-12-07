# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mzidentml-reader is a Python 3.10 application that processes mzIdentML 1.2.0 and 1.3.0 files, primarily for extracting crosslink information from mass spectrometry data. It serves three main purposes:
1. Validate mzIdentML files against crosslinking criteria
2. Extract crosslinked residue pairs for modeling software
3. Populate databases for the crosslinking-api

## Architecture

- **Entry Point**: `parser.py` or `python -m parser` (both delegate to `parser/process_dataset.py`)
- **Core Parser**: `parser/MzIdParser.py` - Main mzIdentML parsing logic using pyteomics
- **Data Models**: `models/` - SQLAlchemy ORM models representing database schema
- **Database Layer**: `parser/database/` - Database creation, schema management, and updates
- **Writers**: `parser/DatabaseWriter.py`, `parser/APIWriter.py` - Handle data output to different targets
- **Configuration**: `config/` - Database connection and configuration parsing

The application uses SQLAlchemy 2.0+ for database operations with support for both PostgreSQL and SQLite backends.

## Development Commands

### Environment Setup
```bash
pipenv install --python 3.10 --dev
pipenv shell
```

### Code Quality
```bash
pipenv run black .          # Format code (79 char line limit)
pipenv run isort .          # Sort imports
pipenv run flake8           # Check style and syntax
```

### Testing
```bash
pipenv run pytest                    # Run all tests with coverage (80% threshold)
pipenv run pytest --cov-report=html # Generate HTML coverage report
pipenv run pytest -m "not slow"     # Skip slow tests
```

### Database Setup
For PostgreSQL testing, ensure test user exists:
```bash
psql -p 5432 -c "create role ximzid_unittests with password 'ximzid_unittests';"
psql -p 5432 -c 'alter role ximzid_unittests with login;'
psql -p 5432 -c 'alter role ximzid_unittests with createdb;'
psql -p 5432 -c 'GRANT pg_signal_backend TO ximzid_unittests;'
```

## Key Usage Patterns

### Validation
```bash
python parser.py -v ~/mydata                           # Validate directory
python parser.py -v ~/mydata/file.mzid -t ~/tempdir   # Validate single file
```

### Data Extraction
```bash
python parser.py --seqsandresiduepairs ~/mydata       # Extract residue pairs (JSON output)
```

### Database Population
```bash
python parser/database/create_db_schema.py             # Create schema
python parser.py -d ~/PXD038060                       # Process directory
python parser.py -p PXD038060                         # Process by ProteomeXchange ID
```

## Configuration

- Database configuration: `config/database.ini`
- Logging configuration: `config/logging.ini`
- Code formatting: 79 character line limit (configured in `.flake8`, `pyproject.toml`)

## Important Dependencies

- **pyteomics 4.7.3**: Core mzIdentML parsing (pinned version)
- **sqlalchemy >= 2.0.38**: Database ORM (modern async-compatible version)
- **psycopg2-binary**: PostgreSQL adapter
- **obonet 1.1.0**: Ontology parsing (pinned version)

## Testing Notes

Tests are organized in `tests/` with fixtures in `tests/fixtures/`. The test suite includes integration tests marked with `@pytest.mark.slow` that can be skipped during development. Coverage threshold is set to 80%.