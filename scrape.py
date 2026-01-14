"""
BoBot-Scrape: Botkyrka Kommun Intranet Document Scraper

Connects to a running Chrome browser via Chrome DevTools Protocol (CDP)
and downloads routine documents from Botkyrka kommun's intranet.

Prerequisites:
    1. Start Chrome with remote debugging:
       /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
    2. Log in to Botkyrka intranet in Chrome

Usage:
    .venv/bin/python scrape.py [OPTIONS]

Options:
    --scan-only     Only scan for documents and create CSV, skip downloading
    --download      Download documents (skips existing files) [default]
    --force         Re-download all files, even if they exist
    --help          Show this help message

Examples:
    # First run - download all documents
    .venv/bin/python scrape.py

    # Update CSV with latest URLs (no download)
    .venv/bin/python scrape.py --scan-only

    # Download only new/missing files
    .venv/bin/python scrape.py --download

    # Re-download everything
    .venv/bin/python scrape.py --force

Output:
    downloads/                    - Base folder for all downloads
    downloads/{category}/         - One folder per rutiner category (15 total)
    downloads/documents.csv       - List of all documents with URLs
"""

import argparse
import csv
import os
import re
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright


TARGET_URL = "https://botwebb.botkyrka.se/sidor/din-forvaltning/forvaltningar/vard--och-omsorgsforvaltningen/kvalitet/lagar-termer-och-styrdokument/styrdokument/rutiner-for-utforare.html"
CDP_ENDPOINT = "http://localhost:9222"
BASE_DOMAIN = "botwebb.botkyrka.se"

# Document file extensions to extract (case-insensitive)
DOCUMENT_EXTENSIONS = (".pdf", ".doc", ".docx")

# The 15 rutiner categories we want to extract
RUTINER_CATEGORIES = [
    "Bemanningsenheten",
    "Boendestöd",
    "Dagverksamhet",
    "Gruppbostad",
    "Hemtjänst",
    "Hälso- och sjukvård",
    "Korttidsboende för äldre (SoL)",
    "Korttidsvistelse för unga (LSS)",
    "Kost-och måltidsenheten",
    "Ledsagning, Avlösning och Kontaktperson",
    "Mötesplatser",
    "Personlig assistans",
    "Serviceboende (LSS)",
    "Servicehus (SoL)",
    "Vård- och omsorgsboende",
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape routine documents from Botkyrka kommun intranet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                  Download all documents (skip existing)
  %(prog)s --scan-only      Only scan and create CSV, no downloads
  %(prog)s --force          Re-download all files
        """
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan for documents and create CSV, skip downloading"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        default=True,
        help="Download documents, skipping existing files (default)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download all files, even if they already exist"
    )
    return parser.parse_args()


def main():
    """Connect to Chrome via CDP and scrape documents from intranet."""
    args = parse_args()

    # Determine mode
    skip_download = args.scan_only
    force_download = args.force

    if skip_download:
        print("Mode: SCAN ONLY (no downloads, just CSV)")
    elif force_download:
        print("Mode: FORCE DOWNLOAD (re-download all files)")
    else:
        print("Mode: DOWNLOAD (skip existing files)")
    print()

    try:
        with sync_playwright() as playwright:
            # Connect to running Chrome with remote debugging enabled
            print(f"Connecting to Chrome at {CDP_ENDPOINT}...")
            browser = playwright.chromium.connect_over_cdp(CDP_ENDPOINT)

            # Get the default browser context (user's existing session)
            context = browser.contexts[0]

            # Use existing page or create a new one
            if context.pages:
                page = context.pages[0]
                print("Using existing browser tab")
            else:
                page = context.new_page()
                print("Created new browser tab")

            # Navigate to the target URL
            print(f"Navigating to: {TARGET_URL}")
            page.goto(TARGET_URL)

            # Wait for page to fully load
            page.wait_for_load_state("networkidle")

            # Print page title as confirmation
            title = page.title()
            print(f"Page title: {title}")
            print("Successfully connected and navigated!")
            print()

            # Extract all links from the page
            print("Extracting rutiner category links...")
            all_links = page.query_selector_all("a")

            # Filter for the 15 rutiner category links
            category_links = []

            for link in all_links:
                href = link.get_attribute("href")
                text = link.text_content()

                # Skip empty links
                if not href:
                    continue

                # Clean up text (remove extra whitespace)
                text = " ".join(text.split()) if text else ""

                # Check if this link text matches one of our target categories
                if text in RUTINER_CATEGORIES:
                    # Normalize relative URLs to absolute
                    if href.startswith("/"):
                        href = f"https://{BASE_DOMAIN}{href}"
                    category_links.append({"url": href, "text": text})

            # Print extracted category links
            print(f"\n{'='*60}")
            print(f"Found {len(category_links)} of {len(RUTINER_CATEGORIES)} rutiner categories:")
            print(f"{'='*60}\n")

            for i, link in enumerate(category_links, 1):
                print(f"{i:3}. {link['text']:<45} -> {link['url']}")

            # Check for missing categories
            found_texts = {link["text"] for link in category_links}
            missing = [cat for cat in RUTINER_CATEGORIES if cat not in found_texts]

            if missing:
                print(f"\n⚠️  Missing categories ({len(missing)}):")
                for cat in missing:
                    print(f"    - {cat}")

            print(f"\n{'='*60}")
            print(f"Total: {len(category_links)}/{len(RUTINER_CATEGORIES)} categories found")
            print(f"{'='*60}")

            # Phase 3: Visit each category and extract document links with subcategory headings
            print("\n" + "="*60)
            print("Extracting document links from categories...")
            print("="*60 + "\n")

            # Store documents by category: {category_name: [{"url": url, "type": "pdf"|"doc"|"docx", "subcategory": str}]}
            documents_by_category = {}
            failed_categories = []
            total_pdfs = 0
            total_word = 0

            for i, cat in enumerate(category_links, 1):
                category_name = cat["text"]
                category_url = cat["url"]
                print(f"Processing category {i}/{len(category_links)}: {category_name}")

                try:
                    # Navigate to category page
                    page.goto(category_url)
                    page.wait_for_load_state("networkidle")

                    # Extract document links with their subcategory headings using JavaScript
                    # Documents are inside collapsible sections with class "sol-collapsible"
                    # The section title is in "sol-collapsible-header-text" div
                    doc_links = page.evaluate("""() => {
                        const EXTENSIONS = ['.pdf', '.doc', '.docx'];
                        const results = [];

                        // Blocklist of headings to ignore (notification banners, etc.)
                        const HEADING_BLOCKLIST = [
                            'pågående strömavbrott',
                            'driftstörning',
                            'meddelande',
                            'notis'
                        ];

                        function isBlocklistedHeading(text) {
                            const lower = text.toLowerCase().trim();
                            return HEADING_BLOCKLIST.some(blocked => lower.includes(blocked));
                        }

                        // Get all links on the page
                        const links = document.querySelectorAll('a');

                        for (const link of links) {
                            const href = link.getAttribute('href');
                            if (!href) continue;

                            // Check if it's a document link
                            const hrefLower = href.toLowerCase();
                            let docType = null;
                            for (const ext of EXTENSIONS) {
                                if (hrefLower.endsWith(ext)) {
                                    docType = ext.substring(1);
                                    break;
                                }
                            }
                            if (!docType) continue;

                            // Find the collapsible section this link belongs to
                            // Look for parent with class "sol-collapsible" or similar
                            let subcategory = '';
                            let element = link;

                            // Walk up DOM to find collapsible container
                            while (element) {
                                // Check if this element or its parent is a collapsible section
                                if (element.classList && (
                                    element.classList.contains('sol-collapsible') ||
                                    element.classList.contains('sol-collapsible-content')
                                )) {
                                    // Found collapsible content, look for header in parent or sibling
                                    let collapsible = element;
                                    if (element.classList.contains('sol-collapsible-content')) {
                                        collapsible = element.closest('.sol-collapsible') || element.parentElement;
                                    }

                                    // Find the header text div
                                    const headerDiv = collapsible.querySelector('.sol-collapsible-header-text');
                                    if (headerDiv) {
                                        const headerText = headerDiv.textContent.trim();
                                        if (!isBlocklistedHeading(headerText)) {
                                            subcategory = headerText;
                                            break;
                                        }
                                    }
                                }

                                // Also check for traditional headings (h2, h3, h4) as fallback
                                let sibling = element.previousElementSibling;
                                while (sibling) {
                                    const tagName = sibling.tagName.toLowerCase();
                                    if (['h2', 'h3', 'h4'].includes(tagName)) {
                                        const headingText = sibling.textContent.trim();
                                        if (!isBlocklistedHeading(headingText)) {
                                            subcategory = headingText;
                                            break;
                                        }
                                    }
                                    // Check for collapsible header in sibling
                                    const collapsibleHeader = sibling.querySelector('.sol-collapsible-header-text');
                                    if (collapsibleHeader) {
                                        const headerText = collapsibleHeader.textContent.trim();
                                        if (!isBlocklistedHeading(headerText)) {
                                            subcategory = headerText;
                                            break;
                                        }
                                    }
                                    sibling = sibling.previousElementSibling;
                                }
                                if (subcategory) break;

                                // Move up to parent
                                element = element.parentElement;
                            }

                            results.push({
                                url: href,
                                type: docType,
                                subcategory: subcategory || ''
                            });
                        }

                        return results;
                    }""")

                    # Normalize relative URLs to absolute
                    for doc in doc_links:
                        if doc["url"].startswith("/"):
                            doc["url"] = f"https://{BASE_DOMAIN}{doc['url']}"

                    # Store results and update counts
                    documents_by_category[category_name] = doc_links
                    pdf_count = sum(1 for d in doc_links if d["type"] == "pdf")
                    word_count = sum(1 for d in doc_links if d["type"] in ("doc", "docx"))
                    total_pdfs += pdf_count
                    total_word += word_count

                    # Count unique subcategories found
                    subcats = set(d["subcategory"] for d in doc_links if d["subcategory"])
                    subcat_info = f", {len(subcats)} subcategories" if subcats else ""
                    print(f"  Found {len(doc_links)} documents ({pdf_count} PDFs, {word_count} Word files{subcat_info})")

                except Exception as e:
                    print(f"  ERROR: Failed to process - {e}")
                    failed_categories.append({"name": category_name, "error": str(e)})
                    documents_by_category[category_name] = []

            # Print final summary
            print("\n" + "="*60)
            print("Document Extraction Summary")
            print("="*60)
            total_docs = total_pdfs + total_word
            print(f"\nTotal: {total_docs} documents across {len(category_links)} categories")
            print(f"  - PDFs: {total_pdfs}")
            print(f"  - Word files: {total_word}")

            if failed_categories:
                print(f"\n⚠️  Failed categories ({len(failed_categories)}):")
                for fail in failed_categories:
                    print(f"    - {fail['name']}: {fail['error']}")

            print("="*60)

            # Create base downloads directory
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            # Phase 4: Download documents (unless --scan-only)
            if not skip_download:
                print("\n" + "="*60)
                print("Downloading documents to category folders...")
                print("="*60 + "\n")

                downloaded_count = 0
                skipped_count = 0
                failed_downloads = []

                for category_name, docs in documents_by_category.items():
                    if not docs:
                        continue

                    # Sanitize folder name (replace invalid chars with -)
                    safe_name = re.sub(r'[<>:"/\\|?*]', '-', category_name)
                    category_dir = os.path.join(downloads_dir, safe_name)
                    os.makedirs(category_dir, exist_ok=True)

                    print(f"Downloading {len(docs)} documents to {safe_name}/")

                    for doc in docs:
                        url = doc["url"]
                        # Extract filename from URL (last path segment)
                        filename = url.split("/")[-1]
                        filename = filename.split("?")[0]  # Remove query params
                        filepath = os.path.join(category_dir, filename)

                        # Skip if file already exists (unless --force)
                        if os.path.exists(filepath) and not force_download:
                            skipped_count += 1
                            print(f"  Skipped (exists): {unquote(filename)}")
                            continue

                        try:
                            # Download using Playwright's built-in HTTP client (shares session)
                            response = page.context.request.get(url)
                            if response.ok:
                                with open(filepath, "wb") as f:
                                    f.write(response.body())
                                downloaded_count += 1
                                print(f"  Downloaded: {unquote(filename)}")
                            else:
                                failed_downloads.append({"url": url, "category": category_name, "error": f"HTTP {response.status}"})
                                print(f"  FAILED: {unquote(filename)} (HTTP {response.status})")
                        except Exception as e:
                            failed_downloads.append({"url": url, "category": category_name, "error": str(e)})
                            print(f"  FAILED: {unquote(filename)} ({e})")

                # Print download summary
                print("\n" + "="*60)
                print("Download Summary")
                print("="*60)
                print(f"\nNewly downloaded: {downloaded_count} documents")
                print(f"Skipped (existing): {skipped_count} documents")
                print(f"Failed: {len(failed_downloads)} documents")

                if failed_downloads:
                    print(f"\n⚠️  Failed downloads ({len(failed_downloads)}):")
                    for fail in failed_downloads[:10]:  # Show first 10 failures
                        print(f"    - {fail['category']}: {fail['error']}")
                    if len(failed_downloads) > 10:
                        print(f"    ... and {len(failed_downloads) - 10} more")

                print("="*60)
            else:
                print("\n(Skipping downloads - scan-only mode)")

            # Export document list to CSV (always)
            # Schema: category (category name), subcategory (heading), filename, filename_decoded, type, url
            csv_path = os.path.join(downloads_dir, "documents.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["category", "subcategory", "filename", "filename_decoded", "type", "url"])
                for category_name, docs in documents_by_category.items():
                    # Use sanitized category name as category for folder consistency
                    safe_name = re.sub(r'[<>:"/\\|?*]', '-', category_name)
                    for doc in docs:
                        filename = doc["url"].split("/")[-1].split("?")[0]
                        filename_decoded = unquote(filename)
                        subcategory = doc.get("subcategory", "")
                        writer.writerow([safe_name, subcategory, filename, filename_decoded, doc["type"], doc["url"]])

            print(f"\nExported document list to: {csv_path}")
            print(f"  - {total_docs} documents with URLs")

            # Don't close browser - we're reusing user's session

    except Exception as e:
        error_msg = str(e)
        if "connect" in error_msg.lower() or "ECONNREFUSED" in error_msg:
            print("Error: Chrome not running with --remote-debugging-port=9222")
            print()
            print("Start Chrome with remote debugging:")
            print("  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug")
        else:
            print(f"Error: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
