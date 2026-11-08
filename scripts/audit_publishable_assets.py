"""Read-only T-019 audit; never packages, deletes, generates audio or contacts APIs.

Checks Git index bytes separately from the working tree and public/dist (including
ignored audio). Findings contain paths/codes only, never matched secret values.
Exit 0 = no findings for selected target, 1 = blocked, 2 = audit could not finish.
This bounded heuristic is not a comprehensive secret/PII or legal clearance scan.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services.elevenlabs_adapter import load_selection
from app.services.tts_adapter import validate_manifest
from app.services.tts_config import LANGUAGES

MEDIA = {'.flac', '.mp3', '.wav', '.ogg', '.m4a', '.mp4', '.webm'}
RAW = {'.zip', '.7z', '.tar', '.gz', '.csv', '.tsv', '.parquet', '.pem', '.key'}
SECRETS = [re.compile(rb'\bsk_[A-Za-z0-9]{20,}\b'),
           re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
           re.compile(rb'''(?im)["']?(?:ELEVENLABS_API_KEY|api[_-]?key|xi-api-key|access_token|client_secret)["']?\s*[:=]\s*["']?([A-Za-z0-9_+/=-]{16,})''')]
PII = {'birth_city', 'birthplace', 'city_of_birth', 'date_of_birth', 'speaker_name',
       'speaker_age', 'email', 'email_address', 'phone_number', 'first_name', 'last_name'}
DATA = {'languages.v1.json', 'wards.v1.json', 'samples.v1.json',
        'experiments.v1.json', 'recommendations.v1.json',
        'mississauga_wards.geojson', 'ward_geometry_status.json', '.gitkeep'}
THEME_IMAGE_SHA256 = 'cc99a8a383d856431cea6b06f0eb97383d2df54a0bba1de52a4f030e4e7eb218'


def built_asset(relative: str, raw: bytes) -> bool:
    """Allow normal code/style outputs and only the exact user-supplied SDG art."""
    return relative.startswith('assets/') and (PurePosixPath(relative).suffix in {'.js', '.css'}
        or PurePosixPath(relative).suffix == '.png' and hashlib.sha256(raw).hexdigest() == THEME_IMAGE_SHA256)


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(ROOT), *args], stderr=subprocess.DEVNULL)


def private_fields(value) -> bool:
    if isinstance(value, dict):
        return any(str(k).lower() in PII or private_fields(v) for k, v in value.items())
    return isinstance(value, list) and any(private_fields(v) for v in value)


def audit(target: str) -> dict:
    findings: set[tuple[str, str, str]] = set()
    counts = Counter()
    inventory = []

    def flag(scope: str, name: str, code: str):
        findings.add((scope, name, code))

    # Reuse the existing immutable sampling digest/identity validator. If it
    # fails, the audit aborts rather than trusting filenames as approvals.
    samples, assets, digest = load_selection()
    expected = {}
    for sample in samples.samples:
        path = PurePosixPath(sample.audio_path)
        if path.is_absolute() or '..' in path.parts or not str(path).startswith('audio/'):
            raise ValueError('Unsafe frozen sample path')
        expected[str(path)] = assets[sample.sample_id]
    source = samples.source
    if (source.get('license') != 'CC BY 4.0'
            or source.get('source_url') != 'https://huggingface.co/datasets/google/fleurs'
            or source.get('license_url') != 'https://creativecommons.org/licenses/by/4.0/'
            or not source.get('attribution') or not source.get('modifications')):
        raise ValueError('Frozen sample attribution/licence metadata unavailable')

    def inspect(scope: str, name: str, raw: bytes):
        counts[scope] += 1
        path = PurePosixPath(name)
        if (path.suffix.lower() in RAW or any(p in {'data', 'raw', 'recordings'} for p in path.parts[:1])
                or any(p.startswith('.env') and p != '.env.example' for p in path.parts)
                or path.name.lower().startswith('credentials')):
            flag(scope, name, 'private_or_bulk_file')
        if any(pattern.search(raw) for pattern in SECRETS):
            flag(scope, name, 'possible_secret')
        if path.name == '.env.example':
            for line in raw.decode('utf-8').splitlines():
                key, separator, value = line.partition('=')
                if separator and re.search(r'(API_KEY|SECRET|TOKEN)$', key.strip(), re.I) and value.strip().strip(chr(34) + chr(39)):
                    flag(scope, name, 'populated_credential_example')
        if name.startswith('frontend/public/'):
            relative = name[len('frontend/public/'):]
            parts = PurePosixPath(relative).parts
            allowed_data = (len(parts) == 2 and parts[0] == 'data' and parts[-1] in DATA
                            or len(parts) == 3 and parts[:2] == ('data', 'fixtures') and parts[-1] in DATA)
            prompt = (len(parts) == 4 and parts[:2] == ('audio', 'prompts')
                      and parts[2] in LANGUAGES and parts[3] in {'manifest.json', 'confirm.mp3'})
            built = scope == 'frontend/dist' and built_asset(relative, raw)
            if not (allowed_data or prompt or built or relative in expected
                    or relative in {'index.html', 'audio/FLEURS_ATTRIBUTION.txt', 'audio/prompts/README.md'}):
                flag(scope, name, 'unlisted_public_asset')
        if path.suffix in {'.json', '.geojson'}:
            try:
                if private_fields(json.loads(raw)):
                    flag(scope, name, 'personal_metadata_field')
            except (ValueError, UnicodeError):
                flag(scope, name, 'invalid_json')
        if path.suffix.lower() in MEDIA:
            # Staged media is never covered by a blanket wildcard approval.
            prefix = 'frontend/public/'
            relative = name[len(prefix):] if name.startswith(prefix) else None
            if relative not in expected:
                flag(scope, name, 'media_requires_explicit_review')
            elif hashlib.sha256(raw).hexdigest() != expected[relative]['sha256']:
                flag(scope, name, 'frozen_audio_hash_mismatch')

    indexed = set()
    for entry in git('ls-files', '--stage', '-z').split(b'\0'):
        if not entry:
            continue
        metadata, encoded = entry.split(b'\t', 1)
        mode, blob, stage = metadata.decode().split()
        name = encoded.decode('utf-8')
        indexed.add(name)
        if mode not in {'100644', '100755'} or stage != '0':
            flag('index', name, 'symlink_submodule_or_unmerged')
            continue
        inspect('index', name, git('cat-file', 'blob', blob))

    others = git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')
    for name in sorted(indexed | {p for p in others if p}):
        path = ROOT / name
        if path.is_symlink():
            flag('worktree', name, 'symlink')
        elif path.is_file():
            inspect('worktree', name, path.read_bytes())

    for directory in ('frontend/public', 'frontend/dist'):
        base = ROOT / directory
        if not base.exists():
            if directory.endswith('dist'):
                flag(directory, directory, 'build_not_available')
            continue
        for path in sorted(base.rglob('*')):
            name = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                flag(directory, name, 'symlink')
                continue
            if not path.is_file():
                continue
            relative = path.relative_to(base).as_posix()
            raw = path.read_bytes()
            # Scan text/metadata/secrets for all build bytes too; media is
            # classified by exact public-relative identity below.
            inspect(directory, 'frontend/public/' + relative, raw)
            if relative in expected:
                asset = expected[relative]
                if (len(raw) != asset['size_bytes'] or not raw.startswith(b'fLaC')
                        or hashlib.sha256(raw).hexdigest() != asset['sha256']):
                    flag(directory, name, 'frozen_audio_mismatch')
                inventory.append({'scope': directory, 'path': relative,
                                  'sample_id': asset['sample_id'], 'license': source['license'],
                                  'sha256': hashlib.sha256(raw).hexdigest()})
            elif relative.startswith('audio/prompts/') and relative != 'audio/prompts/README.md':
                parts = PurePosixPath(relative).parts
                language = parts[2] if len(parts) == 4 else None
                try:
                    prompt_dir = base / 'audio/prompts' / language if language in LANGUAGES else None
                    if (prompt_dir is None or parts[-1] not in {'confirm.mp3', 'manifest.json'}
                            or not validate_manifest(json.loads((prompt_dir / 'manifest.json').read_bytes()),
                                                     (prompt_dir / 'confirm.mp3').read_bytes(), language, approved=True)):
                        flag(directory, name, 'unapproved_prompt')
                    else:
                        # Remove generic media finding only for exact approved cache.
                        findings.discard((directory, 'frontend/public/' + relative, 'media_requires_explicit_review'))
                        if target == 'public':
                            flag(directory, name, 'tts_account_voice_distribution_rights_review_required')
                except (OSError, ValueError, KeyError, TypeError):
                    flag(directory, name, 'unapproved_prompt')
            elif relative not in {'index.html', 'audio/FLEURS_ATTRIBUTION.txt', 'audio/prompts/README.md'}:
                fixture = relative.startswith('data/fixtures/') and PurePosixPath(relative).name in DATA
                data = relative.startswith('data/') and len(PurePosixPath(relative).parts) == 2 and PurePosixPath(relative).name in DATA
                built = directory.endswith('dist') and built_asset(relative, raw)
                if not (fixture or data or built):
                    flag(directory, name, 'unlisted_public_asset')
        for relative in expected:
            if not (base / relative).is_file():
                flag(directory, relative, 'selected_audio_missing')
        notice = base / 'audio/FLEURS_ATTRIBUTION.txt'
        if not notice.is_file() or not all(str(source[k]) in notice.read_text(encoding='utf-8')
                                          for k in ('attribution', 'source_url', 'license_url', 'modifications')):
            flag(directory, 'audio/FLEURS_ATTRIBUTION.txt', 'attribution_missing_or_stale')

    if target == 'public':
        flag('policy', 'municipal census and ward geometry', 'applicable_city_redistribution_terms_unresolved')
        flag('policy', 'saved provider outputs', 'provider_account_output_rights_review_required')
    return {'schema_version': '1.0', 'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'target': target, 'status': 'blocked' if findings else 'passed',
            'git_head': git('rev-parse', 'HEAD').decode().strip(),
            'selection_sha256': digest, 'selected_samples': len(samples.samples),
            'fleurs_attribution': {k: source[k] for k in ('attribution', 'source_url', 'license', 'license_url', 'modifications')},
            'files_inspected': dict(counts), 'audio_inventory': inventory,
            'findings': [{'scope': s, 'path': p, 'code': c} for s, p, c in sorted(findings)],
            'limitations': ['Index and current worktree/public/dist only; not Git history or remote objects.',
                            'Heuristic secret/PII checks; manual review remains required.',
                            'No account rights, human listening or legal approval is inferred.']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('local', 'public'), default='local')
    args = parser.parse_args()
    try:
        report = audit(args.target)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        # Never print exception text: it may contain private paths or payloads.
        print(json.dumps({'status': 'audit_error', 'code': 'inputs_or_git_unavailable'}))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if report['findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
