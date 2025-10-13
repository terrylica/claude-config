#!/usr/bin/env python3
"""
Simplified attachment extraction test - uses httpx only, no browser automation.
Tests with manually identified attachment URLs from Article 14760.
"""

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import httpx


# File categories to DOWNLOAD (plain text/readable only)
FILE_CATEGORIES = {
    "source": [".mq5", ".mq4"],
    "headers": [".mqh"],
    "notebooks": [".ipynb"],
    "data": [".csv", ".json", ".txt"],
    "docs": [".pdf", ".md"]
}

# File extensions to SKIP (binary executables)
SKIP_EXTENSIONS = {".ex5", ".ex4", ".bin", ".dat", ".dll", ".exe"}

# Safety limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_ARCHIVE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_ZIP_DEPTH = 2
MAX_FILES_PER_ARCHIVE = 1000


def should_download_file(filename: str) -> bool:
    """Check if file should be downloaded (plain text only)."""
    ext = os.path.splitext(filename)[1].lower()

    # Skip binary executables
    if ext in SKIP_EXTENSIONS:
        return False

    # Check if in download categories
    for extensions in FILE_CATEGORIES.values():
        if ext in extensions:
            return True

    # Skip unknown types by default
    return False


def get_file_category(filename: str) -> str:
    """Get category for a filename."""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "other"


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_file(url: str, output_path: Path) -> bool:
    """Download a file with safety checks."""
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            # Check file size
            content_length = int(response.headers.get('content-length', 0))
            if content_length > MAX_FILE_SIZE:
                print(f"⚠️  Skipping {output_path.name}: exceeds max size ({content_length / 1024 / 1024:.1f} MB)")
                return False

            # Write file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Downloaded: {output_path.name} ({len(response.content) / 1024:.1f} KB)")
            return True

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False


def extract_zip_safely(zip_path: Path, extract_to: Path, depth: int = 0) -> List[Path]:
    """Safely extract ZIP file with depth limit."""
    if depth > MAX_ZIP_DEPTH:
        print(f"⚠️  Skipping nested ZIP at depth {depth}: {zip_path.name}")
        return []

    extracted_files = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check number of files
            if len(zip_ref.namelist()) > MAX_FILES_PER_ARCHIVE:
                print(f"⚠️  Skipping ZIP with too many files: {zip_path.name}")
                return []

            # Extract files
            for member in zip_ref.namelist():
                # Skip directory entries
                if member.endswith('/'):
                    continue

                # Check if we should download this file
                if not should_download_file(member):
                    print(f"⏭️  Skipping binary/unwanted: {member}")
                    continue

                # Extract to category subdirectory
                category = get_file_category(member)
                target_dir = extract_to / category
                target_dir.mkdir(parents=True, exist_ok=True)

                # Extract file
                source = zip_ref.open(member)
                target_path = target_dir / os.path.basename(member)

                with open(target_path, 'wb') as target:
                    target.write(source.read())

                extracted_files.append(target_path)
                print(f"📦 Extracted: {member} → {category}/{os.path.basename(member)}")

                # Recursively extract nested ZIPs
                if target_path.suffix.lower() == '.zip':
                    nested_extracted = extract_zip_safely(target_path, extract_to, depth + 1)
                    extracted_files.extend(nested_extracted)

        print(f"✅ Extracted {len(extracted_files)} files from {zip_path.name}")

    except Exception as e:
        print(f"❌ Failed to extract {zip_path.name}: {e}")

    return extracted_files


def deduplicate_files(attachments_dir: Path) -> int:
    """Deduplicate files based on SHA256 checksums."""
    checksums = {}
    duplicates_removed = 0

    for category_dir in attachments_dir.iterdir():
        if not category_dir.is_dir():
            continue

        for file_path in category_dir.glob('*'):
            if not file_path.is_file():
                continue

            checksum = calculate_sha256(file_path)

            if checksum in checksums:
                # Duplicate found - remove it
                print(f"🔄 Removing duplicate: {file_path.name} (same as {checksums[checksum].name})")
                file_path.unlink()
                duplicates_removed += 1
            else:
                checksums[checksum] = file_path

    return duplicates_removed


def generate_manifest(
    article_id: str,
    attachments_dir: Path,
    downloaded_archives: List[str]
) -> Dict:
    """Generate attachments manifest JSON."""
    manifest = {
        "article_id": article_id,
        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
        "download_summary": {
            "total_files": 0,
            "total_size_bytes": 0,
            "categories": {}
        },
        "downloaded_archives": downloaded_archives,
        "files": []
    }

    # Count files by category
    for category_dir in attachments_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name == "archives":
            continue

        files = list(category_dir.glob('*'))
        if files:
            manifest["download_summary"]["categories"][category_dir.name] = len(files)
            manifest["download_summary"]["total_files"] += len(files)

            for file_path in files:
                size = file_path.stat().st_size
                manifest["download_summary"]["total_size_bytes"] += size

                manifest["files"].append({
                    "filename": file_path.name,
                    "size_bytes": size,
                    "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
                    "category": category_dir.name,
                    "local_path": f"attachments/{category_dir.name}/{file_path.name}",
                    "checksum_sha256": calculate_sha256(file_path)
                })

    return manifest


def generate_readme(manifest: Dict) -> str:
    """Generate README for attachments."""
    readme = f"""# Article {manifest['article_id']} - Attachments

**Extraction Date:** {manifest['extraction_timestamp']}

## 📊 Summary

- **Total Files:** {manifest['download_summary']['total_files']}
- **Total Size:** {manifest['download_summary']['total_size_bytes'] / 1024:.1f} KB

## 📁 File Categories

"""

    for category, count in manifest['download_summary']['categories'].items():
        readme += f"### {category.capitalize()} ({count} files)\n\n"

        category_files = [f for f in manifest['files'] if f['category'] == category]
        for file_info in sorted(category_files, key=lambda x: x['filename']):
            readme += f"- `{file_info['filename']}` ({file_info['size_bytes'] / 1024:.1f} KB)\n"

        readme += "\n"

    return readme


def test_attachment_extraction():
    """Test attachment extraction with Article 14760."""
    print("=" * 60)
    print("🧪 ATTACHMENT EXTRACTION TEST (Simplified)")
    print("=" * 60)

    # Test data for Article 14760
    article_id = "14760"
    article_dir = Path("/tmp/test_attachment_extraction") / f"article_{article_id}"
    attachments_dir = article_dir / "attachments"
    archives_dir = attachments_dir / "archives"

    # Manually identified attachment URLs from Article 14760
    attachment_urls = [
        "https://www.mql5.com/en/articles/download/14760.zip",
        "https://www.mql5.com/en/articles/download/14760/code_6_files.zip"
    ]

    # Create directory structure
    article_dir.mkdir(parents=True, exist_ok=True)
    archives_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📂 Output directory: {article_dir}")
    print(f"📥 Test URLs: {len(attachment_urls)} attachments")

    # Step 1: Download attachments
    print(f"\n" + "=" * 60)
    print("STEP 1: DOWNLOADING ATTACHMENTS")
    print("=" * 60)
    downloaded_archives = []

    for url in attachment_urls:
        filename = os.path.basename(url)
        archive_path = archives_dir / filename

        print(f"\n🔽 Downloading: {url}")
        if download_file(url, archive_path):
            downloaded_archives.append(str(archive_path))

    # Step 2: Extract ZIPs
    print(f"\n" + "=" * 60)
    print(f"STEP 2: EXTRACTING {len(downloaded_archives)} ARCHIVES")
    print("=" * 60)
    all_extracted_files = []

    for archive_path in downloaded_archives:
        archive_path = Path(archive_path)
        print(f"\n📦 Extracting: {archive_path.name}")
        if archive_path.suffix.lower() == '.zip':
            extracted = extract_zip_safely(archive_path, attachments_dir)
            all_extracted_files.extend(extracted)

    # Step 3: Deduplicate
    print(f"\n" + "=" * 60)
    print("STEP 3: DEDUPLICATING FILES")
    print("=" * 60)
    duplicates = deduplicate_files(attachments_dir)
    print(f"\n✅ Removed {duplicates} duplicates")

    # Step 4: Generate manifest
    print(f"\n" + "=" * 60)
    print("STEP 4: GENERATING MANIFEST")
    print("=" * 60)
    manifest = generate_manifest(article_id, attachments_dir, attachment_urls)
    manifest_path = article_dir / "attachments_manifest.json"

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {manifest_path}")

    # Step 5: Generate README
    print(f"\n" + "=" * 60)
    print("STEP 5: GENERATING README")
    print("=" * 60)
    readme = generate_readme(manifest)
    readme_path = article_dir / "attachments_README.md"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f"✅ Saved: {readme_path}")

    # Step 6: Verify directory structure
    print(f"\n" + "=" * 60)
    print("STEP 6: VERIFY DIRECTORY STRUCTURE")
    print("=" * 60)
    print(f"\n📁 Final structure:")
    print(f"  {article_dir.name}/")
    print(f"  ├── attachments/")
    for category in manifest['download_summary']['categories'].keys():
        files_count = manifest['download_summary']['categories'][category]
        print(f"  │   ├── {category}/ ({files_count} files)")
    print(f"  │   └── archives/ ({len(downloaded_archives)} archives)")
    print(f"  ├── attachments_manifest.json")
    print(f"  └── attachments_README.md")

    # Final summary
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print(f"\n📊 Results:")
    print(f"  - Downloaded archives: {len(downloaded_archives)}")
    print(f"  - Extracted files: {len(all_extracted_files) - duplicates}")
    print(f"  - Removed duplicates: {duplicates}")
    print(f"  - Unique files: {manifest['download_summary']['total_files']}")
    print(f"  - Total size: {manifest['download_summary']['total_size_bytes'] / 1024:.1f} KB")
    print(f"\n📁 Output: {article_dir}")

    # Verification checks
    print(f"\n" + "=" * 60)
    print("VERIFICATION CHECKS")
    print("=" * 60)
    checks = {
        "Archives downloaded": len(downloaded_archives) > 0,
        "Files extracted": manifest['download_summary']['total_files'] > 0,
        "Manifest created": manifest_path.exists(),
        "README created": readme_path.exists(),
        "No binaries extracted": all(f['file_type'] not in ['ex5', 'ex4', 'dll', 'exe'] for f in manifest['files']),
        "Files categorized": len(manifest['download_summary']['categories']) > 0
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    all_passed = all(checks.values())
    if all_passed:
        print(f"\n🎉 All verification checks passed!")
    else:
        print(f"\n⚠️  Some checks failed!")

    return all_passed


if __name__ == "__main__":
    test_attachment_extraction()
