"""deprecated: 改为调用 site_builder.py convert"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import site_builder
sys.exit(site_builder.main(["convert"]))