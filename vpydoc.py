#! .venv/scripts/python.exe
import sys
from pydoc import cli

sys.argv.append("-b")
cli()
