# SynergySphere Backend

A FastAPI-based backend for the SynergySphere project management application.

## Features

- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Project Management**: Create, read, update, and delete projects
- **Task Management**: Full CRUD operations for tasks with status tracking
- **Comment System**: Project discussion through comments
- **Member Management**: Add/remove team members from projects
- **Database**: SQLite database with SQLAlchemy ORM

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure:

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-secret-key-change-in-production-12345
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Initialize Database

```bash
python init_db.py
```

This will create the database tables and optionally add sample data.

### 4. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Projects
- `GET /api/projects` - List user's projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `POST /api/projects/{id}/members` - Add member
- `POST /api/projects/{id}/tasks` - Create task
- `GET /api/projects/{id}/tasks` - Get project tasks
- `POST /api/projects/{id}/comments` - Add comment
- `GET /api/projects/{id}/comments` - Get comments

### Tasks
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Users
- `GET /api/users/me/tasks` - Get user's assigned tasks

## Database Schema

The application uses SQLite with the following main tables:

- **users**: User accounts and profiles
- **projects**: Project information and metadata
- **tasks**: Task details and assignments
- **comments**: Project discussion comments
- **project_members**: Many-to-many relationship between users and projects

## Development

### Running Tests

```bash
python test_server.py
```

### Database Reset

To reset the database:

```bash
rm app.db
python init_db.py
```

## Production Deployment

For production deployment:

1. Set a strong `SECRET_KEY` in your environment
2. Configure proper CORS origins
3. Use a production database (PostgreSQL recommended)
4. Set up proper logging and monitoring
5. Use a reverse proxy (nginx) for serving the application
