"""All runtime paths are resolved from the project, never the working directory."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
KNOWLEDGE_DIR = DATA_DIR / 'knowledge_base'
CASES_DIR = DATA_DIR / 'cases'
ENV_FILE = ROOT / '.env'
