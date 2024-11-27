# Vilcos Framework 🚀

A modern, full-stack web framework built on FastAPI and Vue.js with real-time capabilities.

## Features ✨

- **Modern UI** - Integrated with Vue 3 + Vuetify for beautiful interfaces
- **Authentication** - Simple, secure session-based auth with Argon2 password hashing
- **Database** - Async SQLAlchemy with connection pooling
- **API Ready** - FastAPI-powered REST endpoints with automatic OpenAPI docs
- **Developer Friendly** - CLI tools, hot reloading, and interactive shell
- **Real-time WebSockets** - Built-in support for multi-channel WebSocket communication

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

2. Initialize and run:

```bash
vilcos init-db
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
    ├── routes/        # API endpoints and routes
    │   ├── auth.py    # Authentication routes
    │   └── ws.py      # WebSocket routes
    ├── models.py      # Database models
    ├── config.py      # Application settings
    ├── db.py         # Database configuration and utilities
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
- `/auth/me` - Get current user info

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

### WebSockets

```javascript
// Connect and send messages
const ws = new WebSocket('ws://localhost:8000/live/ws/mychannel');
ws.send(JSON.stringify({ message: 'Hello!' }));

// Receive messages
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

### CLI Tools

```bash
vilcos version          # Show version
vilcos run             # Development server
vilcos init-db         # Setup database
vilcos shell           # Interactive shell
```

## Requirements 📋

- Python 3.8+
- PostgreSQL
- Redis

## Configuration ⚙️

Essential `.env` settings:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
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