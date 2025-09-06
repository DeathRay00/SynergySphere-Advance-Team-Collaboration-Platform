# SynergySphere - Project Management Application

A modern, full-stack project management application built with React and FastAPI, featuring real-time collaboration, task management, and team communication.

## 🚀 Features

- **User Authentication**: Secure login and registration with JWT tokens
- **Project Management**: Create, edit, and manage projects
- **Task Management**: Create, assign, and track tasks with status updates
- **Team Collaboration**: Add team members to projects
- **Real-time Comments**: Discuss projects with team members
- **Responsive Design**: Modern UI built with Tailwind CSS and shadcn/ui components

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **SQLite**: Lightweight, serverless database
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful, accessible UI components
- **Lucide React**: Beautiful & consistent icon toolkit

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+** (for backend)
- **Node.js 16+** and **npm/yarn** (for frontend)
- **Git** (for version control)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd synergysphere
```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Start the backend server
python start.py
```

The backend will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install

# Start the development server
npm start
# or
yarn start
```

The frontend will be available at `http://localhost:3000`

## 🗄️ Database

The application uses SQLite as the database, which is automatically created when you run the initialization script. The database file (`app.db`) will be created in the backend directory.

### Sample Data
The initialization script creates sample users for testing:
- **Email**: `john@example.com` | **Password**: `password123`
- **Email**: `jane@example.com` | **Password**: `password123`

## 📁 Project Structure

```
synergysphere/
├── backend/
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── server.py            # FastAPI application
│   ├── init_db.py           # Database initialization
│   ├── start.py             # Startup script
│   ├── config.py            # Configuration settings
│   ├── requirements.txt     # Python dependencies
│   └── app.db              # SQLite database (created automatically)
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Application entry point
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind CSS configuration
└── README.md
```

## 🔧 Configuration

### Backend Configuration
The backend configuration is managed in `backend/config.py`:
- `SECRET_KEY`: JWT secret key for token signing
- `CORS_ORIGINS`: Allowed origins for CORS requests

### Frontend Configuration
The frontend expects the backend URL to be available as an environment variable:
- `REACT_APP_BACKEND_URL`: Backend API URL (defaults to `http://localhost:8000`)

## 🚀 Deployment

### Backend Deployment
1. Set up a production database (PostgreSQL recommended)
2. Update the database URL in `database.py`
3. Set production environment variables
4. Use a production WSGI server like Gunicorn

### Frontend Deployment
1. Build the production bundle: `npm run build`
2. Serve the `build` directory with a web server
3. Update the backend URL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database not found**: Run `python init_db.py` in the backend directory
2. **CORS errors**: Ensure the frontend URL is included in `CORS_ORIGINS`
3. **Port already in use**: Change the port in the startup scripts
4. **Module not found**: Ensure all dependencies are installed

### Getting Help

If you encounter any issues:
1. Check the console for error messages
2. Ensure all dependencies are installed correctly
3. Verify that both backend and frontend are running
4. Check the API documentation at `http://localhost:8000/docs`

## 🎯 Future Enhancements

- [ ] Real-time notifications with WebSockets
- [ ] File upload and sharing
- [ ] Advanced project analytics
- [ ] Mobile app with React Native
- [ ] Integration with external tools (Slack, GitHub, etc.)
- [ ] Advanced user roles and permissions
- [ ] Project templates
- [ ] Time tracking
- [ ] Gantt charts and project timelines

---

**Happy coding! 🚀**