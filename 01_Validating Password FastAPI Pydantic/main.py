# Path is used to build filesystem paths in an OS-independent way
from pathlib import Path

# BaseModel is the base class for defining request/response schemas
# field_validator lets us attach custom validation logic to a specific field
from pydantic import BaseModel, field_validator
# FastAPI is the app class; Request represents an incoming HTTP request
from fastapi import FastAPI, Request
# Jinja2Templates lets FastAPI render HTML templates using the Jinja2 engine
from fastapi.templating import Jinja2Templates

# Resolve the directory this file lives in, so template paths work regardless of cwd
BASE_DIR = Path(__file__).resolve().parent
# Configure Jinja2 to look for templates inside a "templates" folder next to this file
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Pydantic model describing the expected shape of a "create user" request body
class UserCreate(BaseModel):
    username: str  # Must be a string
    password: str  # Must be a string

    # This validator runs automatically whenever a UserCreate is constructed
    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')  # Enforce minimum length
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one digit')  # Require at least one digit
        if not any(char.isupper() for char in value):
            raise ValueError('Password must contain at least one uppercase letter')  # Require at least one uppercase letter
        return value  # Return the (valid) value so it gets assigned to the field

# Create the FastAPI application instance
app = FastAPI()

# Register a GET endpoint at "/" that serves an HTML signup form
@app.get("/")
async def signup_form(request: Request):
    # Renders templates/index.html, passing the request object (required by Jinja2Templates)
    return templates.TemplateResponse(request, "index.html")

# Register a POST endpoint at "/users" for creating a new user
@app.post("/users")
# FastAPI parses the JSON request body into a UserCreate instance, running validation automatically
async def create_user_controller(user: UserCreate):
    return {"username": user.username, "message": "Account Successfully Created!"}


# ------------------------------------------------------------------
# THEORY: Pydantic Validation + Request Bodies in FastAPI
# ------------------------------------------------------------------
#
# 1. Pydantic models as schemas
#    A class inheriting from `BaseModel` defines the expected structure and
#    types of data. FastAPI uses this to automatically parse, validate, and
#    document (via OpenAPI/Swagger) request bodies.
#
# 2. Request body parameters
#    When a path operation function has a parameter typed as a Pydantic
#    model (e.g. `user: UserCreate`), FastAPI knows to read the incoming
#    request body as JSON and construct that model from it - no manual
#    parsing required.
#
# 3. Automatic validation and error responses
#    If the incoming data doesn't match the model (wrong types, missing
#    fields, or a failing custom validator), FastAPI automatically returns
#    a 422 Unprocessable Entity response with details about what failed -
#    you don't have to write that error-handling logic yourself.
#
# 4. Custom field validators (@field_validator)
#    Beyond basic type checking, you can attach custom business rules to a
#    field (e.g. password complexity rules). Raising a `ValueError` inside
#    a validator causes Pydantic (and therefore FastAPI) to treat the input
#    as invalid.
#
# 5. Server-side HTML rendering with Jinja2Templates
#    FastAPI isn't limited to JSON APIs - `Jinja2Templates` lets a path
#    operation return rendered HTML pages, mixing traditional server-side
#    rendering with API endpoints in the same application.
#
# In short: Pydantic models let FastAPI validate and document your API's
# input/output "shape" declaratively, catching bad data before it ever
# reaches your business logic.
