from signal_bot.backend.core.config import get_settings

settings = get_settings()

def get_google_config():
    return {
	    "web": {
		    "client_id": settings.GOOGLE.CLIENT_ID,
		    "project_id": "signal-bot-368420",
		    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
		    "token_uri": "https://oauth2.googleapis.com/token",
		    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		    "client_secret": settings.GOOGLE.CLIENT_SECRET,
		    "redirect_uris": [
			    "http://127.0.0.1:8000"
		    ]
	    }
    }