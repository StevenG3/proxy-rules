# NOL Ticket Direct Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish an importable Shadowrocket module that sends the two confirmed NOL ticketing and payment domains directly.

**Architecture:** Store one self-contained `.sgmodule` beside the existing Shadowrocket rule list. The module owns its fixed `DIRECT` policy, while the README exposes its stable raw GitHub URL and import purpose.

**Tech Stack:** Shadowrocket module syntax, Markdown, Git, GitHub raw content

---

### Task 1: Add the NOL Direct Module

**Files:**
- Create: `shadowrocket/nol-ticket-direct.sgmodule`
- Reference: `docs/superpowers/specs/2026-07-29-nol-ticket-direct-module-design.md`

- [ ] **Step 1: Run the missing-module check to establish the failing baseline**

Run:

```bash
test -f shadowrocket/nol-ticket-direct.sgmodule
```

Expected: FAIL with exit status `1` because the module does not exist.

- [ ] **Step 2: Create the minimal module**

Create `shadowrocket/nol-ticket-direct.sgmodule` with exactly:

```ini
#!name=NOL Ticket Direct
#!desc=Direct routing for NOL ticketing and payment domains

[Rule]
DOMAIN,secureapi.ext.eximbay.com,DIRECT
DOMAIN,gpoticket.globalinterpark.com,DIRECT
```

- [ ] **Step 3: Verify the module structure and exact rules**

Run:

```bash
test "$(rg -c '^#!name=' shadowrocket/nol-ticket-direct.sgmodule)" -eq 1
test "$(rg -c '^\[Rule\]$' shadowrocket/nol-ticket-direct.sgmodule)" -eq 1
test "$(rg -c '^DOMAIN,[^,]+,DIRECT$' shadowrocket/nol-ticket-direct.sgmodule)" -eq 2
test "$(rg -c '^DOMAIN,secureapi\.ext\.eximbay\.com,DIRECT$' shadowrocket/nol-ticket-direct.sgmodule)" -eq 1
test "$(rg -c '^DOMAIN,gpoticket\.globalinterpark\.com,DIRECT$' shadowrocket/nol-ticket-direct.sgmodule)" -eq 1
! rg -q '^DOMAIN-SUFFIX,' shadowrocket/nol-ticket-direct.sgmodule
git diff --check
```

Expected: every command exits with status `0` and produces no error output.

- [ ] **Step 4: Commit the module**

```bash
git add shadowrocket/nol-ticket-direct.sgmodule
git commit -m "feat: add NOL ticket direct module"
```

Expected: one commit creating `shadowrocket/nol-ticket-direct.sgmodule`.

### Task 2: Document the Remote Module

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run the missing-documentation check**

Run:

```bash
rg -F 'https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/nol-ticket-direct.sgmodule' README.md
```

Expected: FAIL with exit status `1` because the module URL is not documented.

- [ ] **Step 2: Add the README section**

Append:

````markdown
### NOL Ticket Direct

Shadowrocket module URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/nol-ticket-direct.sgmodule
```

Import this URL from Shadowrocket's Modules screen. The module routes the
confirmed NOL ticketing and payment domains through `DIRECT`.
````

- [ ] **Step 3: Verify documentation and formatting**

Run:

```bash
test "$(rg -c -F 'https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/nol-ticket-direct.sgmodule' README.md)" -eq 1
git diff --check
```

Expected: both commands exit with status `0`.

- [ ] **Step 4: Commit the documentation and plan**

```bash
git add README.md docs/superpowers/plans/2026-07-29-nol-ticket-direct-module.md
git commit -m "docs: add NOL module import instructions"
```

Expected: one commit updating the README and recording this implementation plan.

### Task 3: Publish and Verify the Raw Module

**Files:**
- Verify: `shadowrocket/nol-ticket-direct.sgmodule`
- Verify: `README.md`

- [ ] **Step 1: Verify local history and content before publishing**

Run:

```bash
git status --short --branch
git log -4 --oneline
git diff origin/main...HEAD --check
```

Expected: no uncommitted files; local `main` is ahead of `origin/main`; diff check exits with status `0`.

- [ ] **Step 2: Push the commits**

Run:

```bash
git push origin main
```

Expected: push succeeds and updates `origin/main`.

- [ ] **Step 3: Compare the remote raw module with the committed local file**

Run:

```bash
curl -fsSL 'https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/nol-ticket-direct.sgmodule' | diff -u shadowrocket/nol-ticket-direct.sgmodule -
```

Expected: exit status `0` with no diff output.

- [ ] **Step 4: Confirm final repository synchronization**

Run:

```bash
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
git status --short --branch
```

Expected: SHA comparison exits with status `0` and status reports `## main...origin/main` with no file entries.
