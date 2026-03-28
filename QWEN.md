# FileShare Local v2.1 - Project Context

## Project Overview

**FileShare Local** is a local file sharing server built with Flask, featuring role-based access control and a responsive web interface. The application allows administrators and users to manage files in shared and personal folders with different permission levels.

### Key Features
- **Role-based access control**: Admin and User roles with different permissions
- **Shared folder**: Full access for admins, read-only for users
- **Personal folders**: Private storage for each user
- **Nested folder support**: Hierarchical folder structure
- **Responsive UI**: Bootstrap 5-based web interface (Russian localization)
- **Admin panel**: User management, server settings, statistics
- **Modular architecture**: Separated into independent components (Blueprints)

### Tech Stack
- **Backend**: Python 3.8+, Flask 2.3.3
- **Database**: SQLite with Flask-SQLAlchemy 3.0.5
- **Authentication**: Flask-Login 0.6.2, Werkzeug password hashing
- **Frontend**: Bootstrap 5, Jinja2 templates, custom CSS/JS

---

## Building and Running

### Quick Start

**Linux/macOS** (requires root for port 80):
```bash
cd scripts
sudo ./setup_and_run.sh
```

**Windows** (run as Administrator):
```batch
cd scripts
setup_and_run.bat
```

**Access**: http://fileserver.local or http://localhost

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

### Development Mode

Edit `config.json` to enable debug mode:
```json
{
    "debug_mode": true
}
```

### Available Scripts

| Script | Description |
|--------|-------------|
| `setup_and_run.sh/.bat` | Full setup and server start |
| `restart_server.sh/.bat` | Restart server |
| `stop_server.sh/.bat` | Stop server |
| `setup_hosts.sh/.bat` | Configure hosts file |

---

## Project Structure

```
web-server/
├── app.py                      # Application factory (76 lines)
├── requirements.txt            # Python dependencies
├── config.json                 # Runtime configuration (generated)
├── database.db                 # SQLite database (generated)
│
├── modules/                    # Core application modules
│   ├── __init__.py
│   ├── config.py               # Configuration manager (~90 lines)
│   ├── models.py               # Database models & CRUD (~120 lines)
│   ├── utils.py                # Utility functions (~165 lines)
│   └── routes/                 # Flask Blueprints
│       ├── __init__.py
│       ├── auth.py             # Authentication routes (~85 lines)
│       ├── main.py             # Main pages (~65 lines)
│       ├── files.py            # File operations (~150 lines)
│       └── admin.py            # Admin panel (~75 lines)
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base template with navbar
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── shared.html             # Shared folder view
│   ├── personal.html           # Personal folder view
│   └── admin.html              # Admin panel
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Custom styles
│   └── js/
│       └── main.js             # Client-side scripts
│
├── uploads/                    # User file storage
│   ├── shared/                 # Shared folder
│   └── users/                  # Personal folders (username-based)
│
├── scripts/                    # Shell scripts
│   ├── setup_and_run.sh/.bat
│   ├── restart_server.sh/.bat
│   ├── stop_server.sh/.bat
│   └── setup_hosts.sh/.bat
│
└── diagrams/                   # Mermaid diagrams (12 files)
    ├── 01_architecture.mmd     # Architecture overview
    ├── 02_config.mmd           # Config module
    ├── 03_models.mmd           # Models module
    ├── 04_utils.mmd            # Utils module
    ├── 05_auth.mmd             # Authentication flow
    ├── 06_main.mmd             # Main pages flow
    ├── 07_files.mmd            # File management flow
    ├── 08_admin.mmd            # Admin panel structure
    ├── 09_upload.mmd           # Upload sequence
    ├── 10_request_lifecycle.mmd
    ├── 11_database.mmd         # Database ER diagram
    └── 12_project_tree.mmd
```

---

## Architecture

### Application Factory Pattern

```python
# app.py
def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = '...'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    
    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)
    
    return app
```

### Blueprints

| Blueprint | Prefix | Routes |
|-----------|--------|--------|
| `auth_bp` | — | `/login`, `/register`, `/logout` |
| `main_bp` | — | `/`, `/dashboard`, `/shared`, `/personal` |
| `files_bp` | — | `/upload`, `/download`, `/delete`, `/mkdir` |
| `admin_bp` | — | `/admin`, `/admin/settings` |

### Database Models

**User** (`users` table):
- `id`, `username`, `password_hash`, `role`, `created_at`, `upload_blocked`

---

## Configuration

### Config File (`config.json`)

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
| `server_port` | Server port | 80 |
| `max_upload_size_mb` | Max file size (MB) | 100 |
| `allow_registration` | Allow user registration | true |
| `debug_mode` | Flask debug mode | false |

---

## Access Control

### Shared Folder (`/shared`)

| Action | Admin | User |
|--------|-------|------|
| View | ✅ | ✅ |
| Download | ✅ | ✅ |
| Upload | ✅ | ❌ |
| Create Folders | ✅ | ❌ |
| Delete | ✅ | ❌ |

### Personal Folder (`/users/{username}`)

| Action | Owner | Others |
|--------|-------|--------|
| View/Download/Upload/Delete | ✅ | ❌ |

**Note**: Admin can block user upload permissions via admin panel.

---

## Development Conventions

### Code Style
- Python modules follow snake_case naming
- Docstrings present on all modules and classes
- Type hints used where applicable
- Error handling with try/except blocks

### Security Practices
- Password hashing with `werkzeug.security.generate_password_hash`
- Path traversal prevention with `secure_filename` and path validation
- Login required decorators on protected routes
- Admin-only routes protected with `@admin_required`
- Jinja2 auto-escaping for XSS protection

### Testing
- No formal test suite present
- Manual testing via web interface

### First User Behavior
- The first registered user automatically becomes an **Administrator**
- Subsequent users are created as regular **Users**

---

## Common Commands

```bash
# View database contents
sqlite3 instance/database.db ".schema"

# Check running process
lsof -i :80  # macOS/Linux
netstat -ano | findstr :80  # Windows

# Reset database (deletes all users)
rm database.db  # or del database.db on Windows

# Reset configuration
rm config.json
```

---

## Known Issues

1. **Port 80 requires admin/root privileges** - Use port 8080 or run with sudo
2. **Restart script may cause "Address already in use"** - Manual restart may be needed
3. **Registration can be disabled** - Re-enable via admin panel or config.json

---

## Metrics

| Metric | Value |
|--------|-------|
| Python files | 8 |
| Total Python LOC | ~864 |
| HTML templates | 6 |
| Mermaid diagrams | 12 |
| Blueprints | 4 |
