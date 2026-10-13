# Starter environment

Generic tooling only. The project itself is built from Sat 14 Nov 09:00 in its own repo.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r starter/requirements.txt
```

Before the weekend, also prepare (allowed prep):
- accounts: NASA Earthdata Login, api.nasa.gov key, GitHub, a deploy host (Vercel, Netlify, Hugging Face Spaces or GitHub Pages);
- a front-end boilerplate you know well (e.g. Vite + React + MapLibre/Leaflet, or Streamlit for a data app) deployed once as "hello world";
- video tools (screen recorder, editor with subtitle export) and a slide template;
- `ffmpeg` installed so `scripts/check_submission.py` can measure video length.
