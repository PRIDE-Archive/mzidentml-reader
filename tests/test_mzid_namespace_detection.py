"""Tests for the root-namespace-prefix detection used to surface a clear
error when pyteomics' offset index silently fails on prefixed mzIdentML files.

See issue #109.
"""

from parser.MzIdParser import _root_namespace_prefix


PREFIXED_MZID = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<ns0:MzIdentML xmlns:ns0="http://psidev.info/psi/pi/mzIdentML/1.3" '
    'id="x" version="1.3.0">\n'
    '  <ns0:cvList/>\n'
    '</ns0:MzIdentML>\n'
)

DEFAULT_NS_MZID = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<MzIdentML xmlns="http://psidev.info/psi/pi/mzIdentML/1.3" '
    'id="x" version="1.3.0">\n'
    '  <cvList/>\n'
    '</MzIdentML>\n'
)


def test_detects_non_default_namespace_prefix(tmp_path):
    p = tmp_path / "prefixed.mzid"
    p.write_text(PREFIXED_MZID)
    assert _root_namespace_prefix(str(p)) == "ns0"


def test_returns_none_for_default_namespace(tmp_path):
    p = tmp_path / "default_ns.mzid"
    p.write_text(DEFAULT_NS_MZID)
    assert _root_namespace_prefix(str(p)) is None


def test_returns_none_for_missing_file(tmp_path):
    assert _root_namespace_prefix(str(tmp_path / "does_not_exist.mzid")) is None


def test_detects_arbitrary_prefix(tmp_path):
    p = tmp_path / "weird.mzid"
    p.write_text(
        '<?xml version="1.0"?>\n'
        '<psi:MzIdentML xmlns:psi="http://psidev.info/psi/pi/mzIdentML/1.2" '
        'id="x" version="1.2.0"/>\n'
    )
    assert _root_namespace_prefix(str(p)) == "psi"


def test_ignores_unrelated_xmlns_declarations(tmp_path):
    p = tmp_path / "mixed.mzid"
    p.write_text(
        '<?xml version="1.0"?>\n'
        '<MzIdentML xmlns="http://psidev.info/psi/pi/mzIdentML/1.3" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'id="x" version="1.3.0"/>\n'
    )
    assert _root_namespace_prefix(str(p)) is None
