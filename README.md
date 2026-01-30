# Notes (Django)

A lightweight, mobile-optimized note-taking Django app with user authentication, search, archiving, and trash functionality.

## Features

- ✅ **User Authentication**: Signup, login, logout with Django's built-in auth system
- ✅ **Create & Manage Notes**: Create, edit, view, and delete notes
- ✅ **Archive System**: Archive notes for later retrieval
- ✅ **Trash Management**: Soft delete with restore functionality
- ✅ **Search Functionality**: Search notes by title or content in real-time
- ✅ **User Profiles**: Auto-generated profiles with SVG avatar system (based on user initials)
- ✅ **Note Customization**: Color-coded notes and pinning support
- ✅ **Dark Mode Support**: Dark theme for better accessibility
- ✅ **Mobile-Optimized UI**: Off-canvas sidebar and responsive design
- ✅ **Timestamps**: Track note creation and modification dates

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

## Database Models

### Note
- `user`: Foreign Key to User (cascade delete)
- `title`: CharField (max 200 chars, can be blank)
- `content`: TextField (required)
- `color`: CharField (default: #ffffff) for note color coding
- `pinned`: BooleanField (default: False) for pinning notes
- `created_at`: Auto-generated timestamp
- `updated_at`: Auto-updated on save
- `archived`: BooleanField (default: False) for archiving notes
- `trashed`: BooleanField (default: False) for soft delete

### Profile
- `user`: OneToOne relationship to User (cascade delete)
- `profile_picture`: ImageField pointing to auto-generated SVG avatars

## Avatar System

- User profiles automatically get SVG avatars based on their initials (first name → last name → username)
- Avatars are pre-made SVG files stored in `static/avatars/` directory
- Named as `[INITIAL].svg` (e.g., `A.svg`, `B.svg`, etc.)
- Automatically assigned on user signup via Django signals

## Production Notes

- Always set `DEBUG=False` in production.
- Use a strong, random `SECRET_KEY` (never commit the real one).
- Configure `ALLOWED_HOSTS` with your domain(s).
- Serve static files using WhiteNoise (included in `requirements.txt`).
- Media files (user avatars and profile pictures) are stored in `media/` directory. For Render, consider using cloud storage (AWS S3, etc.) for production.

## Project Structure

```
notes_project/
├── notes/                 # Main Django app
│   ├── models.py         # Note, Profile models with signal handlers
│   ├── views.py          # Note CRUD, archive, trash, restore views
│   ├── urls.py           # URL routing
│   ├── forms.py          # Profile form
│   ├── context_processors.py  # Custom context processors
│   └── migrations/       # Database migrations
├── templates/            # HTML templates
│   ├── base.html         # Base layout with navigation
│   └── notes/            # App-specific templates (list, edit, profile, login, signup, trash)
├── static/               # CSS, JS, avatars
│   └── avatars/         # Pre-made SVG avatar files
├── media/               # User-uploaded media (profile pictures)
├── manage.py            # Django CLI
├── Procfile             # Render deployment config
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Technologies

- **Backend**: Django 6.0.1
- **Frontend**: HTML5, CSS3, Material Icons, Vanilla JS
- **Image Processing**: Pillow (for avatar handling)
- **Deployment**: Gunicorn, WhiteNoise, Render
- **Database**: SQLite (development), PostgreSQL recommended (production)

## Key Endpoints

- `GET /` - List all active notes
- `POST /` - Create a new note
- `GET /note/<id>/edit` - Edit note
- `POST /note/<id>/edit` - Save note
- `GET /archive/` - View archived notes
- `GET /trash/` - View trashed notes
- `GET /note/<id>/archive` - Archive a note
- `GET /note/<id>/unarchive` - Unarchive a note
- `GET /note/<id>/trash` - Move to trash
- `GET /note/<id>/restore` - Restore from trash
- `GET /profile/` - View and edit user profile
- `GET /login` - User login
- `POST /login` - Process login
- `GET /signup` - User registration
- `POST /signup` - Process signup
- `GET /logout` - User logout

## License

MIT License — feel free to use this project for personal or commercial purposes.

## Author

Made by Kamalesh

