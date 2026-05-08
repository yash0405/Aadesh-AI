# AGENTS.md

## Scope
Aadesh AI is a Streamlit-based court judgment action-planning demo that extracts structured case details from a PDF and presents a human-verifiable action plan dashboard.

## Architecture
- UI/runtime: Streamlit app in `app.py`
- Data model: Pydantic schemas in `models.py`
- Pipeline: PDF extraction and planning logic in `pipeline/`
- Assets/data: demo PDFs and JSON payloads in `data/` and `static/`
- Deployment: Docker config in `/root/docker/aadeshai`, app source mounted read-only from this project

## Critical Project Rules
- Root route and `/demo` must both stay functional on the public domain.
- The default no-upload experience must open in demo mode using the bundled judgment PDF.
- Upload flow must keep writing only into the mounted `uploads/` volume, not back into the read-only source tree.
- Do not introduce direct external LLM API calls for production wiring; platform-standard routing must use `llm.lehana.in` if live inference is added later.

## Browser Test Cases
1. Root Demo Load:
   - Open `https://aadeshai.aidhunik.com`.
   - Expect the Streamlit app shell to load with the court-themed interface and bundled demo judgment state.
2. Demo Path Load:
   - Open `https://aadeshai.aidhunik.com/demo`.
   - Expect the same app to render successfully instead of a 404, redirect loop, or broken asset load.
3. Demo PDF Workflow:
   - On the public app, confirm the default screen can proceed using the bundled judgment data without uploading a file.
4. Upload Flow:
   - Upload a PDF and wait for processing.
   - Expect the app to switch away from the bundled demo PDF and show the uploaded filename as active.
5. Mobile Validation:
   - Open the root route at `390x844`.
   - Expect the fixed header, stepper, and review columns to remain usable without clipped controls.

## Required Validation
- `docker compose up -d --build` from `/root/docker/aadeshai` must produce a healthy `aadeshai` container.
- `curl -I http://127.0.0.1:8501/_stcore/health` inside the running container context must return `200`.
- Public validation must cover `https://aadeshai.aidhunik.com` and `https://aadeshai.aidhunik.com/demo`.

## Known Operational Notes
- The current deployed-friendly mode is the built-in demo/mock pipeline; `OPENAI_API_KEY` is optional and should remain unset unless the app is later refactored to use the platform LLM service.
- `/demo` is implemented at the routing layer, not as a separate Streamlit page.