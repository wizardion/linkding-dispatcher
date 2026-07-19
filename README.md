# Linkding Dispatcher

A powerful bookmark dispatcher addon for [Linkding](https://github.com/sissbruecker/linkding) that enables automatic distribution and management of bookmarks across various services.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Token Authentication**: Secure API access with token-based authentication
- **Bookmark Management**: Create, read, update, and delete bookmarks with advanced filtering
- **Background Job Processing**: Asynchronous task execution using Redis/ARQ workers
- **Caching**: High-performance caching with Memcached and in-memory cache management
- **User Preferences**: Manage user settings and dispatch preferences
- **Bundle Operations**: Group bookmarks into bundles for bulk operations
- **Session Management**: Secure session handling with token tokens
- **RESTful API**: Clean, well-structured API endpoints
- **Web Interface**: Interactive TypeScript/Bootstrap frontend for easy bookmark management

## 🏗️ Architecture

The application consists of two main components:

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM and asyncpg driver
- **Task Queue**: Redis-backed job queue using ARQ
- **Caching**: Memcached and in-memory cache layer
- **Authentication**: token-based auth middleware
- **API Version**: v1.0 RESTful endpoints

### Frontend (TypeScript/Webpack)
- **Language**: TypeScript
- **Build Tool**: Webpack with dev server support
- **UI Framework**: Bootstrap 5
- **Code Quality**: ESLint and Prettier for code formatting

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx reverse proxy
- **Database**: PostgreSQL 16 Alpine
- **Cache**: Memcached & Redis

## 📦 Prerequisites

- **Docker** & **Docker Compose** (for containerized deployment)
- **Python** >= 3.13 (for local backend development)
- **Node.js** >= 18 (for frontend development)
- **PostgreSQL** 16 (if running outside Docker)
- **Redis** (for job queue)
- **Memcached** (for caching)

## 🚀 Installation

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd linkding-dispatcher
   ```

2. **Copy environment configuration**:
   ```bash
   cp docker-compose.example.yml docker-compose.yml
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - API: `http://bookmarks.local:8080/api/v1/dispatcher/`
   - Web UI: `http://bookmarks.local:8080/dispatcher/`
   - Linkding: `http://bookmarks.local:8080/`

### Local Development Setup

#### Backend

1. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -e .
   ```

2. **Set up environment variables**:
   ```bash
   cp local.env .env
   # Edit .env with your configuration
   ```

3. **Initialize database**:
   ```bash
   # Make sure PostgreSQL is running
   python -m dispatcher
   ```

#### Frontend

1. **Install dependencies**:
   ```bash
   cd web
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```
   The app will be available at `http://localhost:8080/`

## ⚙️ Configuration

### Backend Configuration

Environment variables in `backend/local.env`:

```bash
# Linkding Connection
LINKDING_HOST=127.0.0.1
LINKDING_PORT=3000
LINKDING_SCHEMA=HTTP

# Database
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=linkding
DB_PASSWORD=your_secure_password
DB_NAME=linkding

# Cache
MEMCACHE_HOST=127.0.0.1
MEMCACHE_PORT=11211
CACHE_LOGGING_ENABLED=true

# HTTP Protocol
HTTP_PROTOCOL=HTTP

# Redis/Task Queue
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### Frontend Configuration

Environment variables in `web/local.env`:

```bash
# Application URLs
APP_URL=http://bookmarks.local/dispatcher/
CHECK_URL=https://gemini.google.com/

# Backend Token
BACKEND_TOKEN=your_backend_token_here
```

## 🏃 Running the Application

### With Docker Compose
```bash
docker compose up -d --build
```

### Backend Only (Local)
```bash
cd backend
uvicorn dispatcher.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Only (Local)
```bash
cd web
npm start
```

### Background Workers
```bash
cd backend
python -m dispatcher.workers.config
```

### Cache Management

**Reset Memcached**:
```bash
docker exec -it linkding_memcached sh -c "echo 'flush_all' | nc 127.0.0.1 11211"
```

## 📁 Project Structure

```
linkding-dispatcher/
├── backend/                      # FastAPI backend application
│   ├── dispatcher/
│   │   ├── main.py              # Application entry point
│   │   ├── api/                 # API routes and endpoints
│   │   │   ├── routes.py
│   │   │   ├── dependencies.py
│   │   ├── core/                # Core application logic
│   │   │   ├── settings.py      # Configuration management
│   │   │   ├── lifespan.py      # App lifecycle events
│   │   │   ├── cache_manager.py # Caching logic
│   │   ├── db/                  # Database models and setup
│   │   │   ├── models.py
│   │   │   ├── database.py
│   │   ├── middleware/          # Custom middleware
│   │   │   ├── auth_middleware.py
│   │   │   ├── api_middleware.py
│   │   ├── schemas/             # Pydantic data models
│   │   │   ├── bookmark.py
│   │   │   ├── user.py
│   │   ├── services/            # Business logic
│   │   │   ├── bookmark_service.py
│   │   │   ├── linkding_service.py
│   │   │   ├── user_service.py
│   │   ├── workers/             # Background jobs
│   │   │   ├── tasks.py
│   │   │   ├── save_bookmark.py
│   │   │   ├── remove_bookmark.py
│   ├── pyproject.toml           # Python dependencies
│   ├── Dockerfile
│   └── local.env
│
├── web/                         # TypeScript/Webpack frontend
│   ├── src/
│   │   ├── index.ts            # Entry point
│   │   ├── index.html          # HTML template
│   │   ├── styles/             # SCSS stylesheets
│   │   ├── autocomplete/       # Autocomplete feature
│   │   ├── core/               # Core utilities
│   │   ├── types/              # TypeScript type definitions
│   ├── package.json
│   ├── webpack.config.js       # Production config
│   ├── webpack.dev.js          # Development config
│   ├── Dockerfile
│   └── local.env
│
├── docker-compose.yml          # Docker Compose configuration
├── docker-compose.example.yml  # Example configuration
├── example.nginx.conf          # Nginx configuration template
├── deploy.sh                   # Deployment script
└── README.md
```

## 👨‍💻 Development

### Backend Development

**Code Quality**:
```bash
cd backend

# Lint with Ruff
ruff check .

# Format code
ruff format .

# Type checking
py --strict  # Using ty package
```

**Database Migrations** (if using Alembic):
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

**Code Quality**:
```bash
cd web

# Lint
npm run lint

# Fix linting issues
npm run lint:fix

# Format with Prettier
npm run format
```

**Build for Production**:
```bash
npm run deploy
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v10/dispatcher/bookmark/check` | Check if URL is bookmarked |
| GET | `/api/v10/dispatcher/bookmark/metadata` | Get bookmark metadata and Linkding info |
| GET | `/api/v10/dispatcher/bookmark/info` | Get tags, bundles, and user preferences |
| GET | `/api/v10/dispatcher/bookmark/job/status/{job_id}` | Get background job status |
| POST | `/api/v10/dispatcher/bookmark/` | Save a new bookmark (async job) |
| DELETE | `/api/v10/dispatcher/bookmark/{bookmark_id}` | Remove a bookmark (async job) |

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Author**: Alex Zarnitsa ([alex@zarnitsa.com](mailto:alex@zarnitsa.com))
