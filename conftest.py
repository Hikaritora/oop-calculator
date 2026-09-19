import sys
from pathlib import Path

# Makes sure "from models.memory import Memory" etc. works in tests,
# no matter which directory pytest is run from.
sys.path.insert(0, str(Path(__file__).parent))
