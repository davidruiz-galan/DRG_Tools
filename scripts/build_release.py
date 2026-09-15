"""Build a clean, verified DRG Tools ZIP using only Python's standard library."""
from pathlib import Path
import ast
import hashlib
import json
import re
import zipfile

repo = Path(__file__).resolve().parents[1]
root = repo / 'DRG_Tools'
version = (root / 'VERSION').read_text().strip()
assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version), 'Invalid version'
metadata = json.loads((root / 'manifest.json').read_text(encoding='utf-8-sig'))
assert metadata['version'] == version, 'Manifest version mismatch'
tree = ast.parse((root / 'python/drg_tools/config.py').read_text(encoding='utf-8-sig'))
values = {target.id: ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) for target in node.targets if isinstance(target, ast.Name)}
assert values['VERSION'] == version, 'Config version mismatch'
files = sorted(p for p in root.rglob('*') if p.is_file() and not any(part.startswith('.') or part in ('__pycache__', 'dev') for part in p.relative_to(root).parts) and p.suffix != '.pyc')
for p in files:
    if p.suffix == '.py':
        ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p), feature_version=(3, 11))
for required in ('init.py', 'menu.py', 'LICENSE.txt', 'docs/INSTALL.md', 'docs/INSTALACION_ES.md'):
    assert (root / required).is_file(), required
out = repo / 'dist'
out.mkdir(exist_ok=True)
archive = out / ('DRG_Tools_v' + version + '.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files:
        info = zipfile.ZipInfo(p.relative_to(repo).as_posix(), (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, p.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for p in files:
        assert z.read(p.relative_to(repo).as_posix()) == p.read_bytes()
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='utf-8')
print(f'Verified {len(files)} files: {archive}')
print('Nuke interactive and rendering tests must be performed separately.')
