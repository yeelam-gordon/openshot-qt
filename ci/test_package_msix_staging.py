# SPDX-FileCopyrightText: 2026 OpenShot Studios, LLC
# SPDX-License-Identifier: LGPL-3.0-or-later

import json
import shutil
import subprocess
import unittest
from pathlib import Path
from xml.etree import ElementTree


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "installer" / "package_msix.ps1"
BUILD_DIR = REPO_ROOT / "build"
MSIX_DIR = BUILD_DIR / "msix"
FIXTURE_DIR = BUILD_DIR / "test-package-msix-staging"
INSTALLER_PATH = FIXTURE_DIR / "OpenShot-msix-staging-arm64.exe"
TEMPLATE_PATH = FIXTURE_DIR / "OpenShot_template.xml"
REPORT_PATH = MSIX_DIR / "prepare-report.json"
WORKING_TEMPLATE_PATH = MSIX_DIR / "OpenShot_template.generated.xml"
STAGED_INSTALLER_PATH = MSIX_DIR / "installer-source" / INSTALLER_PATH.name
VERSION_FILE = BUILD_DIR / "install-arm64" / "share" / "openshot-qt.env"


def remove_path(path):
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        path.unlink()


class PackageMsixStagingTests(unittest.TestCase):
    def setUp(self):
        for path in (REPORT_PATH, WORKING_TEMPLATE_PATH, STAGED_INSTALLER_PATH):
            remove_path(path)
        remove_path(MSIX_DIR / "installer-source")
        remove_path(FIXTURE_DIR)
        remove_path(MSIX_DIR / "old-package.msix")
        remove_path(MSIX_DIR / "msix-packaging-tool.log")

        FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
        MSIX_DIR.mkdir(parents=True, exist_ok=True)
        VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        VERSION_FILE.write_text("VERSION:4.0.0\n", encoding="utf-8")

    def tearDown(self):
        remove_path(FIXTURE_DIR)
        remove_path(MSIX_DIR)
        remove_path(BUILD_DIR / "install-arm64")
        if BUILD_DIR.exists() and not any(BUILD_DIR.iterdir()):
            BUILD_DIR.rmdir()

    def test_prepare_only_preserves_existing_packaging_outputs_and_refreshes_owned_staging(self):
        INSTALLER_PATH.write_bytes(b"fresh-arm64-installer")
        TEMPLATE_PATH.write_text(
            "\n".join(
                [
                    "<MsixPackagingToolTemplate>",
                    '  <SaveLocation PackagePath="C:\\OpenShot-MSIX\\OpenShot.msix" TemplatePath="C:\\OpenShot-MSIX\\OpenShot-template.xml" />',
                    '  <Installer Path="C:\\OpenShot-MSIX\\source\\OpenShot-original-arm64.exe" Arguments="/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-" InstallLocation="C:\\Program Files\\OpenShot Video Editor" />',
                    '  <PackageInformation PackageName="Old.Name" PublisherName="CN=Old Publisher" PublisherDisplayName="Old Publisher" Version="1.0.0.0">',
                    "    <Applications />",
                    "  </PackageInformation>",
                    "</MsixPackagingToolTemplate>",
                ]
            ),
            encoding="utf-8",
        )

        stale_msix = MSIX_DIR / "old-package.msix"
        stale_msix.write_bytes(b"stale-msix")
        stale_log = MSIX_DIR / "msix-packaging-tool.log"
        stale_log.write_text("stale-log", encoding="utf-8")
        stale_report = REPORT_PATH
        stale_report.write_text('{"stale": true}', encoding="utf-8")
        stale_working_template = WORKING_TEMPLATE_PATH
        stale_working_template.write_text("stale-template", encoding="utf-8")
        stale_source_dir = MSIX_DIR / "installer-source"
        stale_source_dir.mkdir(parents=True, exist_ok=True)
        (stale_source_dir / "stale.txt").write_text("stale", encoding="utf-8")
        (stale_source_dir / INSTALLER_PATH.name).write_bytes(b"old-installer")

        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(SCRIPT_PATH),
                "-Architecture",
                "arm64",
                "-InstallerPath",
                str(INSTALLER_PATH),
                "-TemplatePath",
                str(TEMPLATE_PATH),
                "-PrepareOnly",
                "-PreparationReportPath",
                str(REPORT_PATH),
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}",
        )

        self.assertTrue(stale_msix.exists())
        self.assertEqual(stale_msix.read_bytes(), b"stale-msix")
        self.assertTrue(stale_log.exists())
        self.assertEqual(stale_log.read_text(encoding="utf-8"), "stale-log")
        self.assertFalse((stale_source_dir / "stale.txt").exists())

        self.assertTrue(STAGED_INSTALLER_PATH.exists())
        self.assertEqual(STAGED_INSTALLER_PATH.read_bytes(), INSTALLER_PATH.read_bytes())

        self.assertTrue(REPORT_PATH.exists())
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
        self.assertNotEqual(REPORT_PATH.read_text(encoding="utf-8-sig"), '{"stale": true}')
        self.assertEqual(report["output_dir"], str(MSIX_DIR))
        self.assertEqual(report["source_installer_dir"], str(MSIX_DIR / "installer-source"))
        self.assertEqual(report["source_installer_path"], str(STAGED_INSTALLER_PATH))
        self.assertEqual(report["working_template_path"], str(WORKING_TEMPLATE_PATH))
        self.assertEqual(report["processor_architecture"], "arm64")
        self.assertEqual(report["publisher"], "CN=5FE34B8B-A62B-4594-911F-0D6CFC87D00F")
        self.assertEqual(report["publisher_display_name"], "OpenShot Studios")

        self.assertTrue(WORKING_TEMPLATE_PATH.exists())
        working_template = WORKING_TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertNotEqual(working_template, "stale-template")
        self.assertIn(str(STAGED_INSTALLER_PATH), working_template)
        self.assertNotIn(r"C:\OpenShot-MSIX\source\OpenShot-original-arm64.exe", working_template)
        template_xml = ElementTree.fromstring(working_template)
        package_info = template_xml.find(".//PackageInformation")
        self.assertEqual(package_info.attrib["Version"], "4.0.0.0")
        self.assertEqual(package_info.attrib["PackageName"], "OpenShotStudios.OpenShotforWindows")
        self.assertEqual(
            package_info.attrib["PublisherName"],
            "CN=5FE34B8B-A62B-4594-911F-0D6CFC87D00F",
        )
        self.assertEqual(package_info.attrib["PublisherDisplayName"], "OpenShot Studios")


if __name__ == "__main__":
    unittest.main()
