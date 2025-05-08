# Vilcos: Give Your Site a Built-in, Self-Hosted AI Web Developer

<p align="center">
  <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos.png" alt="Vilcos Logo" width="300"/>
</p>

**Vilcos transforms how you create and manage your website. Instead of a traditional CMS or a separate admin panel, your website gets its own dedicated, self-hosted AI web developer agent. Simply chat with it to build your initial site, make updates, manage content on any page, and evolve your entire project over time – all through natural language!**

Vilcos is an AI-powered framework that empowers you to:
-   **Create & Build:** Generate new pages and entire site structures.
-   **Edit & Update:** Modify HTML, CSS (including Tailwind CSS), JavaScript, and importantly, the content within your pages.
-   **Manage & Evolve:** Iteratively refine your website, add new sections, or change layouts, much like a CMS, but through a conversational interface with your own AI agent.

This self-hosted agent acts as your personal web development assistant, understanding your requests and applying changes directly to your project files.

## Features

- **AI-Powered Website Management**: Use natural language to create, edit, and manage your entire website – pages, content, and structure.
- **Live Preview**: See changes in real-time as you interact with your AI agent.
- **File Watching**: Automatic synchronization for instant feedback during development.
- **Static Publishing**: Generate optimized static sites ready for production.
- **Self-Hosted Agent**: You control the core AI agent framework.
- **Docker Deployment**: Simple deployment option available for the published static site.

## Quick Start

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/level09/vilcos.git
    cd vilcos
    ```

2.  **Install Dependencies:**
    *(Ensure you have Python 3.7+ and Node.js 16+ installed)*
    ```bash
    ./vilcos install
    ```

3.  **Configure OpenAI API Key:**
    Vilcos needs access to the OpenAI API.
    *   You can set the `OPENAI_API_KEY` environment variable before starting:
        ```bash
        export OPENAI_API_KEY='your_api_key_here'
        ```
    *   Alternatively, when you run `./vilcos start` for the first time, you will be prompted to enter your API key. This key will be saved to a local `.env` file for future use.
    You can obtain an API key from [OpenAI Platform](https://platform.openai.com/account/api-keys).

4.  **Start the Application:**
    ```bash
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