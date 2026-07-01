# Import FastAPI class to create the app, and Depends to declare dependencies
from fastapi import FastAPI, Depends

# This is a "dependency" function - FastAPI will call it for us and inject its result
def get_db():
    db = ... # Create a Database Session (placeholder - would normally open a real DB connection/session)
    try:
        yield db  # Hand the db session over to the path operation function that needs it
    finally:
        db.close()  # After the request is done (even if it raised an error), close the db session

# Create the FastAPI application instance - this is the main entry point of the app
app = FastAPI()

# Register a GET endpoint at /users/{email}/messages
@app.get("/users/{email}/messages")
# email is a path parameter taken from the URL
# db = Depends(get_db) tells FastAPI to call get_db() and inject its yielded value as `db`
def get_current_user_message(email, db = Depends(get_db)):
    user = db.query(...) # db is reused - same session/connection used here...
    messages = db.query(...) # db is reused - ...and reused again here, without creating a new one
    return messages  # FastAPI automatically converts the return value to a JSON response


# ------------------------------------------------------------------
# THEORY: Dependency Injection (DI) in FastAPI
# ------------------------------------------------------------------
#
# 1. What is Dependency Injection?
#    Dependency Injection is a design pattern where an object (or function)
#    receives the things it needs ("dependencies") from an external source,
#    rather than creating them itself. This decouples "what a function needs"
#    from "how that thing is created."
#
# 2. How FastAPI implements it: Depends()
#    - `Depends(get_db)` tells FastAPI: "before running this path operation
#      function, call `get_db()` and pass its result as the `db` argument."
#    - FastAPI manages calling the dependency, handling its return value,
#      and cleaning it up afterward - the endpoint function just uses `db`.
#
# 3. Why use generator-based dependencies (yield instead of return)?
#    - Code before `yield` runs BEFORE the endpoint function executes
#      (setup phase, e.g., opening a DB session).
#    - The yielded value (`db`) is what gets injected into the endpoint.
#    - Code after `yield` (inside `finally`) runs AFTER the endpoint
#      function finishes - even if an exception occurred - making it perfect
#      for cleanup (closing connections, releasing resources).
#    - This mirrors a try/finally context manager pattern.
#
# 4. Why is this useful?
#    - Reusability: `get_db` can be reused across many endpoints without
#      duplicating session-creation/cleanup logic.
#    - Testability: In tests, you can override the dependency
#      (app.dependency_overrides[get_db] = fake_get_db) to inject a mock
#      database, without touching the endpoint code at all.
#    - Separation of concerns: The endpoint focuses on business logic
#      (querying data), while dependency functions handle infrastructure
#      concerns (DB connections, auth, config, etc.).
#    - Automatic resource management: Guarantees cleanup happens exactly
#      once per request, regardless of success or failure.
#
# 5. Common use cases for Depends() beyond DB sessions:
#    - Authentication/authorization (e.g., get_current_user)
#    - Shared query parameters/pagination logic
#    - Rate limiting or permission checks
#    - Configuration/settings injection
#
# In short: Dependency Injection lets FastAPI supply ready-to-use resources
# to your route functions, while centralizing setup/teardown logic in one
# reusable place instead of repeating it in every endpoint.
