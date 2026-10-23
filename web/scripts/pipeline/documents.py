"""Bounded primary-document decoding, preserving original bytes separately."""
import subprocess
import tempfile
from pathlib import Path

from contracts import digest, require
from discovery import Page, decoded_discovery_body


def article_input(body, observation):
    """Return one parser/model view, leaving original evidence bytes untouched.

    Plain input keeps the existing extractor identity and has no descriptor.
    Compressed input binds both its decoded bytes and actual scoped model text.
    """
    compressed = body.startswith(b'\x1f\x8b')
    decoded = decoded_discovery_body(body) if compressed else body
    source_url = observation.get('finalUrl') or observation['requestedUrl']
    page = Page(decoded.decode('utf8', errors='strict' if compressed else 'replace'), source_url=source_url)
    base = 5 if page.scoped_extraction else 4 if page.published_from_time else 3
    model_text = (f'Source publication date metadata: {page.published}\n' if page.published else '') + page.readable
    descriptor = None
    if compressed:
        descriptor = {'schemaVersion': 1, 'inputView': 'bounded-gzip-1', 'extractor': base,
                      'sourceUrl': source_url, 'rawSha256': digest(body), 'decodedSha256': digest(decoded),
                      'decodedBytes': len(decoded), 'articleSha256': digest(page.readable.encode()),
                      'modelInputSha256': digest(model_text.encode()), 'modelInputChars': len(model_text)}
    return {'page': page, 'modelText': model_text, 'decoded': decoded,
            'extractor': {'inputView': 'bounded-gzip-1', 'extractor': base, 'inputSha256': digest(descriptor)} if compressed else base,
            'compressedInput': descriptor}


def verify_article_input(record, body, observation):
    """Require exact decoded-input provenance only for compressed articles."""
    view = article_input(body, observation)
    if view['compressedInput'] is not None:
        require(record.get('compressedInput') == view['compressedInput'], 'COMPRESSED_ARTICLE_INPUT_DIFFERS_OR_MISSING')
    return view


def readable_document(body, content_type=""):
    compressed = body.startswith(b'\x1f\x8b')
    body = decoded_discovery_body(body)
    if body.startswith(b"%PDF-") or "application/pdf" in content_type:
        with tempfile.TemporaryDirectory(prefix="smp-pdf-") as directory:
            source, destination = Path(directory) / "source.pdf", Path(directory) / "text.txt"
            source.write_bytes(body)
            result = subprocess.run(["pdftotext", "-layout", str(source), str(destination)], capture_output=True, timeout=30)
            require(result.returncode == 0 and destination.exists(), "PDF_TEXT_EXTRACTION_FAILED")
            require(destination.stat().st_size <= 8_000_000, "PDF_TEXT_BUDGET_EXCEEDED")
            text = destination.read_text(errors="replace")
    else:
        text = Page(body.decode('utf8', errors='strict' if compressed else 'replace')).readable
    require(len(text.strip()) >= 100, "DOCUMENT_HAS_NO_READABLE_TEXT")
    opening = text[:2000].lower()
    require(not any(s in opening for s in ("your request originates from an undeclared automated tool", "request rate threshold exceeded", "access denied", "verify you are human")), "SOURCE_BLOCK_PAGE")
    return text
