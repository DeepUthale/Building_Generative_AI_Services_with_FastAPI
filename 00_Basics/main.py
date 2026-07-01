# Import FastAPI class to create the web application
from fastapi import FastAPI
# Import the OpenAI client to talk to OpenAI's chat completion API
from openai import OpenAI
# Load environment variables from a local .env file
from dotenv import load_dotenv

# Read the .env file in this folder and populate os.environ
load_dotenv()

# Create the FastAPI application instance
app = FastAPI()
# Create an OpenAI client configured with an API key loaded from the
# OPENAI_API_KEY environment variable (set in the .env file, which is
# git-ignored and never committed to source control)
openai_Client = OpenAI()

# Register a GET endpoint at the root path "/"
@app.get("/")
def root_controller():
    return {"status": "healthy"}  # Simple health check response

# Register a GET endpoint at "/chat"
@app.get("/chat")
# prompt is a query parameter with a default value of "Inspire me"
def chat_controller(prompt: str = "Inspire me"):
    # Call OpenAI's chat completions endpoint with a system + user message
    response = openai_Client.chat.completions.create(
        model="gpt-4o",  # Which model to use for generating the response
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},  # Sets the assistant's behavior/persona
            {"role": "user", "content": prompt},  # The actual user prompt coming from the query parameter
        ],
    )

    # Extract the generated text from the first (and only) choice returned
    statement = response.choices[0].message.content
    return {"statemtnt": statement}  # Return the generated text as JSON


# ------------------------------------------------------------------
# THEORY: FastAPI Basics + Integrating an External API (OpenAI)
# ------------------------------------------------------------------
#
# 1. FastAPI application instance
#    `app = FastAPI()` creates the central object that ties together all
#    routes (endpoints), middleware, and configuration for your web service.
#
# 2. Path operation decorators (@app.get, @app.post, etc.)
#    These decorators register a Python function as the handler for a
#    specific HTTP method + URL path. FastAPI uses the function's signature
#    (parameter names, types, defaults) to automatically parse and validate
#    incoming requests.
#
# 3. Query parameters
#    Function arguments that are simple types (str, int, etc.) and are NOT
#    part of the URL path are treated as query parameters by default.
#    Example: `def chat_controller(prompt: str = "Inspire me")` means
#    GET /chat?prompt=hello will set prompt="hello"; if omitted, it defaults
#    to "Inspire me".
#
# 4. Automatic JSON serialization
#    Returning a Python dict from a path operation function causes FastAPI
#    to automatically serialize it to a JSON HTTP response.
#
# 5. Wrapping a third-party client (OpenAI SDK)
#    FastAPI doesn't care what your endpoint does internally - here it just
#    calls the OpenAI client's `chat.completions.create(...)` method and
#    returns the result. This illustrates how FastAPI apps commonly act as
#    a thin HTTP layer over some external service or business logic.
#
# 6. Security note: never hardcode API keys
#    Secrets like API keys should be loaded from environment variables or a
#    secrets manager (e.g. using python-dotenv or os.environ), not embedded
#    directly in source code, since source code is often shared, version
#    controlled, or otherwise exposed.
