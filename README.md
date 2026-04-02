# SSW567-Project

MRTD (Machine-Readable Travel Document) system for encoding, decoding, and validating passport MRZ data using Fletcher-16 checksums.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (for dependency management)

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip install coverage
```

## Running Tests

```bash
python -m unittest MTTDtest -v
```

## Coverage

```bash
.venv/bin/coverage run -m unittest MTTDtest
.venv/bin/coverage report -m --include=MRTD.py
```

## Mutation Testing (MutPy)

Requires Python 3.7.15 via [Conda](https://docs.conda.io/en/latest/miniconda.html) (MutPy does not work reliably on newer Python versions).

### MutPy Setup

```bash
# Install Miniconda (if not already installed)
curl -fsSL -o /tmp/Miniconda3-latest-MacOSX-arm64.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash /tmp/Miniconda3-latest-MacOSX-arm64.sh -b -p $HOME/miniconda3

# Create environment with Python 3.7.15 (x86 via Rosetta on ARM Mac)
CONDA_SUBDIR=osx-64 $HOME/miniconda3/bin/conda create -n mutpy python=3.7.15 -y

# Install MutPy
$HOME/miniconda3/envs/mutpy/bin/python -m pip install mutpy
```

### Running MutPy

```bash
$HOME/miniconda3/envs/mutpy/bin/python $HOME/miniconda3/envs/mutpy/bin/mut.py \
  --target MRTD \
  --unit-test tests.test_calculate_check_digit tests.test_scan_mrz \
  tests.test_query_database tests.test_decode_mrz tests.test_encode_mrz \
  tests.test_validate_mrz tests.test_round_trip tests.test_mutpy_additional \
  -m
```

Note: MutPy must be pointed at individual test modules (not `MTTDtest`) due to how MutPy's module injection works with the test package structure.

See [MUTPY_REPORT.md](MUTPY_REPORT.md) for full results and analysis.
