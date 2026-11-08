"""MOCK restoration metadata, separate from real research/artifacts."""
from copy import deepcopy
import hashlib

import pytest
from restore_demo_assets import verify_restoration
from sample_fleurs import canonical


def test_restore_accepts_only_original_digest_with_proven_crlf_conversion():
    mapping = b'{"MOCK": true}\n'
    content = {"schema_version": "1.0", "source": {"language_map_sha256": hashlib.sha256(mapping).hexdigest()},
               "selection": {"ids": [1]}, "samples": [{"sample_id": "MOCK"}], "assets": [{"sha256": "MOCK"}]}
    digest = hashlib.sha256(canonical(content)).hexdigest()
    published = {**content, "generated_at_utc": "2026-11-07T00:00:00Z",
                 "source": {**content["source"], "selection_sha256": digest}}
    candidate = deepcopy(content)
    candidate["source"]["language_map_sha256"] = hashlib.sha256(mapping.replace(b'\n', b'\r\n')).hexdigest()
    assert verify_restoration(published, candidate, mapping.replace(b'\n', b'\r\n'))["selection_sha256"] == digest
    candidate["assets"][0]["sha256"] = "changed"
    with pytest.raises(ValueError, match="asset hashes"):
        verify_restoration(published, candidate, mapping)
    with pytest.raises(ValueError, match="beyond Git CRLF"):
        verify_restoration(published, candidate, b'changed mapping')
