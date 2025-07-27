import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define what permissions we need from YouTube API
SCOPES = ['https://www.googleapis.com/auth/youtube']

def authenticate_youtube():
    """
    Handles YouTube API authentication using OAuth2
    Returns: authenticated YouTube service object
    """
    creds = None

    # Check if we already have saved credentials
    if os.path.exists('token.json') and os.path.getsize('token.json') > 0:
        # Load existing credentials from file
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Try to refresh expired creditnails
            creds.refresh(Request())
        else:
            # Start OAuth flow - opens browser for user to authorize
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Create and return YouTube API service object
    return build('youtube', 'v3', credentials=creds)

# Test authentication when script runs directly
if __name__ == "__main__":
    youtube = authenticate_youtube()
    print("YouTube API connected successfully!")

    # How to verify this works:
    # 1. Run the script - browser should open asking for Google account login
    # 2. After authorization, you should see success message
    # 3. Check that 'token.json' file was created in your project folder
    # 4. Run script again - should connect without opening browser (using saved token)