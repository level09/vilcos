import os
from pathlib import Path
import chainlit as cl
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
import logging # Import logging

# --- Modern Agno Knowledge Base Imports ---
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.embedder.openai import OpenAIEmbedder
# --- End Modern Imports ---

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Define base directory for templates
BASE_DIR = Path(os.getcwd())
TEMPLATES_DIR = BASE_DIR / "templates"
# Create templates directory if it doesn't exist
TEMPLATES_DIR.mkdir(exist_ok=True)

# --- Modern Agno Knowledge Base Setup ---
# Initialize the vector database with Agno's native ChromaDB implementation
# Using in-memory version without persistence to avoid file-related issues
vector_db = ChromaDb(
    collection="templates",
    embedder=OpenAIEmbedder()
)

# Create a knowledge base for templates
def create_template_knowledge():
    """
    Creates a knowledge base from template files using Agno's native DocumentKnowledgeBase.
    Returns a knowledge base instance that can be directly used with an Agent.
    """
    logging.info(f"Creating knowledge base from templates directory: {TEMPLATES_DIR}")
    
    # Check if the templates directory exists
    if not TEMPLATES_DIR.exists() or not TEMPLATES_DIR.is_dir():
        logging.warning(f"Templates directory {TEMPLATES_DIR} does not exist or is not a directory")
        return DocumentKnowledgeBase(documents=[], vector_db=vector_db)
    
    # Get HTML files only to simplify the approach 
    html_files = list(TEMPLATES_DIR.glob("**/*.html"))
    
    # Load the files directly
    documents = []
    for file_path in html_files:
        try:
            # Read the file content
            content = file_path.read_text(encoding='utf-8')
            
            # Create a simple document dictionary with page_content and metadata
            document = {
                "content": content,
                "metadata": {"source": str(file_path)}
            }
            
            documents.append(document)
            logging.info(f"Loaded file: {file_path}")
        except Exception as e:
            logging.error(f"Error loading file {file_path}: {e}")
    
    if not documents:
        logging.warning("No documents found for knowledge base")
        return DocumentKnowledgeBase(documents=[], vector_db=vector_db)
    
    logging.info(f"Successfully loaded {len(documents)} documents")
    
    # Create the knowledge base with the loaded documents
    knowledge_base = DocumentKnowledgeBase(
        documents=documents,  # List of document dictionaries
        vector_db=vector_db
    )
    
    # Load the knowledge base (process and index the documents)
    try:
        knowledge_base.load(recreate=False)
        logging.info("Knowledge base loaded successfully")
    except Exception as e:
        logging.error(f"Error loading knowledge base: {e}")
    
    return knowledge_base

# Create the template knowledge base
template_knowledge = create_template_knowledge()
# --- End Modern Knowledge Base Setup ---

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
    
    # Initialize conversation history
    cl.user_session.set("chat_history", [])
    
    # Set up file tools with restricted access to only the templates directory
    file_tools = FileTools(
        base_dir=TEMPLATES_DIR,
        save_files=True,
        read_files=True,
        list_files=True
    )
    
    # Simple function to fix path issues
    def normalize_path(path):
        """Normalize path to prevent nested templates directories."""
        path_str = str(path)
        if '/templates/templates/' in path_str:
            path_str = path_str.replace('/templates/templates/', '/templates/')
        return path_str
    
    # Log configuration
    logging.info(f"FileTools configured with base_dir: {TEMPLATES_DIR}")
    
    # Create an Agno agent for template editing with integrated knowledge base
    agent = Agent(
        model=OpenAIChat(id="gpt-4.1"),
        description="Website template editor that creates and edits HTML/CSS/JS files.",
        instructions=[
            # Clear, direct instructions for file operations
            "USE THE FILE TOOLS to save and read files in the templates directory.",
            "When asked to create or edit a file, ALWAYS USE save_file to save the changes.",
            "ALWAYS save files with their direct filename, like 'index.html' or 'src/style.css'.",
            "After saving a file, respond with: 'Done: [brief description of changes]'.",
            
            # Template guidance
            "Create HTML files with proper Tailwind CSS structure.",
            "HTML files should link to /src/main.js using <script type='module' src='/src/main.js'></script>.",
            "CSS should use Tailwind classes. Custom CSS goes in /src/style.css.",
            "JavaScript files should be placed in the /src directory.",
            
            # Important context
            f"Current directory structure:\n{template_contents}\n"
        ],
        tools=[file_tools],
        knowledge=template_knowledge,
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
    
    # Get conversation history
    chat_history = cl.user_session.get("chat_history", [])
    
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
        # Add user message to history
        chat_history.append({"role": "user", "content": message.content})
        
        # Create a full context message that includes history
        if len(chat_history) > 1:
            logging.info(f"Using conversation history with {len(chat_history)} messages")
        
        # Process the message with Agno and stream the response
        response_content = ""
        
        # Process the message with Agno and stream the response
        logging.info(f"Running agent with message: {message.content}")
        
        # Run the agent with the message
        for chunk in await cl.make_async(agent.run)(
            message.content,
            stream=True
        ):
            chunk_content = chunk.get_content_as_string()
            response_content += chunk_content
            await response_message.stream_token(chunk_content)
        
        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": response_content})
        
        # Update the session with the new history
        cl.user_session.set("chat_history", chat_history)
        
        # Keep history manageable (optional)
        if len(chat_history) > 20:  # Limit to last 20 messages
            chat_history = chat_history[-20:]
            cl.user_session.set("chat_history", chat_history)
        
        await response_message.send()
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await cl.Message(content=f"Error: {str(e)}").send()

# Running instructions: 
# chainlit run app.py -w 