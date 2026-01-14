---
name: digi:push-kb
description: Sync KB content to GitHub repo (converted, indexes, prompts)
allowed-tools:
  - Bash
  - Read
---

<objective>
Sync all knowledge base content to the bobot-kb GitHub repository.

Syncs three folders:
- converted/ - Markdown documents organized by verksamhet
- indexes/ - INDEX files for each verksamhet
- prompts/ - GENERAL.md, *-PROMPT.md, and combined/ directory

Output: Files synced count, commit hash, success message
</objective>

<process>
1. Clone or update bobot-kb repo in temp directory
2. Rsync all three folders with --delete for clean sync
3. Commit changes with timestamp
4. Push to GitHub
5. Report results
</process>

<instructions>
Execute the following sync workflow:

## Step 1: Setup temp directory and clone/update repo

```bash
# Create temp dir if needed
TEMP_DIR="/tmp/bobot-kb-sync"
REPO_URL="https://github.com/fabian-von-tiedemann/bobot-kb.git"

if [ -d "$TEMP_DIR/.git" ]; then
  echo "Updating existing clone..."
  cd "$TEMP_DIR" && git fetch origin && git reset --hard origin/main
else
  echo "Cloning repository..."
  rm -rf "$TEMP_DIR"
  gh repo clone fabian-von-tiedemann/bobot-kb "$TEMP_DIR"
fi
```

## Step 2: Rsync all three folders

```bash
SOURCE_DIR="${PWD}"  # Should be BoBot-Scrape root

# Sync converted/ (--delete removes files not in source)
echo "Syncing converted/..."
rsync -av --delete --exclude='.DS_Store' "${SOURCE_DIR}/converted/" "$TEMP_DIR/converted/"

# Sync indexes/
echo "Syncing indexes/..."
rsync -av --delete --exclude='.DS_Store' "${SOURCE_DIR}/indexes/" "$TEMP_DIR/indexes/"

# Sync prompts/
echo "Syncing prompts/..."
rsync -av --delete --exclude='.DS_Store' "${SOURCE_DIR}/prompts/" "$TEMP_DIR/prompts/"
```

## Step 3: Count synced files

```bash
cd "$TEMP_DIR"
CONVERTED_COUNT=$(find converted -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
INDEXES_COUNT=$(find indexes -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
PROMPTS_COUNT=$(find prompts -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "Files synced:"
echo "  converted/: ${CONVERTED_COUNT} files"
echo "  indexes/:   ${INDEXES_COUNT} files"
echo "  prompts/:   ${PROMPTS_COUNT} files"
echo "  Total:      $((CONVERTED_COUNT + INDEXES_COUNT + PROMPTS_COUNT)) files"
```

## Step 4: Commit and push

```bash
cd "$TEMP_DIR"

# Stage all changes
git add -A

# Check if there are changes to commit
if git diff --staged --quiet; then
  echo ""
  echo "No changes to commit - KB is already in sync"
else
  # Commit with timestamp
  TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
  git commit -m "sync: KB update ${TIMESTAMP}"

  # Push to GitHub (may need http.postBuffer for large pushes)
  git config http.postBuffer 524288000
  git push origin main

  # Get commit hash
  COMMIT_HASH=$(git rev-parse --short HEAD)

  echo ""
  echo "Success! KB synced to GitHub"
  echo "Commit: ${COMMIT_HASH}"
  echo "Repo:   https://github.com/fabian-von-tiedemann/bobot-kb"
fi
```

## Error handling

If push fails with HTTP 400/RPC error:
- Increase http.postBuffer: `git config http.postBuffer 524288000`
- Retry push

If authentication fails:
- Run `gh auth login` to authenticate
- Ensure gh CLI has repo access
</instructions>
