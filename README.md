# Vilcos Framework 🚀

<p align="center">
  <img src="https://raw.githubusercontent.com/level09/vilcos/main/.github/images/vilcos.jpg" alt="Vilcos Framework Logo" width="300">
</p>

A modern, full-stack web framework built on FastAPI and Vue.js with real-time capabilities.

## Features ✨

- **Modern UI** - Vue 3 + Vuetify 3.7.3 for beautiful, responsive interfaces
- **Authentication** - Secure session-based auth with Argon2 password hashing and role-based access control
- **Database** - Async SQLAlchemy with PostgreSQL and connection pooling
- **API Ready** - FastAPI-powered REST endpoints with automatic OpenAPI docs
- **Developer Friendly** - CLI tools, hot reloading, and interactive shell
- **Real-time WebSockets** - Multi-channel WebSocket support with JSON message broadcasting
- **Session Management** - Redis-backed secure sessions with configurable settings
- **User Management** - Complete user administration with CRUD operations
- **Role-Based Access** - Flexible role management system with admin interface
- **Modern Frontend** - Material Design Icons, Axios for HTTP requests, and responsive layouts

## Quick Start 🏃

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/vilcos.git
cd vilcos

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install vilcos
pip install vilcos
```

### Environment Setup

1. Set up your environment variables:

```bash
# Copy the sample environment file
cp .env.sample .env

# Edit .env with your configuration
vim .env  # or use your preferred editor
```

Required environment variables:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# Security Settings
SECRET_KEY=your-secure-secret-key
SESSION_COOKIE_NAME=vilcos_session
SESSION_COOKIE_MAX_AGE=86400
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=lax

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

2. Initialize and run:

```bash
# Create database tables and default roles
vilcos init-db

# Create an admin user (optional)
vilcos create-admin

# Start the development server
vilcos run
```

Your app is now running at http://localhost:8000 🎉

## Project Structure 📁

```
vilcos/
├── .env.sample          # Sample environment configuration
├── pyproject.toml      # Project configuration and dependencies
├── requirements.txt    # Python dependencies
└── vilcos/            # Main package
    ├── static/        # Static assets
    ├── templates/     # View templates
    │   ├── admin/    # Admin interface templates
    │   └── auth/     # Authentication templates
    ├── routes/        # API endpoints and routes
    │   ├── auth.py    # Authentication routes
    │   ├── users.py   # User management routes
    │   ├── roles.py   # Role management routes
    │   └── websockets.py  # WebSocket routes
    ├── models.py      # Database models
    ├── schemas.py     # Pydantic schemas
    ├── config.py      # Application settings
    ├── db.py         # Database configuration and utilities
    ├── auth_utils.py  # Authentication utilities
    ├── utils.py      # Utility functions
    ├── cli.py        # Command-line interface
    └── app.py        # Application entry point
```

## Authentication 🔑

Vilcos uses a simple but secure session-based authentication system:

- **Secure Password Storage**: Argon2 hashing (winner of the Password Hashing Competition)
- **Session Management**: Redis-backed sessions with secure defaults
- **Cookie Security**: HTTPOnly, Secure, and SameSite flags enabled
- **Database Integration**: Direct SQLAlchemy models for user management

### Routes

- `/auth/signin` - User login
- `/auth/signup` - New user registration
- `/auth/signout` - User logout
- `/admin/users` - User management dashboard
- `/admin/roles` - Role management dashboard

### Security Best Practices

1. Generate a strong secret key:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

2. In production:
- Set `SESSION_COOKIE_SECURE=True`
- Use HTTPS
- Configure Redis with authentication
- Use strong database passwords

## Key Features 🔑

### User Management

The framework includes a comprehensive user management system:

- **User Administration**
  - Create, read, update, and delete users
  - Manage user roles and permissions
  - Toggle user activation status
  - Secure password management

- **Role Management**
  - Create and manage custom roles
  - Assign/remove roles from users
  - Role-based access control for routes
  - Admin interface for role management

### WebSockets

```javascript
// Connect to a specific channel
const ws = new WebSocket('ws://localhost:8000/ws/mychannel');

// Send JSON messages
ws.send(JSON.stringify({ 
    type: 'chat',
    content: 'Hello everyone!' 
}));

// Handle incoming messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`Received at ${data.timestamp}:`, data.data);
};
```

### CLI Tools

```bash
vilcos version          # Show version
vilcos run             # Start development server
vilcos init-db         # Initialize database tables
vilcos create-admin    # Create admin user
vilcos shell           # Launch interactive shell
```

## Requirements 📋

- Python 3.8+
- PostgreSQL
- Redis

## Configuration ⚙️

Essential `.env` settings:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
SECRET_KEY=your-secure-secret-key
REDIS_URL=redis://localhost:6379
```

## Contributing 🤝

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## License 📄

MIT License - see [LICENSE](LICENSE) file

## Support 💬

- GitHub Issues: Bug reports
- GitHub Discussions: Questions
- Documentation: [Coming Soon]

---

Built with ❤️ using FastAPI, Vue.js, and modern web technologies.