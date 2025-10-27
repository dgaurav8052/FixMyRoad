from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import traceback
import logging
import os
import jwt
from datetime import datetime, timedelta
import app.crud as crud

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# CORS middleware (allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Logic ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT Secret not configured on the server",
        )

    try:
        # Debug: Let's see what we're working with
        print(f"JWT Secret length: {len(SUPABASE_JWT_SECRET) if SUPABASE_JWT_SECRET else 'None'}")
        print(f"JWT Secret starts with: {SUPABASE_JWT_SECRET[:10] if SUPABASE_JWT_SECRET else 'None'}...")
        print(f"Token starts with: {token[:20] if token else 'None'}...")
        
        # Supabase JWT tokens have audience validation, let's skip it for now
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}  # Skip audience verification
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except jwt.PyJWTError as e:
        print(f"JWT decode error: {e}")
        raise credentials_exception
        
    return payload
# --- End of Authentication Logic ---

# Mount static files at /static
app.mount(
    "/static",
    StaticFiles(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Frontend")), html=True),
    name="static",
)

# Serve home page at root
@app.get("/", response_class=FileResponse)
def serve_home():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Frontend/home.html"))

# Serve form page at /form.html
@app.get("/form.html", response_class=FileResponse)
def serve_form():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Frontend/form.html"))

# Serve thankyou page
@app.get("/thankyou.html", response_class=FileResponse)
def serve_thankyou():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Frontend/thankyou.html"))

# Form submission endpoint
@app.post("/submit-report/")
async def submit_report(
    name: str = Form(...),
    email: str = Form(None),
    issue_type: str = Form(None, alias="issue-type"),
    description: str = Form(None),
    location: str = Form(None),
    files: list[UploadFile] = File([])
):
    try:
        report = await crud.create_report(
            name=name,
            contact_details=email,
            issue_category=issue_type,
            discription=description,
            manual_location_input=location,
            files=files
        )
    except Exception as e:
        logging.error("Form submission failed: %s", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
    return RedirectResponse(url=f"/thankyou.html?rid={report['report_id']}", status_code=303)

# --- Admin Routes ---
@app.get("/AdminLogin.html", response_class=FileResponse)
def serve_admin_login():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Frontend/AdminLogin.html"))

@app.get("/AdminDashBoard.html", response_class=FileResponse)
def serve_admin_dashboard():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Frontend/AdminDashBoard.html"))

# Protected API endpoint for the admin dashboard
@app.get("/api/admin/reports")
async def get_admin_reports(current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("email")
    return {
        "message": "Successfully accessed protected admin data.",
        "admin_user_email": user_email,
    }

# Debug endpoint to test JWT without authentication
@app.get("/api/debug/jwt-info")
async def debug_jwt_info():
    return {
        "jwt_secret_configured": SUPABASE_JWT_SECRET is not None,
        "jwt_secret_length": len(SUPABASE_JWT_SECRET) if SUPABASE_JWT_SECRET else 0,
        "jwt_secret_preview": SUPABASE_JWT_SECRET[:10] + "..." if SUPABASE_JWT_SECRET else None,
    }

