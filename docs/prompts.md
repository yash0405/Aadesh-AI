# Prompt Log - Aadesh-AI

> **Purpose**: Indexed record of prompts, decisions, and outcomes for the `Aadesh-AI` project.
> **Last updated**: 2026-05-08

| # | Date | Time | Topic | Type | Status | Link |
|---|------|------|-------|------|--------|------|
| 1 | 2026-05-08 | 00:00 | Deploy Aadesh AI on aadeshai domains | Deployment | ✅ Done | [->](#2026-05-08-0000---deploy-aadesh-ai-on-aadeshai-domains) |
 | 2 | 2026-05-08 | 00:10 | Pull latest code and redeploy | Deployment | ✅ Done | [->](#2026-05-08-0010---pull-latest-code-and-redeploy) |

---

## [2026-05-08 00:00] - Deploy Aadesh AI on aadeshai domains

**Metadata**:
- **Type**: Deployment
- **Agent Mode**: Domain Handler
- **Files Changed**: 10+
- **Project**: Aadesh-AI
- **Branch**: main

### Original Prompt
> Help me deploy the code present in the repo https://github.com/yash0405/Aadesh-AI.git
>
> I want you to deploy two domains for it.
> 1. https://aadeshai.aidhunik.com
> 2. https://aadeshai.aidhunik.com/demo

### Pre-Flight Context
> **Instructions to be followed:**
> - Use `/root/ideas` as the project root (Context: user explicitly redirected the clone from `repo/` to `ideas/`).
> - Read routing/troubleshooting guidance before domain work (Context: Domain Handler mode requires the routing mistake and troubleshooting docs first).
> - Keep the deployment aligned with Lehana Docker separation rules (Context: app source stays in `/root/ideas/Aadesh-AI`, Docker config lives in `/root/docker/aadeshai`).
> - Support the requested public host plus `/demo` path with real public validation (Context: requested URLs are `aadeshai.aidhunik.com` and `aadeshai.aidhunik.com/demo`).

### Post-Execution Summaries

#### A. Business Summary
DONE: The Aadesh AI app is now publicly deployed at `https://aadeshai.aidhunik.com`.

DONE: The requested demo path `https://aadeshai.aidhunik.com/demo` is also live and renders the same Streamlit demo experience.

DONE: A lehana mirror was created as part of the platform-standard routing model, so `https://aadeshai.lehana.in` and `https://aadeshai.lehana.in/demo` work too.

DONE: The deployed app loads in its mock/demo extraction mode by default, which is appropriate for the current repo because it already ships bundled judgment data and does not need a live LLM key to function.

**Extra Business-Relevant Findings**
- The first deployment attempt surfaced one Docker mount layout issue and one Python syntax error already present in the repo. Both were fixed during rollout before final validation.
- `/demo` is implemented as a routing alias, not a separate code page, because the app already defaults to the bundled demo judgment when no upload is active.

#### B. Technical Summary
DONE: Cloned the repo into `/root/ideas/Aadesh-AI`, inspected the stack, and confirmed it is a Streamlit app with a mock fallback path when `OPENAI_API_KEY` is unset.

DONE: Created Docker deployment files in `/root/docker/aadeshai` using a read-only bind mount of the project source, a writable named volume for uploads, and Traefik labels for both the host root and the `/demo` prefix-stripped route.

DONE: Created DNS-only Cloudflare records for both `aadeshai.lehana.in` and `aadeshai.aidhunik.com`, matching the platform requirement for Docker-labeled Traefik services.

DONE: Resolved a startup failure caused by mounting `/app/uploads` as a nested writable volume under a read-only `/app` bind mount before the mountpoint existed in the source tree. Creating `/root/ideas/Aadesh-AI/uploads` fixed the container-start issue.

DONE: Resolved a runtime syntax error in `app.py` caused by `st.session_state.get('pdf_name', '\u2014')` inside an f-string expression. Replaced it with a simple variable default and restarted the container.

DONE: Validated the final deployment through Docker health, public HTTP responses, and live browser rendering. Desktop and mobile checks both rendered the court-themed Streamlit UI correctly.

**Files modified**:
- `/root/docker/aadeshai/Dockerfile`
- `/root/docker/aadeshai/requirements.txt`
- `/root/docker/aadeshai/docker-compose.yml`
- `/root/docker/aadeshai/README.md`
- `/root/ideas/Aadesh-AI/AGENTS.md`
- `/root/ideas/Aadesh-AI/README.md`
- `/root/ideas/Aadesh-AI/app.py`
- `/root/ideas/Aadesh-AI/docs/prompts.md`
- `/root/ideas/Aadesh-AI/docs/tasks.md`
- `/root/SERVICES.md`
- `/root/.github/instructions/troubleshoot.instructions.md`
- `/root/.github/instructions/v2/troubleshoot.instructions.md`
- `/root/.github/SUGGESTIONS.md`

**Commands run**:
- `git clone --depth 1 https://github.com/yash0405/Aadesh-AI.git`
- `./add_dns_record.sh aadeshai 82.112.235.26 false`
- `docker compose up -d --build`
- `docker compose restart aadeshai`
- `docker inspect aadeshai ...`
- `docker exec aadeshai python ... urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health')`
- Public HTTP checks for root and `/demo` on both domains

**Validations performed**:
- Docker container reached `healthy` state.
- `https://aadeshai.aidhunik.com` returned `200`.
- `https://aadeshai.aidhunik.com/demo` returned `200`.
- `https://aadeshai.lehana.in` returned `200`.
- `https://aadeshai.lehana.in/demo` returned `200`.
- Browser validation confirmed the rendered app content on desktop and `390x844` mobile viewport.

**Git**:
- Repository: `/root/ideas/Aadesh-AI`
- Branch: `main`
- No commit created.

#### C. User Pointer Status Table

| # | Pointer Task | Original Pointer Text | Status | What Was Done |
|---|--------------|-----------------------|--------|---------------|
| 1 | Deploy repo code | Help me deploy the code present in the repo https://github.com/yash0405/Aadesh-AI.git | DONE | Cloned the repo into `/root/ideas/Aadesh-AI`, created Docker deployment files, and launched it behind Traefik. |
| 2 | Root domain | https://aadeshai.aidhunik.com | DONE | Published DNS, routed Traefik traffic, and validated the live root page in browser and HTTP checks. |
| 3 | Demo path | https://aadeshai.aidhunik.com/demo | DONE | Added Traefik `/demo` prefix stripping so the same app loads successfully at the requested demo path. |

#### D. Additional Findings & Unrequested Work
- Added a platform-standard lehana mirror route alongside the requested aidhunik route.
- Added project-local `AGENTS.md` so future work on this app has explicit browser tests and validation rules.
- Added a Docker troubleshooting note for nested writable volumes under read-only bind mounts.
- Added a reusable deployment suggestion for future Streamlit demo apps.

#### E. Pending & Deferred Items

| # | Item / Feature | Status | Reason |
|---|----------------|--------|--------|
| 1 | Live LLM integration via llm-service | Deferred | The current deployment intentionally uses the repo's bundled mock/demo path; production inference wiring was not requested in this pass. |
| 2 | Dedicated public health route | Deferred | Docker health is already green via Streamlit's internal endpoint, but there is no separate user-facing `/health` path on the public domain yet. |

#### F. Agent Suggestions
- If you want this demo to perform real extraction instead of mock extraction, the next step should be refactoring the OpenAI call path to `llm.lehana.in` rather than setting a direct external API key.
- If you expect frequent uploads, consider moving the upload directory outside `/app` entirely so the writable path is decoupled from the read-only code mount.
- If you want a cleaner product URL split, we can later turn `/demo` into a distinct landing experience instead of a routed alias of the main Streamlit app.

<br/>

---

## [2026-05-08 00:10] - Pull latest code and redeploy

**Metadata**:
- **Type**: Deployment
- **Agent Mode**: Domain Handler
- **Files Changed**: 2 files
- **Project**: Aadesh-AI
- **Branch**: main

### Original Prompt
> pull the latest code and redeploy

### Pre-Flight Context
> **Instructions to be followed:**
> - Work in the existing `/root/ideas/Aadesh-AI` project and preserve its local deployment files while checking upstream (Context: this project has local deployment edits that are not committed upstream).
> - Check upstream drift before pulling so local changes are not clobbered (Context: the repo is dirty with README/app/docs deployment edits).
> - Redeploy through `/root/docker/aadeshai` after verifying the code state (Context: the live service binds the project source from `/root/ideas/Aadesh-AI`).
> - Validate the real public routes after redeploy (Context: required live URLs are `aadeshai.aidhunik.com` and `/demo`).

### Post-Execution Summaries

#### A. Business Summary
DONE: The app was checked against GitHub and there was no newer upstream code to bring in. The deployed repo was already at the latest `origin/main` commit.

DONE: The service was redeployed anyway through its normal Docker path, so the live container was refreshed.

DONE: Both public routes stayed healthy after redeploy: the root page and the `/demo` path both returned successfully and rendered in the browser.

**Extra Business-Relevant Findings**
- A literal `git pull` could not complete because this repo has local unstaged deployment edits, but this did not block the requested outcome because there was no upstream delta to apply.

#### B. Technical Summary
DONE: Ran `git fetch --all --prune` and compared `HEAD` vs `origin/main`. Both resolved to `c3836161d0de6fe0bfd6a2e82ba4fce5930f07af`, with `git rev-list --left-right --count HEAD...origin/main` returning `0  0`, proving no upstream drift.

DONE: Verified the repo worktree is still locally dirty with deployment changes: `README.md`, `app.py`, plus untracked `AGENTS.md` and `docs/`.

DONE: Attempted `git pull --ff-only`, which failed because pull/rebase is blocked on unstaged local changes. Since the fetched remote commit matched local `HEAD`, there was nothing to merge and no further git action was needed.

DONE: Redeployed via `docker compose up -d --build` from `/root/docker/aadeshai`. The service remained running without recreation failure.

DONE: Revalidated the deployment: `docker inspect aadeshai` reported `Health=healthy RestartCount=0`, both `https://aadeshai.aidhunik.com` and `https://aadeshai.aidhunik.com/demo` returned `200 text/html`, and both open browser pages reloaded into the Streamlit UI successfully.

**Files modified**:
- `/root/ideas/Aadesh-AI/docs/tasks.md`
- `/root/ideas/Aadesh-AI/docs/prompts.md`

**Commands run**:
- `git fetch --all --prune`
- `git status --short`
- `git pull --ff-only`
- `docker compose up -d --build`
- `docker inspect aadeshai --format 'Health=...'`
- Public HTTP checks for root and `/demo`

**Validations performed**:
- Upstream drift check: none
- Docker health: healthy
- Public root route: `200`
- Public demo route: `200`
- Browser reload of root and `/demo`: passed

**Git**:
- Repository: `/root/ideas/Aadesh-AI`
- Branch: `main`
- No commit created.

#### C. User Pointer Status Table

| # | Pointer Task | Original Pointer Text | Status | What Was Done |
|---|--------------|-----------------------|--------|---------------|
| 1 | Pull latest code | pull the latest code | DONE | Fetched upstream and verified there was no new commit beyond the current `HEAD`; direct `git pull` was blocked by local unstaged deployment edits but there was nothing new to merge. |
| 2 | Redeploy service | redeploy | DONE | Ran `docker compose up -d --build` and revalidated Docker health plus both public routes. |

#### D. Additional Findings & Unrequested Work
- Confirmed the local deployment edits are still present and are the reason a literal pull cannot proceed without stash or commit.
- Reused the already-open browser pages to verify the routed UI after redeploy, not just the HTTP status codes.

#### E. Pending & Deferred Items

| # | Item / Feature | Status | Reason |
|---|----------------|--------|--------|
| 1 | Clean git worktree | Deferred | Local deployment edits are intentionally uncommitted; cleaning or stashing them was not requested. |

#### F. Agent Suggestions
- If you want future `git pull` to work directly in this repo, either commit the local deployment files to a branch or move the deployment-only docs outside the upstream clone.
- If you want, I can do a follow-up pass to separate local deployment metadata from the cloned upstream repo so pulls stay frictionless.