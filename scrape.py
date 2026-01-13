"""
BoBot-Scrape: CDP Connection Script

Connects to a running Chrome browser via Chrome DevTools Protocol (CDP)
and navigates to the Botkyrka kommun intranet page.

Usage:
    1. Start Chrome with remote debugging:
       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
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

            # Don't close browser - we're reusing user's session

    except Exception as e:
        error_msg = str(e)
        if "connect" in error_msg.lower() or "ECONNREFUSED" in error_msg:
            print("Error: Chrome not running with --remote-debugging-port=9222")
            print()
            print("Start Chrome with remote debugging:")
            print("  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
        else:
            print(f"Error: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
