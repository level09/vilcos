import os
from pathlib import Path
import chainlit as cl
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
import logging # Import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Define base directory for templates
BASE_DIR = Path(os.getcwd())
TEMPLATES_DIR = BASE_DIR / "templates"
# Create templates directory if it doesn't exist
TEMPLATES_DIR.mkdir(exist_ok=True)

# Create src directory for CSS and JS files if it doesn't exist
SRC_DIR = TEMPLATES_DIR / "src"
SRC_DIR.mkdir(exist_ok=True)

def scan_templates_directory():
    """
    Scan the templates directory and return a formatted string with its contents.
    """
    template_contents = []
    
    # List files in templates root directory
    template_contents.append("Files in templates directory:")
    root_files = [f.name for f in TEMPLATES_DIR.glob("*") if f.is_file()]
    for f in sorted(root_files):
        template_contents.append(f"  - {f}")
    
    # List files in src directory if it exists
    if SRC_DIR.exists():
        template_contents.append("\nFiles in templates/src directory:")
        src_files = [f.name for f in SRC_DIR.glob("*") if f.is_file()]
        for f in sorted(src_files):
            template_contents.append(f"  - {f}")
    
    return "\n".join(template_contents)

def get_html_pages():
    """
    Get a list of all HTML pages in the templates directory.
    """
    return [f for f in TEMPLATES_DIR.glob("*.html")]

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Handle authentication."""
    # Simple auth using environment variables
    expected_username = os.getenv("CHAINLIT_USERNAME", "admin")
    expected_password = os.getenv("CHAINLIT_PASSWORD", "password")
    
    if username == expected_username and password == expected_password:
        return cl.User(identifier=username, metadata={"role": "admin"})
    return None

# --- Specific Action Callbacks --- 

@cl.action_callback("view_page")
async def handle_view_page(action):
    """Handles the 'view_page' action."""
    logging.info(f"Action received: Name={action.name}, Payload={action.payload}")
    payload = action.payload
    page_name = payload.get("file")

    if not page_name:
        logging.error("Missing file name for view action.")
        await cl.Message(content="Error: Missing file name for view action.").send()
        return
        
    full_path = TEMPLATES_DIR / page_name
    
    if full_path.exists() and full_path.is_file():
        content = full_path.read_text()
        await cl.Message(content=f"Content of **{page_name}**:\n```html\n{content}\n```").send()
    else:
        logging.warning(f"File not found for view action: {page_name}")
        await cl.Message(content=f"File {page_name} not found").send()

@cl.action_callback("edit_page")
async def handle_edit_page(action):
    """Handles the 'edit_page' action."""
    logging.info(f"Action received: Name={action.name}, Payload={action.payload}")
    payload = action.payload
    page_name = payload.get("file")

    if not page_name:
        logging.error("Missing file name for edit action.")
        await cl.Message(content="Error: Missing file name for edit action.").send()
        return
        
    await cl.Message(content=f"What changes would you like to make to {page_name}?").send()

@cl.action_callback("create_new_page")
async def handle_create_new_page(action):
    """Handles the 'create_new_page' action."""
    logging.info(f"Action received: Name={action.name}, Payload={action.payload}")
    await cl.Message(content="Please provide a name for the new page and describe its content.").send()

# --- End Specific Action Callbacks ---

@cl.on_chat_start
async def start():
    """Initialize the chat session and setup the agent."""
    # Get current directory contents for context
    template_contents = scan_templates_directory()
    
    # Set up file tools with restricted access to only the templates directory
    file_tools = FileTools(
        base_dir=TEMPLATES_DIR,
        save_files=True,
        read_files=True,
        list_files=True
    )
    
    # Create an Agno agent for template editing
    agent = Agent(
        model=OpenAIChat(id="gpt-4.1"),
        description="Concise AI assistant for editing website templates with Tailwind CSS.",
        instructions=[
            "Only work within the templates directory.",
            "Don't explain or share the changes you will make, just do it and notify the user.",
            "When asked to create or edit a template,say Right-o, Off we go! , then just do it without showing the code first.",
            "After editing a file, respond with only: 'Done: [brief description of changes]'.",
            "Only show code if the user specifically asks to see it.",
            "You help users edit website template files in HTML/CSS/JS using Tailwind CSS.",
            "HTML files should link to /src/main.js using <script type='module' src='/src/main.js'></script>.",
            "CSS is handled via Tailwind - use Tailwind classes for styling.",
            "Custom CSS should go in /src/style.css after the Tailwind imports.",
            "JavaScript files should be placed in the /src directory.",
            f"\nIMPORTANT - Current directory structure:\n{template_contents}\n",
            "ALWAYS work within this existing structure. DO NOT create nested 'templates' directories."
        ],
        tools=[file_tools],
        add_history_to_messages=True,
        show_tool_calls=True,
        markdown=True,
    )
    
    # Store the agent in user session
    cl.user_session.set("agent", agent)
    
    # Get HTML pages for buttons
    html_pages = get_html_pages()
    
    # Create action buttons for each page
    actions = []
    for page in html_pages:
        page_name = page.name
        actions.append(
            cl.Action(
                name="view_page",  # Generic name
                value=page_name, # Keep value for potential other uses
                description=f"View the content of {page_name}",
                label=f"👁️ View {page_name}",
                payload={"file": page_name} # Identify file in payload
            )
        )
        actions.append(
            cl.Action(
                name="edit_page",  # Generic name
                value=page_name, # Keep value for potential other uses
                description=f"Edit {page_name}",
                label=f"✏️ Edit {page_name}",
                payload={"file": page_name} # Identify file in payload
            )
        )
    
    # Add button to create a new page
    actions.append(
        cl.Action(
            name="create_new_page",
            value="new_page",
            description="Create a new HTML page",
            label="🆕 Create New Page",
            payload={"action": "create_new"}
        )
    )
    
    # First message to show the directory structure and page actions
    await cl.Message(
        content=f"""**Available Templates:**

I'll help you create and edit website templates. Use the buttons below to view or edit existing pages, or tell me what changes you'd like to make.

**Directory Structure:**
```
{template_contents}
```

What would you like to do?""",
        actions=actions
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages."""
    # Get the agent from user session
    agent = cl.user_session.get("agent")
    
    # Check for create new page command (simple check, could be improved)
    if message.content.lower().startswith("create new page"):
         # Forward to the create_new_page action handler logic
         # In a real app, you might want to parse details from the message
         await cl.Message(content="Please provide the name for the new page and describe its content.").send()
         # Or potentially invoke the handler directly if needed, though usually handled by action button
         # await handle_create_new_page(cl.Action(name="create_new_page", value="", payload={})) 
         return

    # Create a message for streaming the response
    response_message = cl.Message(content="")
    
    try:
        # Process the message with Agno and stream the response
        for chunk in await cl.make_async(agent.run)(
            message.content,
            stream=True,
        ):
            await response_message.stream_token(chunk.get_content_as_string())
        
        await response_message.send()
    except Exception as e:
        # Handle errors gracefully
        error_msg = f"Error: {str(e)}"
        logging.error(f"Error processing message: {error_msg}") # Log the error
        await cl.Message(content=error_msg).send()

# Running instructions: 
# chainlit run app.py -w 