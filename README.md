# Vilcos - AI-Driven Website Template Editor

A minimal proof of concept for a website template editor powered by AI.

## Features

- **Simple Authentication**: Password-based login for secure access
- **Template Editing**: Create and edit website templates through natural language
- **AI-Powered**: Uses OpenAI's GPT models to understand and implement requested changes
- **File Management**: Restricted file operations for safe template manipulation

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables (create a `.env` file):
   ```
   OPENAI_API_KEY=your_openai_api_key
   CHAINLIT_USERNAME=admin
   CHAINLIT_PASSWORD=password
   ```

## Running

Start the application with:
```bash
chainlit run app.py
```

## Usage

1. Log in with your credentials
2. The AI assistant will create a default index.html if none exists
3. Chat with the assistant to create or edit templates:
   - "Create a new page called about.html"
   - "Add a contact form to index.html"
   - "Update the styling to use a dark theme"

All template files are stored in the `templates` directory. 