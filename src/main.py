import logging
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .gemini_routes import router as gemini_router
from .openai_routes import router as openai_router
from .auth import get_credentials, get_user_project_id, onboard_user

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Environment variables loaded from .env file")
except ImportError:
    logging.warning("python-dotenv not installed, .env file will not be loaded automatically")
except Exception as e:
    logging.warning(f"Could not load .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Add CORS middleware for preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
async def startup_event():
    try:
        logging.info("Starting Gemini Chat Playground...")
        
        # Check if credentials exist
        import os
        from .config import CREDENTIAL_FILE
        
        env_creds_json = os.getenv("GEMINI_CREDENTIALS")
        creds_file_exists = os.path.exists(CREDENTIAL_FILE)
        
        if env_creds_json or creds_file_exists:
            try:
                # Try to load existing credentials without OAuth flow first
                creds = get_credentials(allow_oauth_flow=False)
                if creds:
                    try:
                        proj_id = get_user_project_id(creds)
                        if proj_id:
                            onboard_user(creds, proj_id)
                            logging.info(f"Successfully onboarded with project ID: {proj_id}")
                        logging.info("Gemini Chat Playground started successfully")
                        logging.info("Authentication required - Password: see .env file")
                    except Exception as e:
                        logging.error(f"Setup failed: {str(e)}")
                        logging.warning("Server started but may not function properly until setup issues are resolved.")
                else:
                    logging.warning("Credentials file exists but could not be loaded. Server started - authentication will be required on first request.")
            except Exception as e:
                logging.error(f"Credential loading error: {str(e)}")
                logging.warning("Server started but credentials need to be set up.")
        else:
            # No credentials found - prompt user to authenticate
            logging.info("No credentials found. Starting OAuth authentication flow...")
            try:
                creds = get_credentials(allow_oauth_flow=True)
                if creds:
                    try:
                        proj_id = get_user_project_id(creds)
                        if proj_id:
                            onboard_user(creds, proj_id)
                            logging.info(f"Successfully onboarded with project ID: {proj_id}")
                        logging.info("Gemini Chat Playground started successfully")
                    except Exception as e:
                        logging.error(f"Setup failed: {str(e)}")
                        logging.warning("Server started but may not function properly until setup issues are resolved.")
                else:
                    logging.error("Authentication failed. Server started but will not function until credentials are provided.")
            except Exception as e:
                logging.error(f"Authentication error: {str(e)}")
                logging.warning("Server started but authentication failed.")
        
        logging.info("Authentication required - Password: see .env file")
        
    except Exception as e:
        logging.error(f"Startup error: {str(e)}")
        logging.warning("Server may not function properly.")

@app.options("/{full_path:path}")
async def handle_preflight(request: Request, full_path: str):
    """Handle CORS preflight requests without authentication."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Root interface - no authentication required
@app.get("/")
async def root():
    """
    Root interface providing project information.
    No authentication required.
    """
    return {
        "name": "gemini-chat-playground",
        "description": "Gemini AI Chat Playground with OpenAI-compatible and native Gemini chat interfaces",
        "purpose": "Provides both OpenAI-compatible chat interfaces (/v1/chat/completions) and native Gemini chat interfaces for exploring Gemini models",
        "version": "1.0.0",
        "interfaces": {
            "openai_compatible": {
                "chat_completions": "/v1/chat/completions",
                "models": "/v1/models"
            },
            "native_gemini": {
                "models": "/v1beta/models",
                "generate": "/v1beta/models/{model}/generateContent",
                "stream": "/v1beta/models/{model}/streamGenerateContent"
            },
            "health": "/health"
        },
        "authentication": "Required for all interfaces except root and health",
        "repository": "https://github.com/user/gemini-chat-playground"
    }

# Health check interface for Docker/Hugging Face
@app.get("/health")
async def health_check():
    """Health check interface for container orchestration."""
    return {"status": "healthy", "service": "gemini-chat-playground"}

app.include_router(openai_router)
app.include_router(gemini_router)