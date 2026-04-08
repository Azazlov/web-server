# FileShare Local v2.1 — Project Context

## Project Overview

**FileShare Local** is a local file-sharing server built with Python Flask. It provides role-based access control (Admin/User), shared and personal folders, nested directory support, and a responsive Russian-localized web interface. The application uses a modular architecture with Flask Blueprints and an application factory pattern.

### Core Features
- **Role-based access control**: Admin (full control) and User (read-only shared) roles
- **Shared folder**: Admins can upload/delete; users can only view/download (unless granted upload permission)
- **Personal folders**: Private per-user directories with full owner control
- **Nested folder support**: Hierarchical directory navigation with breadcrumbs
- **Admin panel**: User management, server settings toggle, live server restart, statistics
- **Auto-first-admin**: The first registered user becomes an Administrator automatically
- **Configurable settings**: Port, max upload size, registration toggle, debug mode via `config.json`

### Tech Stack
- **Backend**: Python 3.8+, Flask 2.3.3
- **Database**: SQLite via Flask-SQLAlchemy 3.0.5
- **Auth**: Flask-Login 0.6.2, Werkzeug password hashing
- **Frontend**: Bootstrap 5, Jinja2 templates, custom CSS/JS
- **Localization**: Russian

---

## Building and Running

### Prerequisites
- Python 3.8+
- Administrator/root privileges if using port 80

### Quick Start

**Windows** (run as Administrator for port 80):
```batch
cd scripts
setup_and_run.bat
```

**Linux/macOS**:
```bash
cd scripts
sudo ./setup_and_run.sh
```

Access at: `http://localhost` or `http://fileserver.local`

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

### Using a Non-Privileged Port
Edit `config.json`:
```json
{ "server_port": 8080 }
```
Then restart the server.

### Available Scripts
| Script | Purpose |
|--------|---------|
| `scripts/setup_and_run.bat/.sh` | Full setup and server start |
| `scripts/restart_server.bat/.sh` | Restart the server |
| `scripts/stop_server.bat/.sh` | Stop the server |
| `scripts/setup_hosts.bat/.sh` | Configure hosts file for `fileserver.local` |

---

## Project Structure

```
web-server/
├── app.py                      # Application factory (create_app)
├── requirements.txt            # Python dependencies
├── config.json                 # Runtime configuration (generated)
├── database.db                 # SQLite database (generated, in instance/)
│
├── modules/                    # Core application modules
│   ├── __init__.py
│   ├── config.py               # Configuration manager (load/save config.json)
│   ├── models.py               # SQLAlchemy models + CRUD helpers + schema migration
│   ├── utils.py                # Utility functions (path handling, decorators, formatting)
│   └── routes/                 # Flask Blueprints
│       ├── __init__.py         # Blueprint exports
│       ├── auth.py             # /login, /register, /logout
│       ├── main.py             # /, /dashboard, /shared, /personal
│       ├── files.py            # /upload, /download, /delete, /mkdir
│       └── admin.py            # /admin, /admin/settings
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with navbar
│   ├── login.html
│   ├── register.html
│   ├── shared.html             # Shared folder view
│   ├── personal.html           # Personal folder view
│   └── admin.html              # Admin panel
│
├── static/                     # Static assets
│   ├── css/style.css
│   └── js/main.js
│
├── uploads/                    # File storage
│   ├── shared/                 # Shared folder
│   └── users/{username}/       # Per-user personal folders
│
├── scripts/                    # Shell/batch scripts
├── diagrams/                   # Mermaid diagrams (12 files)
└── instance/                   # Flask instance folder (database.db)
```

---

## Architecture

### Application Factory (`app.py`)
```python
def create_app():
    app = Flask(__name__)
    # Config → Extensions → LoginManager → Blueprints → DB init
    return app
```

### Blueprints

| Blueprint | Routes |
|-----------|--------|
| `auth_bp` | `/login`, `/register`, `/logout` |
| `main_bp` | `/`, `/dashboard`, `/shared`, `/personal` |
| `files_bp` | `/upload`, `/download`, `/delete`, `/mkdir` |
| `admin_bp` | `/admin`, `/admin/settings` |

### Database Models

**User** (`users` table):
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `username` | String(50) | Unique username |
| `password_hash` | Text | Hashed password |
| `role` | Text | `'admin'` or `'user'` |
| `created_at` | DateTime | Registration timestamp |
| `upload_blocked` | Boolean | Blocks personal folder uploads |
| `can_upload_shared` | Boolean | Allows shared folder uploads for non-admins |

### Configuration (`config.json`)
```json
{
    "server_port": 80,
    "max_upload_size_mb": 100,
    "allow_registration": true,
    "debug_mode": false
}
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `server_port` | HTTP server port | 80 |
| `max_upload_size_mb` | Max upload size in MB | 100 |
| `allow_registration` | Allow new user registration | true |
| `debug_mode` | Flask debug mode | false |

---

## Access Control

### Shared Folder (`/shared`)

| Action | Admin | User (default) | User (with `can_upload_shared`) |
|--------|-------|----------------|---------------------------------|
| View | ✅ | ✅ | ✅ |
| Download | ✅ | ✅ | ✅ |
| Upload | ✅ | ❌ | ✅ |
| Create Folders | ✅ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ |

### Personal Folder (`/users/{username}`)

| Action | Owner | Others |
|--------|-------|--------|
| All operations | ✅ | ❌ |

**Note**: Admins can block a user's personal folder uploads via `upload_blocked` flag.

---

## Security

- Passwords hashed with `werkzeug.security.generate_password_hash`
- Path traversal prevention (`..` stripping + `startswith(base_path)` validation)
- `@login_required` and `@admin_required` decorators on protected routes
- `secure_filename` used for uploaded files
- Jinja2 auto-escaping for XSS protection

---

## Development Conventions

- **Python style**: snake_case naming, docstrings on modules/classes, error handling with try/except
- **Modular design**: Each concern isolated (config, models, utils, route blueprints)
- **CRUD helpers**: Database operations in `models.py` as standalone functions, not methods on models
- **Russian localization**: All user-facing text in templates and flash messages is in Russian
- **No formal test suite**: Testing is manual via the web interface
- **Schema migration**: `migrate_database_schema()` adds missing columns on startup using raw SQL `ALTER TABLE`

---

## Common Operations

### View database
```bash
sqlite3 instance/database.db ".schema"
```

### Reset database (deletes all data)
```bash
rm database.db  # or del database.db on Windows
```

### Reset configuration
```bash
rm config.json
```

### Check what's using port 80
```bash
# Windows
netstat -ano | findstr :80

# Linux/macOS
lsof -i :80
```

---

## Known Issues

1. **Port 80 requires admin/root** — Use port 8080 or run with elevated privileges
2. **Restart may fail with "Address already in use"** — The old process may still hold the port; manually kill it and restart
3. **Registration can be disabled** — Re-enable via admin panel or by editing `config.json`

---

## Key Code Patterns

### Creating a new route in a blueprint
```python
from flask import Blueprint
my_bp = Blueprint('my', __name__)

@my_bp.route('/my-route')
@login_required          # if auth needed
@admin_required          # if admin only
def my_view():
    ...
```

### Adding a config setting
1. Add to `DEFAULT_CONFIG` in `modules/config.py`
2. Add a `@property` accessor on the `Config` class
3. Add to `config.json` if you want a non-default value

### Adding a database column
1. Add to `User` model in `modules/models.py`
2. Add migration logic to `migrate_database_schema()` using `ALTER TABLE`
3. The migration runs automatically on app startup

---

## Metrics

| Metric | Value |
|--------|-------|
| Python source files | 8 |
| Total Python LOC | ~864 |
| HTML templates | 6 |
| Mermaid diagrams | 12 |
| Blueprints | 4 |
