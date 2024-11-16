# Vilcos Framework 🚀

A modern, full-stack web framework built on FastAPI and Vue.js with real-time capabilities.

## Features ✨

- **Real-time WebSockets** - Built-in support for multi-channel WebSocket communication
- **Modern UI** - Integrated with Vue 3 + Vuetify for beautiful interfaces
- **Authentication** - Complete auth system with Supabase integration
- **Database** - Async SQLAlchemy with connection pooling
- **API Ready** - FastAPI-powered REST endpoints with automatic OpenAPI docs
- **Developer Friendly** - CLI tools, hot reloading, and interactive shell

## Quick Start 🏃

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install vilcos
pip install vilcos
```

### Setup

1. Create project and environment:

```bash
mkdir myproject && cd myproject

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
EOF
```

2. Initialize and run:

```bash
vilcos init-db
vilcos run
```

Your app is now running at http://localhost:8000 🎉

## Project Structure 📁

```
myproject/
├── .env                # Configuration
└── vilcos/            # Application
    ├── static/        # Assets
    ├── templates/     # Views
    ├── routes/        # Endpoints
    ├── models.py      # Database models
    └── config.py      # Settings
```

## Key Features 🔑

### WebSockets

```javascript
// Connect and send messages
const ws = new WebSocket('ws://localhost:8000/live/ws/mychannel');
ws.send(JSON.stringify({ message: 'Hello!' }));

// Receive messages
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

### Authentication
- Built-in routes: `/auth/signin`, `/auth/signup`, `/auth/signout`
- Supabase integration
- GitHub OAuth support
- Session management with Redis

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
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-api-key
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