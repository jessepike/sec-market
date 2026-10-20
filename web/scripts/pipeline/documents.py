"""Bounded primary-document decoding, preserving original bytes separately."""
import subprocess
import tempfile
from pathlib import Path

from contracts import require
from discovery import Page


def readable_document(body, content_type=""):
    if body.startswith(b"%PDF-") or "application/pdf" in content_type:
        with tempfile.TemporaryDirectory(prefix="smp-pdf-") as directory:
            source, destination = Path(directory) / "source.pdf", Path(directory) / "text.txt"
            source.write_bytes(body)
            result = subprocess.run(["pdftotext", "-layout", str(source), str(destination)], capture_output=True, timeout=30)
            require(result.returncode == 0 and destination.exists(), "PDF_TEXT_EXTRACTION_FAILED")
            require(destination.stat().st_size <= 8_000_000, "PDF_TEXT_BUDGET_EXCEEDED")
            text = destination.read_text(errors="replace")
    else:
        text = Page(body.decode("utf8", errors="replace")).readable
    require(len(text.strip()) >= 100, "DOCUMENT_HAS_NO_READABLE_TEXT")
    opening = text[:2000].lower()
    require(not any(s in opening for s in ("your request originates from an undeclared automated tool", "request rate threshold exceeded", "access denied", "verify you are human")), "SOURCE_BLOCK_PAGE")
    return text
