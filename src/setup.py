"""
Run this once to build all artifacts needed by the app.
Order: download_data -> build_bm25 -> build_semantic
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "src"

scripts = [
    SRC / "download_data.py",
    SRC / "build_bm25.py",
    SRC / "build_semantic.py",
]

for script in scripts:
    print(f"\n{'='*50}")
    print(f"Running {script.name}...")
    print('='*50)
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),          # always run from project root
        check=True
    )

print("\nAll artifacts built successfully.")