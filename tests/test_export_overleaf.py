"""No-network regression tests of deterministic paper-only archive export."""
import hashlib
import io
import unittest
from zipfile import ZipFile

from scripts.export_overleaf import bundle_bytes, WHITELIST, PAPER


class OverleafBundleTests(unittest.TestCase):
    def test_source_only_allowlist(self):
        with ZipFile(io.BytesIO(bundle_bytes())) as archive:
            self.assertEqual(
                set(archive.namelist()),
                set(WHITELIST) | {"BUNDLE_SHA256.txt"},
            )
            self.assertNotIn("sn-jnl.cls", archive.namelist())
            for name in WHITELIST:
                self.assertEqual(archive.read(name), (PAPER / name).read_bytes())

    def test_deterministic_archive_with_fixed_metadata(self):
        one, two = bundle_bytes(), bundle_bytes()
        self.assertEqual(hashlib.sha256(one).digest(), hashlib.sha256(two).digest())
        with ZipFile(io.BytesIO(one)) as archive:
            self.assertEqual(len({item.date_time for item in archive.infolist()}), 1)
            self.assertTrue(all("/" not in name for name in archive.namelist()))

    def test_sha256_manifest_covers_exact_sources(self):
        with ZipFile(io.BytesIO(bundle_bytes())) as archive:
            lines = archive.read("BUNDLE_SHA256.txt").decode().strip().splitlines()
            self.assertEqual(len(lines), len(WHITELIST))
            for line in lines:
                digest, filename = line.split("  ", 1)
                self.assertIn(filename, WHITELIST)
                self.assertEqual(digest, hashlib.sha256(archive.read(filename)).hexdigest())


if __name__ == "__main__":
    unittest.main()
