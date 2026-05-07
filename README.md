# Quran & Sunnah Reflection

This is a small but meaningful prototype using Codex (AI), and it reminded me how fast AI is changing the way we create.

The idea was to build a Streamlit web app with AI & API Integration where a user can write how they are feeling, whether anxious, emotionally exhausted, grateful, lonely, hopeful, guilty, or going through a difficult phase of life. Based on that input, the app suggests relevant reminders from the Quran, authentic Hadith, and selected lessons from the Seerah, with proper references.

For the prototype, I used a curated local dataset. It includes selected Quranic verses, authentic Hadith references from collections like Sahih al-Bukhari, Sahih Muslim, and Jami’ at-Tirmidhi, and a few Seerah-based lessons such as Ta’if, Hijrah, Uhud, and the comfort of Khadijah رضي الله عنها during the beginning of revelation.

The app does not randomly generate religious content. It follows a retrieval-first approach: first it finds relevant references from the dataset, then AI helps explain them gently in the context of the user’s emotion.

**Some key features:**

- User can describe their emotional state in natural language
- App detects themes like anxiety, grief, guilt, gratitude, hope, loneliness, and burnout
- It retrieves Quran, Hadith, and Seerah-based reminders
- Each result includes references such as surah/ayah number or Hadith collection and number
- Arabic and English text are shown where available
- AI response is grounded in retrieved references
- Safety handling is included for severe emotional distress
- This is only a prototype, but it can be scaled in a much stronger way.

**Scaling Scope:**
For production, the curated dataset can be expanded and connected with authentic live sources through APIs, such as Quran.com / Quran Foundation APIs for Quranic verses, translations, and tafseer, QuranEnc for translations, Sunnah.com or Hadith APIs for authentic Ahadith, and structured Seerah resources for verified historical events and references.

That would allow the app to retrieve live, properly referenced content instead of depending only on local seed data.
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
