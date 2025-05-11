# <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos.png" alt="Vilcos Logo" width="100" align="left" style="margin-right: 10px;"/> Vilcos: Your Website's AI-Powered Developer & Content Manager

&nbsp;
&nbsp;

**Vilcos transforms how you create and manage your website. Instead of a traditional CMS or a separate admin panel, your website gets its own dedicated, self-hosted AI web developer agent. Simply chat with it to build your initial site, make updates, manage content on any page, and evolve your entire project over time – all through natural language!**

<p align="center">
  <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos-demo.gif" alt="Vilcos Demo" width="80%"/>
</p>

Vilcos is an AI-powered framework that empowers you to:
-   **Create & Build:** Generate new pages and entire site structures.
-   **Edit & Update:** Modify HTML, CSS (including Tailwind CSS), JavaScript, and importantly, the content within your pages.
-   **Manage & Evolve:** Iteratively refine your website, add new sections, or change layouts, much like a CMS, but through a conversational interface with your own AI agent.

<p align="center">
  <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos-robot.gif" alt="Vilcos Robot" width="250"/>
</p>

This self-hosted agent acts as your personal web development assistant, understanding your requests and applying changes directly to your project files.

## Features

- **AI-Powered Website Management**: Use natural language to create, edit, and manage your entire website – pages, content, and structure.
- **Live Preview**: See changes in real-time as you interact with your AI agent.
- **File Watching**: Automatic synchronization for instant feedback during development.
- **Static Publishing**: Generate optimized static sites ready for production.
- **Self-Hosted Agent**: You control the core AI agent framework.
- **Docker Deployment**: Simple deployment option available for the published static site.

## Quick Start

### Option 1: Using npx (Recommended)

The fastest way to get started with Vilcos:

```bash
# Create a new Vilcos project
npx create-vilcos-app my-website

# Or initialize in the current directory
npx create-vilcos-app

# Start the application
cd my-website  # If you specified a project name
./vilcos start
```

### Option 2: Manual Installation

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

    This will automatically copy default templates to the `templates/` directory if none exist.
    The `templates/` directory is excluded from git to keep your repository clean.

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
├── deploy.sh              # One-step deployment script
├── force-rebuild.sh       # Forces clean template rebuilds
├── templates/             # Website templates (editable)
│   ├── index.html         # Default template
│   ├── src/               # CSS and JS source files
│   └── dist/              # Development build (generated)
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
   - Files are built to `templates/dist/` for development preview
   - Preview changes in real-time at http://localhost:3000

### 2. Production Mode (Static Publishing)
1. **Publish**:
   - When satisfied, publish your site as static files: `./vilcos publish`
   - This creates optimized files in the `public/` directory with production settings
2. **Deploy Locally**:
   - You have two options for Docker deployment:
     - **Quick deployment with pre-built files**: `./vilcos deploy -p` (uses existing files)
     - **Full deployment from source**: `./vilcos deploy` (builds the site inside Docker)
   - Benefit from improved performance and security

### 3. Cloud Deployment (Fly.io)
Vilcos includes ready-to-use configuration for deploying to [Fly.io](https://fly.io/), a platform-as-a-service for running applications globally.

1. **Prerequisites**:
   - Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/): `curl -L https://fly.io/install.sh | sh`
   - Sign up and authenticate: `flyctl auth signup` or `flyctl auth login`

2. **Deploy to Fly.io**:
   ```bash
   # First time setup (only once)
   fly launch
   
   # For subsequent deployments (recommended workflow):
   ./deploy.sh            # One-step build and deploy
   
   # If template changes aren't showing up:
   ./force-rebuild.sh     # Force a clean rebuild of templates
   ./deploy.sh            # Then deploy as normal
   
   # For advanced users (manual steps):
   ./vilcos publish       # Generate optimized files in public/
   cd public              # Navigate to the public directory
   fly deploy --local-only # Deploy your local files
   ```

   The `--local-only` flag ensures your customized templates are used in deployment.
   
   > **IMPORTANT**: When making changes to templates (e.g., index.html), always use `./force-rebuild.sh` before deploying to ensure changes are properly detected and built.

Your site will be available at `https://your-app-name.fly.dev`.

## Understanding the Build Process

1. **Development builds** go to `templates/dist/` and are used for the preview server
2. **Production builds** go to `public/` and include additional optimizations and configurations
3. When template changes aren't reflected in deployment, use `./force-rebuild.sh` to clear the build cache

## Troubleshooting

- **Template changes not appearing**: Run `./force-rebuild.sh` followed by `./deploy.sh`
- **OpenAI API Key**: You'll be prompted for your key when starting; get one at https://platform.openai.com/account/api-keys
- **Port Conflicts**: If ports 8000 or 3000 are in use, edit the port numbers in start.sh
- **Logs**: Check logs with `./vilcos logs` to diagnose issues
- **Content Security Policy**: If embedding external content (YouTube, etc.), check the CSP in `publish.sh`

## Requirements

- Python 3.7+
- Node.js 16+
- npm 8+
- OpenAI API key

## License

MIT 