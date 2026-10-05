"""Restore the complete project tree from the GitHub source archive."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
with zipfile.ZipFile(root / 'Repayment_Lab.zip') as archive:
    for item in archive.infolist():
        path = Path(item.filename)
        if path.parts[0] != 'repayment-lab' or '..' in path.parts or path.is_absolute():
            raise ValueError('Unexpected archive path')
        relative = Path(*path.parts[1:])
        if not relative.parts or item.is_dir() or relative.name == 'README.md':
            continue
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(item))
print('Restored SQL, tests, docs, workflow and ready-to-open demo. Run: python lab.py')
