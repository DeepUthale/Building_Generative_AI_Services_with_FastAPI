# Path is used to build filesystem paths in an OS-independent way
from pathlib import Path

# FastAPI is the app class; Depends declares dependencies; Request represents an incoming HTTP request
from fastapi import FastAPI, Depends, Request
# Jinja2Templates lets FastAPI render HTML templates using the Jinja2 engine
from fastapi.templating import Jinja2Templates

# Create the FastAPI application instance
app = FastAPI()
# Configure Jinja2 to look for templates inside a "templates" folder next to this file
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Fake in-memory "database" of 50 messages, generated at startup
messages = [{"id": i, "text": f"message {i}"} for i in range(1, 51)]
# Fake in-memory "database" of 20 conversations, generated at startup
conversations = [{"id": i, "title": f"conversation {i}"} for i in range(1, 21)]

# Shared dependency function: extracts pagination parameters from the request
def paginate(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}  # Returned value gets injected wherever this is used as a dependency

# Register a GET endpoint at "/messages"
@app.get("/messages")
# pagination is computed by calling paginate(), reusing the same logic instead of duplicating it
def list_messages_controller(pagination: dict = Depends(paginate)):
    skip, limit = pagination["skip"], pagination["limit"]  # Unpack the injected pagination values
    return messages[skip: skip + limit]  # Slice the messages list according to skip/limit

# Register a GET endpoint at "/conversations"
@app.get("/conversations")
# Same paginate dependency is reused here - no duplicated skip/limit parsing logic
def list_conversations_controller(pagination: dict = Depends(paginate)):
    skip, limit = pagination["skip"], pagination["limit"]  # Unpack the injected pagination values
    return conversations[skip: skip + limit]  # Slice the conversations list according to skip/limit

# Register a GET endpoint at "/" that serves an HTML home page
@app.get("/")
def home_page(request: Request):
    # Renders templates/index.html, passing the request object (required by Jinja2Templates)
    return templates.TemplateResponse(request, "index.html")


# ------------------------------------------------------------------
# THEORY: Reducing Duplication with Shared Dependencies
# ------------------------------------------------------------------
#
# 1. The problem: repeated logic across endpoints
#    Both `/messages` and `/conversations` need the same "skip/limit"
#    pagination parameters parsed from the query string. Without
#    dependency injection, you'd duplicate that parameter-parsing logic
#    (and any validation/defaults) in every endpoint that needs pagination.
#
# 2. The solution: a shared dependency function
#    `paginate(skip: int = 0, limit: int = 10)` is a plain function that
#    declares the query parameters it needs, with defaults. Because it's
#    just a function (not a generator here, no yield/cleanup needed), it
#    simply returns a value directly.
#
# 3. Reuse via Depends()
#    `Depends(paginate)` is used in multiple path operations. FastAPI calls
#    `paginate()` for each request, extracting `skip`/`limit` from the query
#    string automatically, and injects the returned dict as `pagination`.
#    This means the pagination logic is written once and reused everywhere.
#
# 4. Benefits of this pattern
#    - DRY (Don't Repeat Yourself): one place to change pagination
#      behavior (e.g., add a max limit) that affects every endpoint using it.
#    - Consistency: every paginated endpoint behaves identically.
#    - Discoverability: FastAPI's auto-generated docs show `skip`/`limit`
#      as query parameters on every endpoint that depends on `paginate`.
#
# In short: Dependencies aren't just for things like database sessions -
# any reusable piece of "parse this input / compute this value" logic can
# be extracted into a dependency function and shared across multiple routes.
