"""Produce a deterministic, source-only Overleaf upload bundle.

This is NOT a compiled Springer PDF and does NOT modify live Overleaf.
Import these files into an official publisher template preserving sn-jnl.cls.
"""
import argparse
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "overleaf"
WHITELIST = ("main.tex", "references.bib", "README.md")
FIXED_DATE = (2026, 10, 24, 0, 0, 0)


def bundle_bytes() -> bytes:
    """Stable, inspectable archive; no secrets, unlicensed code or hidden data."""
    files: dict[str, bytes] = {}
    for filename in WHITELIST:
        path = PAPER / filename
        files[filename] = path.read_bytes()
    checksums = [
        f"{hashlib.sha256(content).hexdigest()}  {filename}"
        for filename, content in sorted(files.items())
    ]
    files["BUNDLE_SHA256.txt"] = ("\n".join(checksums) + "\n").encode("utf-8")
    stream = io.BytesIO()
    with ZipFile(stream, mode="w") as zipped:
        for filename, content in sorted(files.items()):
            info = ZipInfo(filename, date_time=FIXED_DATE)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            zipped.writestr(info, content, compress_type=ZIP_DEFLATED,
                            compresslevel=9)
    return stream.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("dist/UCODE_Overleaf_sources.zip"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data = bundle_bytes()
    args.output.write_bytes(data)
    print(f"OVERLEAF_SOURCE_ONLY={args.output} BYTES={len(data)}")
    print(f"SHA256={hashlib.sha256(data).hexdigest()}")
    print("IMPORT_INTO_OFFICIAL_SPRINGER_TEMPLATE; LIVE_OVERLEAF_NOT_MODIFIED")


if __name__ == "__main__":
    main()
