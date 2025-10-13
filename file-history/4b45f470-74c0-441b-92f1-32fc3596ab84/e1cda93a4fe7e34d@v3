#!/usr/bin/env python3
"""
Minimal test script for attachment extraction design validation.
Tests with Article 14760 (Autoencoder) which has diverse attachment types.
"""

import asyncio
import hashlib
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


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


async def extract_attachment_links(article_url: str) -> List[Dict]:
    """Extract attachment download links from article page."""
    print(f"\n🔍 Extracting attachment links from: {article_url}")

    attachment_links = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(article_url, timeout=30000)
            await page.wait_for_selector("div.content", timeout=10000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Pattern 1: Find download section at bottom of article
            download_section = soup.find('div', class_='content')
            if download_section:
                # Look for download links
                for link in download_section.find_all('a', href=True):
                    href = link['href']
                    if '/articles/download/' in href:
                        full_url = f"https://www.mql5.com{href}" if href.startswith('/') else href
                        filename = os.path.basename(href)

                        attachment_links.append({
                            "url": full_url,
                            "filename": filename,
                            "link_text": link.get_text(strip=True)
                        })

            print(f"✅ Found {len(attachment_links)} attachment links")

        finally:
            await browser.close()

    return attachment_links


async def download_file(url: str, output_path: Path) -> bool:
    """Download a file with safety checks."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
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
                    print(f"⏭️  Skipping binary: {member}")
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
                print(f"🔄 Removing duplicate: {file_path.name}")
                file_path.unlink()
                duplicates_removed += 1
            else:
                checksums[checksum] = file_path

    return duplicates_removed


def generate_manifest(
    article_id: str,
    attachments_dir: Path,
    attachment_links: List[Dict]
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


def generate_readme(manifest: Dict, article_dir: Path) -> str:
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


async def test_attachment_extraction(article_url: str, output_dir: Path):
    """Test attachment extraction with a single article."""
    print("=" * 60)
    print("🧪 ATTACHMENT EXTRACTION TEST")
    print("=" * 60)

    # Extract article ID from URL
    article_id = article_url.split('/articles/')[-1].strip('/')
    article_dir = output_dir / f"article_{article_id}"
    attachments_dir = article_dir / "attachments"
    archives_dir = attachments_dir / "archives"

    # Create directory structure
    article_dir.mkdir(parents=True, exist_ok=True)
    archives_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📂 Output directory: {article_dir}")

    # Step 1: Extract attachment links
    attachment_links = await extract_attachment_links(article_url)

    if not attachment_links:
        print("⚠️  No attachments found")
        return

    # Step 2: Download attachments
    print(f"\n📥 Downloading {len(attachment_links)} attachments...")
    downloaded_archives = []

    for link_info in attachment_links:
        url = link_info['url']
        filename = link_info['filename']
        archive_path = archives_dir / filename

        if await download_file(url, archive_path):
            downloaded_archives.append(archive_path)

    # Step 3: Extract ZIPs
    print(f"\n📦 Extracting {len(downloaded_archives)} archives...")
    all_extracted_files = []

    for archive_path in downloaded_archives:
        if archive_path.suffix.lower() == '.zip':
            extracted = extract_zip_safely(archive_path, attachments_dir)
            all_extracted_files.extend(extracted)

    # Step 4: Deduplicate
    print(f"\n🔄 Deduplicating files...")
    duplicates = deduplicate_files(attachments_dir)
    print(f"✅ Removed {duplicates} duplicates")

    # Step 5: Generate manifest
    print(f"\n📋 Generating manifest...")
    manifest = generate_manifest(article_id, attachments_dir, attachment_links)
    manifest_path = article_dir / "attachments_manifest.json"

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved manifest: {manifest_path}")

    # Step 6: Generate README
    print(f"\n📄 Generating README...")
    readme = generate_readme(manifest, article_dir)
    readme_path = article_dir / "attachments_README.md"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f"✅ Saved README: {readme_path}")

    # Final summary
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print(f"\n📊 Results:")
    print(f"  - Downloaded archives: {len(downloaded_archives)}")
    print(f"  - Extracted files: {len(all_extracted_files)}")
    print(f"  - Unique files: {manifest['download_summary']['total_files']}")
    print(f"  - Total size: {manifest['download_summary']['total_size_bytes'] / 1024:.1f} KB")
    print(f"\n📁 File structure:")
    print(f"  {article_dir}/")
    print(f"  ├── attachments/")
    for category in manifest['download_summary']['categories'].keys():
        print(f"  │   ├── {category}/")
    print(f"  │   └── archives/")
    print(f"  ├── attachments_manifest.json")
    print(f"  └── attachments_README.md")


if __name__ == "__main__":
    # Test with Article 14760 (Autoencoder) - has diverse attachments
    test_url = "https://www.mql5.com/en/articles/14760"
    test_output = Path("/tmp/test_attachment_extraction")

    asyncio.run(test_attachment_extraction(test_url, test_output))
