# Phase 1: Setup - Context

**Gathered:** 2026-01-13
**Status:** Ready for planning

<vision>
## How This Should Work

Run a script that connects to an already-running Chrome browser where I'm logged into Botkyrka kommun's intranet. The script attaches to my existing session — no need to handle authentication, just reuse what's already there.

Once connected, navigate directly to the intranet start page so everything is ready for the next phases. One command, and I'm at the starting point.

</vision>

<essential>
## What Must Be Nailed

- **Reliable connection** — It just works every time without manual fiddling. Start Chrome with the right flags, run the script, and it connects. No guesswork.

</essential>

<boundaries>
## What's Out of Scope

- Keep it minimal — this phase is about getting connected and navigated, nothing more
- Detailed error recovery can be simple (fail cleanly if Chrome isn't running)
- No page scraping or link extraction yet

</boundaries>

<specifics>
## Specific Ideas

- Connect to existing Chrome via CDP (Chrome DevTools Protocol)
- Use Playwright's connect_over_cdp capability
- Navigate to intranet start page as final step of setup

</specifics>

<notes>
## Additional Context

The reason for connecting to an existing browser is to bypass intranet authentication. User already has a logged-in session — just need to attach to it and use those credentials.

</notes>

---

*Phase: 01-setup*
*Context gathered: 2026-01-13*
