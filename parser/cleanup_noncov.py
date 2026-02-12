"""Noncov cleanup for mzIdentML files.

Removes invalid crosslink modifications at location="-1" (MS:1002509/MS:1002510)
and their corresponding MS:1002511 cvParams from SpectrumIdentificationItems.
"""

import gzip
import logging
import os
import shutil
import tempfile

from lxml import etree

logger = logging.getLogger(__name__)


def cleanup_noncov(input_path, output_path):
    """Clean up invalid noncov crosslink modifications from an mzIdentML file.

    Removes Modification elements at location="-1" that have crosslink donor
    (MS:1002509) or acceptor (MS:1002510) cvParams. Also removes corresponding
    MS:1002511 (crosslink spectrum identification item) cvParams from
    SpectrumIdentificationItems that reference the affected peptides.

    Args:
        input_path: Path to the input .mzid file.
        output_path: Path to write the cleaned .mzid file.

    Returns:
        Tuple of (peptides_cleaned, modifications_removed, sii_cleaned).
    """
    tree = etree.parse(input_path)
    root = tree.getroot()

    # Dynamically detect namespace
    ns_uri = root.nsmap.get(None)
    ns = {"mzid": ns_uri}

    # Step 1: Find and clean peptides with crosslink donor/acceptor at location -1
    peptides_to_clean = set()
    peps_cleaned = 0
    mods_removed = 0

    for peptide in root.xpath(".//mzid:Peptide", namespaces=ns):
        peptide_id = peptide.get("id")
        removed = False
        for mod in peptide.xpath(
            './mzid:Modification[@location="-1"]', namespaces=ns
        ):
            if mod.xpath(
                './mzid:cvParam[@accession="MS:1002510" or @accession="MS:1002509"]',
                namespaces=ns,
            ):
                peptide.remove(mod)
                removed = True
                mods_removed += 1
        if removed:
            peptides_to_clean.add(peptide_id)
            peps_cleaned += 1

    # Step 2: Remove cross-link spectrum identification item cvParam
    sii_cleaned = 0
    for sii in root.xpath(
        ".//mzid:SpectrumIdentificationItem", namespaces=ns
    ):
        if sii.get("peptide_ref") in peptides_to_clean:
            for cv in sii.xpath(
                './mzid:cvParam[@accession="MS:1002511"]', namespaces=ns
            ):
                sii.remove(cv)
                sii_cleaned += 1

    # Write the updated XML to output_path
    with open(output_path, "wb") as out_f:
        out_f.write(
            etree.tostring(
                root,
                encoding="UTF-8",
                xml_declaration=True,
                pretty_print=True,
            )
        )

    return peps_cleaned, mods_removed, sii_cleaned


def cleanup_noncov_gz(input_path, output_path):
    """Clean up noncov modifications from a .mzid.gz file.

    Decompresses, applies cleanup_noncov, and recompresses.
    If input is not actually gzipped (despite .gz extension), treats as plain .mzid.

    Args:
        input_path: Path to the input .mzid.gz file.
        output_path: Path to write the cleaned .mzid.gz file.

    Returns:
        Tuple of (peptides_cleaned, modifications_removed, sii_cleaned).
    """
    # Check if file is actually gzipped
    with open(input_path, "rb") as f:
        is_gzipped = f.read(2) == b"\x1f\x8b"

    if not is_gzipped:
        return cleanup_noncov(input_path, output_path)

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".mzid"
    ) as tmp_file:
        tmp_path = tmp_file.name
        with gzip.open(input_path, "rb") as gz_in:
            shutil.copyfileobj(gz_in, tmp_file)

    try:
        peps_cleaned, mods_removed, sii_cleaned = cleanup_noncov(
            tmp_path, tmp_path
        )

        if peps_cleaned > 0 or mods_removed > 0 or sii_cleaned > 0:
            with gzip.open(output_path, "wb") as gz_out:
                with open(tmp_path, "rb") as tmp_in:
                    shutil.copyfileobj(tmp_in, gz_out)
        elif input_path != output_path:
            shutil.copy2(input_path, output_path)

        return peps_cleaned, mods_removed, sii_cleaned
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
