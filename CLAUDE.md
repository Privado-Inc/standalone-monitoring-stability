# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a standalone monitoring stability tool that compares different branches of the Privado Core privacy analysis engine and the Privado rules repository. The tool analyzes various open-source repositories to ensure consistency and stability across different versions.

## Architecture

The project is structured around comparing two main components:
- **Privado Core Enterprise**: Privacy analysis engine (Scala-based with build.sbt)
- **Privado Rules**: Rule definitions for privacy analysis
- **Joern**: Code analysis platform (also Scala-based)

The tool manages multiple temporary directories for different comparison scenarios:
- `direct-comp-data/`: Contains cloned versions of repositories for direct comparison
- `temp-*/`: Temporary directories for different test runs
- `privado-core-temp/`: Working directory for privado-core builds
- `result/`: Contains scan results and analysis outputs

## Common Commands

### Environment Setup
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Basic Comparison
```bash
# Compare two branches
python3 ./run.py -f [first_branch] -s [second_branch]

# Compare with custom repository list
python3 ./run.py -r path_to_file.txt -f [base_branch] -s [head_branch]

# Upload results to Slack
python3 ./run.py -b [base_branch] -h [head_branch] --upload

# Clear cache and binary data
python3 ./run.py -b [base_branch] -h [head_branch] -c
```

### Docker-based Comparison
```bash
# Use Docker instead of building binaries
python3 ./run.py --use-docker -b [base_docker_tag] -h [head_docker_tag]
```

### Privado Branch Comparison
```bash
# Compare privado branches
python3 ./run.py -rbb [privado_base_branch] -rbh [privado_head_branch] -urc

# Compare existing privado.json files
python3 ./run.py -b [base_privado_json_path] -h [head_privado_json_path] -m
```

### Joern Operations
```bash
# For Scala/Joern components, use sbt for building
sbt compile
sbt test
sbt stage  # For creating distributions
```

## Key Components

### Core Python Modules
- `run.py`: Main entry point with argument parsing
- `config.py`: Configuration constants and branch management
- `builder.py`: Binary building logic
- `utils/`: Core functionality modules
  - `scan.py`: Repository scanning and analysis
  - `compare.py`: Comparison logic between branches
  - `build_binary.py`: Binary building for different branches
  - `clone_repo.py`: Repository cloning and management

### Repository Lists
Repository lists are stored in `repos/` directory, organized by language:
- `java-1.txt`, `java-2.txt`: Java repositories
- `kotlin.txt`: Kotlin repositories  
- `python.txt`: Python repositories
- `js.txt`: JavaScript repositories
- And others for different languages

### Output Structure
Results are stored in structured directories:
```
temp/
├── privado/           # Privado rules for each branch
├── privado-core/      # Privado core builds for each branch  
└── result/            # Scan results and analysis
    ├── [base_branch]/
    │   ├── repo-output.txt    # Scan results
    │   └── repo.json          # Privado.json output
    └── [head_branch]/
        ├── repo-output.txt
        └── repo.json
```

## Development Workflow

1. The tool clones and builds different versions of Privado Core and Rules
2. Runs privacy analysis on test repositories using both versions
3. Compares results to identify differences in behavior
4. Generates Excel reports with detailed comparisons
5. Optionally uploads summaries to Slack

## Docker Integration

The tool supports Docker-based execution to avoid local binary building. Docker tags are used to specify which versions to compare, with containers handling the build and execution process.

## Testing

No formal test suite exists. Testing is done through comparison runs against known repositories with expected outputs.