# Vilcos Website Builder

Vilcos is an AI-powered website template manager that lets you create and edit website templates through natural language conversations.

## Features

- **AI-Powered Editing**: Use natural language to create and edit website templates
- **Live Preview**: See changes in real-time as you edit
- **File Watching**: Automatic synchronization between templates and preview
- **Static Publishing**: Generate optimized static sites for production
- **Docker Deployment**: Simple deployment with Docker

## Quick Start

```bash
# Make the vilcos script executable
chmod +x ./vilcos

# Install dependencies
./vilcos install

# Start the application
./vilcos start
```

Then access:
- **AI Management**: http://localhost:8000 (login: admin/password)
- **Website Preview**: http://localhost:3000

## Using the Application

In the AI Management Interface, you can:
- Create new pages by clicking "🆕 Create New Page" 
- Edit existing pages with the "✏️ Edit" buttons
- Preview your website with the "🔍 Live Preview" button
- Publish your site with the "📦 Publish Website" button

### AI Chat Examples
- **Create**: "Create a new page called about.html with an about section"
- **Edit**: "Add a navigation bar to index.html"
- **Style**: "Update index.html to use a blue color scheme"
- **List**: "Show me all templates"

## Project Structure

```
vilcos/
├── app.py                 # Chainlit AI interface
├── vilcos                 # Main command-line script
├── start.sh               # Development startup script
├── watch-templates.js     # Template file watcher
├── publish.sh             # Static site generator
├── deploy.sh              # Docker deployment script
├── templates/             # Website templates (editable)
│   ├── index.html         # Default template
│   └── src/               # CSS and JS files
├── dist/                  # Development build (generated)
└── public/                # Production build (generated)
```

## Available Commands

```bash
./vilcos help      # Show available commands
./vilcos start     # Start all components
./vilcos ai        # Start Chainlit AI interface only
./vilcos dev       # Start website preview only
./vilcos watch     # Start file watcher only
./vilcos publish   # Generate static site
./vilcos deploy    # Deploy with Docker (simple, single container)
./vilcos logs      # View application logs
./vilcos clean     # Clean generated files
```

## Development Workflow

Vilcos operates in two distinct modes to support both development/editing and production deployment.

### 1. Development Mode (Edit & Preview)
1. **Develop and Edit**:
   - Use the AI-powered interface to create/edit templates
   - Preview changes in real-time

### 2. Production Mode (Static Publishing)
1. **Publish**:
   - When satisfied, publish your site as static files: `./vilcos publish`
2. **Deploy**:
   - Deploy the optimized static site: `./vilcos deploy`
   - Benefit from improved performance and security

## Troubleshooting

- **OpenAI API Key**: You'll be prompted for your key when starting; get one at https://platform.openai.com/account/api-keys
- **Port Conflicts**: If ports 8000 or 3000 are in use, edit the port numbers in start.sh
- **Logs**: Check logs with `./vilcos logs` to diagnose issues

## Requirements

- Python 3.7+
- Node.js 16+
- npm 8+
- OpenAI API key

## License

MIT 