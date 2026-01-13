"""
BoBot-Scrape: CDP Connection Script

Connects to a running Chrome browser via Chrome DevTools Protocol (CDP)
and navigates to the Botkyrka kommun intranet page.

Usage:
    1. Start Chrome with remote debugging:
       /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
    2. Log in to Botkyrka intranet in Chrome if not already
    3. Run: .venv/bin/python scrape.py
"""

import sys
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


def main():
    """Connect to Chrome via CDP and navigate to the target intranet page."""
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

            # Phase 3: Visit each category and extract document links
            print("\n" + "="*60)
            print("Phase 3: Extracting document links from categories...")
            print("="*60 + "\n")

            # Store documents by category: {category_name: [{"url": url, "type": "pdf"|"doc"|"docx"}]}
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

                    # Extract all links from category page
                    cat_links = page.query_selector_all("a")
                    doc_links = []

                    for link in cat_links:
                        href = link.get_attribute("href")
                        if not href:
                            continue

                        # Check for document extensions (case-insensitive)
                        href_lower = href.lower()
                        doc_type = None
                        for ext in DOCUMENT_EXTENSIONS:
                            if href_lower.endswith(ext):
                                doc_type = ext[1:]  # Remove the dot
                                break

                        if doc_type:
                            # Normalize relative URLs to absolute
                            if href.startswith("/"):
                                href = f"https://{BASE_DOMAIN}{href}"
                            doc_links.append({"url": href, "type": doc_type})

                    # Store results and update counts
                    documents_by_category[category_name] = doc_links
                    pdf_count = sum(1 for d in doc_links if d["type"] == "pdf")
                    word_count = sum(1 for d in doc_links if d["type"] in ("doc", "docx"))
                    total_pdfs += pdf_count
                    total_word += word_count

                    print(f"  Found {len(doc_links)} documents ({pdf_count} PDFs, {word_count} Word files)")

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
