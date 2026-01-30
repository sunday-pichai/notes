# Notes (Django)

A lightweight, mobile-optimized note-taking Django app with user authentication, search, archiving, and trash functionality.

## Features

- ✅ User authentication (signup/login/logout)
- ✅ Create, edit, archive, and delete notes
- ✅ Search notes by title or content
- ✅ Trash management with permanent delete
- ✅ User profiles with custom avatars (auto-generated on signup)
- ✅ Dark mode support
- ✅ Mobile-optimized UI with off-canvas sidebar
- ✅ Light & responsive design

## Quick start (development)

1. Clone the repository:
```bash
git clone https://github.com/your-username/notes.git
cd notes
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Run migrations:
```bash
python manage.py migrate
```

6. (Optional) Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Open http://127.0.0.1:8000 in your browser.

## Deployment on Render

### Prerequisites
- Render account (free tier available)
- GitHub repository

### Steps

1. Push your code to GitHub.

2. On Render, create a new Web Service:
   - Connect your GitHub repo
   - Environment: Python
   - Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start command: `gunicorn notes_project.wsgi`

3. Add environment variables in Render dashboard:
   - `SECRET_KEY`: Generate a secure key (e.g. using Django's `get_random_secret_key()`)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: your-render-url.onrender.com
   - Add any other vars from `.env.example`

4. Deploy!

### Example Build & Start Commands for Render

```
Build: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
Start: gunicorn notes_project.wsgi
```

## Environment Variables

See `.env.example` for all available configuration options:

- `SECRET_KEY`: Django secret key (generate a strong one for production)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains
- `DATABASE_URL`: Optional; defaults to SQLite (leave blank for development)

## Production Notes

- Always set `DEBUG=False` in production.
- Use a strong, random `SECRET_KEY` (never commit the real one).
- Configure `ALLOWED_HOSTS` with your domain(s).
- Serve static files using WhiteNoise (included in `requirements.txt`).
- Media files (user avatars) are stored in `media/` directory. For Render, consider using cloud storage (AWS S3, etc.) for production.

## Project Structure

```
notes_project/
├── notes/                 # Main Django app
│   ├── models.py         # Note, Profile models
│   ├── views.py          # Note CRUD, auth views
│   ├── urls.py           # URL routing
│   ├── forms.py          # Profile form
│   └── migrations/       # Database migrations
├── templates/            # HTML templates
│   ├── base.html         # Base layout
│   └── notes/            # Note templates
├── static/               # CSS, JS, icons
├── manage.py             # Django CLI
├── Procfile              # Render deployment config
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

## Technologies

- **Backend**: Django 6.0.1
- **Frontend**: HTML5, CSS3, Material Icons, Vanilla JS
- **Deployment**: Gunicorn, WhiteNoise, Render
- **Database**: SQLite (development), PostgreSQL recommended (production)

## License

MIT License — feel free to use this project for personal or commercial purposes.

## Author

Made by Kamalesh

