# FastAPI is the app class; status provides named HTTP status code constants
from fastapi import FastAPI, status
# RedirectResponse sends the client an HTTP redirect instead of normal content
from fastapi.responses import RedirectResponse

# Create the FastAPI application instance
app = FastAPI()

# Register a GET endpoint at the root path "/"
# include_in_schema=False hides this route from the auto-generated OpenAPI docs
@app.get("/", include_in_schema = False)
def docs_redirect_controller():
    # Redirect any visitor of "/" to FastAPI's auto-generated "/docs" (Swagger UI) page
    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)


# ------------------------------------------------------------------
# THEORY: Redirects and Auto-Generated Docs in FastAPI
# ------------------------------------------------------------------
#
# 1. RedirectResponse
#    Instead of returning JSON or HTML, a path operation can return a
#    `RedirectResponse`, which sends an HTTP redirect (3xx status code) and
#    a `Location` header telling the client's browser to navigate elsewhere.
#
# 2. HTTP status codes for redirects
#    `status.HTTP_303_SEE_OTHER` tells the browser "the resource you asked
#    for can be found at a different URL, fetch it with GET." FastAPI's
#    `status` module provides readable names for these numeric codes
#    instead of hardcoding "303" directly.
#
# 3. Auto-generated interactive docs
#    FastAPI automatically builds interactive API documentation (Swagger UI
#    at "/docs" and ReDoc at "/redoc") from your path operations and
#    Pydantic models - no extra work required. This endpoint simply makes
#    "/docs" the default landing page by redirecting "/" there.
#
# 4. include_in_schema=False
#    This flag excludes a specific route from the generated OpenAPI schema
#    (and therefore from "/docs" and "/redoc"). It's useful for internal or
#    utility endpoints (like this redirect) that shouldn't be listed as
#    part of the public API surface.
#
# In short: FastAPI gives you free, always up-to-date interactive API docs,
# and simple response types like RedirectResponse let you control exactly
# how the client's browser should behave beyond just returning data.
