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
            print("Extracting links from page...")
            all_links = page.query_selector_all("a")

            # Filter and extract link information
            category_links = []
            base_domain = "botwebb.botkyrka.se"

            for link in all_links:
                href = link.get_attribute("href")
                text = link.text_content()

                # Skip empty links
                if not href:
                    continue

                # Clean up text (remove extra whitespace)
                text = " ".join(text.split()) if text else ""

                # Filter for internal links (same domain or relative paths)
                # Skip direct PDF links, anchors, and external links
                is_internal = (
                    href.startswith("/")
                    or href.startswith("https://botwebb.botkyrka.se")
                    or href.startswith("http://botwebb.botkyrka.se")
                )
                is_anchor = href.startswith("#")
                is_pdf = href.lower().endswith(".pdf")
                is_javascript = href.startswith("javascript:")

                if is_internal and not is_anchor and not is_pdf and not is_javascript:
                    # Normalize relative URLs to absolute
                    if href.startswith("/"):
                        href = f"https://{base_domain}{href}"
                    category_links.append({"url": href, "text": text})

            # Print extracted links
            print(f"\n{'='*60}")
            print(f"Found {len(category_links)} category/internal links:")
            print(f"{'='*60}\n")

            for i, link in enumerate(category_links, 1):
                print(f"{i:3}. {link['text'][:50]:<50} -> {link['url']}")

            print(f"\n{'='*60}")
            print(f"Total links: {len(category_links)}")
            print(f"{'='*60}")

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
