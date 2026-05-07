# Quran & Sunnah Reflection

A local Streamlit prototype that lets a user describe how they feel and receives grounded reminders from the Quran, authentic hadith, and selected Seerah lessons.

## Moreover


## Run Locally

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open http://localhost:8501.

## Deploy Permanently

Recommended path: Streamlit Community Cloud.

1. Push this project to a GitHub repository.
2. Go to https://share.streamlit.io.
3. Choose the repository and set the main file path to `app.py`.
4. Add optional secrets from `.env.example` only if needed.
5. Deploy and share the generated Streamlit URL.

The app works without API keys because it uses `data/content_seed.json`.

## Optional Keys

Copy `.env.example` to `.env` and fill only the services you want to use.

- `OPENAI_API_KEY` enables AI-generated grounded reflections.
- `QURAN_CLIENT_ID`, `QURAN_CLIENT_SECRET`, and `QURAN_ACCESS_TOKEN` are reserved for Quran Foundation/Quran.com enrichment.
- `HADITH_API_KEY` is reserved for structured hadith API enrichment.

Without keys, the app uses `data/content_seed.json`.

## Project Structure

- `app.py` is the main Streamlit app. It builds the UI, collects the user's feeling, shows Quran/Hadith/Seerah tabs, renders references, and handles crisis messaging.
- `src/retrieval.py` detects emotional themes and retrieves the most relevant Quran, Hadith, and Seerah items from the local dataset.
- `src/ai.py` creates a short grounded reflection. It uses OpenAI only when `OPENAI_API_KEY` is configured; otherwise it falls back to a local response.
- `src/sources.py` contains optional API clients for future Quran Foundation/Quran.com, QuranEnc, and HadithAPI integrations.
- `data/content_seed.json` is the curated prototype dataset with Quran verses, authentic Hadith, and Seerah lessons including references, themes, Arabic/English text, and source URLs.
- `scripts/smoke_test.py` is a quick test that checks dataset loading, retrieval, crisis detection, and reflection generation.
- `.streamlit/config.toml` controls the Streamlit theme.
- `.env.example` lists optional environment variables and API keys.
- `requirements.txt` lists Python dependencies.
- `.gitignore` keeps local environments, logs, caches, and secrets out of Git.
- `.venv/` is the local Python environment used to run the app. It is useful locally but is uploaded to GitHub.

## Guardrails

- The app retrieves citations first and only explains retrieved items.
- It does not invent Quran verses, hadith, grades, references, fatwas, or diagnoses.
- Crisis-like language triggers a gentle safety message encouraging immediate real-world support.
