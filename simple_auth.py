# simple_auth.py - Simple YouTube authentication script

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# OAuth 2.0 scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def create_credentials_json():
    """Create a credentials JSON file from environment variables"""
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Missing YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET in .env file")
        return None

    # Create credentials directory
    creds_dir = Path("credentials")
    creds_dir.mkdir(exist_ok=True)

    # Create client secrets file
    client_secrets = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"],
        }
    }

    secrets_file = creds_dir / "client_secrets.json"
    with open(secrets_file, "w") as f:
        json.dump(client_secrets, f, indent=2)

    print(f"✅ Created {secrets_file}")
    return str(secrets_file)


def authenticate_youtube():
    """Authenticate with YouTube using the simplest method"""
    try:
        # Create credentials file
        secrets_file = create_credentials_json()
        if not secrets_file:
            return None

        print("🔑 Starting YouTube authentication...")
        print("📱 This will open your browser automatically")
        print("🔐 Please authorize the application when prompted")

        # Create flow from client secrets
        flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)

        # Run local server - this handles everything automatically
        credentials = flow.run_local_server(
            port=8080, prompt="select_account", open_browser=True
        )

        # Save credentials for future use
        creds_file = Path("credentials/youtube_credentials.json")
        with open(creds_file, "w") as f:
            f.write(credentials.to_json())

        print("✅ Authentication successful!")
        print(f"💾 Credentials saved to {creds_file}")

        # Test the connection
        youtube = build("youtube", "v3", credentials=credentials)

        # Get channel info to verify
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()

        if response["items"]:
            channel = response["items"][0]
            snippet = channel["snippet"]
            stats = channel["statistics"]

            print("\n📺 Channel Information:")
            print(f"   Name: {snippet['title']}")
            print(f"   Subscribers: {int(stats.get('subscriberCount', 0)):,}")
            print(f"   Videos: {int(stats.get('videoCount', 0)):,}")
            print(f"   Total Views: {int(stats.get('viewCount', 0)):,}")

            return True
        else:
            print("⚠️ Authenticated but no channel found")
            return False

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 YouTube Authentication Setup")
    print("=" * 40)

    # Check if already authenticated
    creds_file = Path("credentials/youtube_credentials.json")
    if creds_file.exists():
        print(f"✅ Credentials file exists: {creds_file}")

        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            # Load and test existing credentials
            credentials = Credentials.from_authorized_user_file(str(creds_file), SCOPES)

            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Save refreshed credentials
                with open(creds_file, "w") as f:
                    f.write(credentials.to_json())
                print("🔄 Refreshed expired credentials")

            # Test connection
            youtube = build("youtube", "v3", credentials=credentials)
            request = youtube.channels().list(part="snippet", mine=True)
            response = request.execute()

            if response["items"]:
                channel_name = response["items"][0]["snippet"]["title"]
                print(f"✅ Already authenticated for channel: {channel_name}")
                print("🎉 You're ready to upload videos!")
            else:
                print("⚠️ Credentials exist but channel access failed")
                print("🔄 Re-authenticating...")
                authenticate_youtube()

        except Exception as e:
            print(f"⚠️ Existing credentials invalid: {e}")
            print("🔄 Re-authenticating...")
            authenticate_youtube()
    else:
        print("🔑 No existing credentials found")
        print("🔄 Starting authentication...")
        authenticate_youtube()
