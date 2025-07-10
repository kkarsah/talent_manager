#!/usr/bin/env python3
"""
Secure YouTube Authentication Script
Stores credentials in environment variables only
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv, set_key
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


def validate_environment():
    """Validate required environment variables"""
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Missing YouTube credentials in .env file")
        print("\n📋 Required environment variables:")
        print("   YOUTUBE_CLIENT_ID=your-client-id")
        print("   YOUTUBE_CLIENT_SECRET=your-client-secret")
        print("\n🔧 Get these from Google Cloud Console:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Enable YouTube Data API v3")
        print("   3. Create OAuth 2.0 credentials (Desktop application)")
        return False

    print("✅ Environment variables found")
    return True


def check_existing_credentials():
    """Check if valid credentials already exist"""
    token = os.getenv("YOUTUBE_ACCESS_TOKEN")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not token or not refresh_token:
        return False

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        # Create credentials object
        credentials = Credentials(
            token=token,
            refresh_token=refresh_token,
            client_id=os.getenv("YOUTUBE_CLIENT_ID"),
            client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            token_uri="https://oauth2.googleapis.com/token",
        )

        # Test credentials
        if credentials.expired and credentials.refresh_token:
            print("🔄 Refreshing expired credentials...")
            credentials.refresh(Request())

            # Save refreshed credentials
            save_credentials_to_env(credentials)
            print("✅ Credentials refreshed successfully")

        # Test API call
        youtube = build("youtube", "v3", credentials=credentials)
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()

        if response["items"]:
            channel = response["items"][0]
            snippet = channel["snippet"]
            stats = channel["statistics"]

            print("✅ Existing credentials are valid!")
            print(f"\n📺 Channel Information:")
            print(f"   Name: {snippet['title']}")
            print(f"   Subscribers: {int(stats.get('subscriberCount', 0)):,}")
            print(f"   Videos: {int(stats.get('videoCount', 0)):,}")
            print(f"   Total Views: {int(stats.get('viewCount', 0)):,}")
            return True
        else:
            print("⚠️ Credentials valid but no channel found")
            return False

    except Exception as e:
        print(f"⚠️ Existing credentials invalid: {e}")
        return False


def save_credentials_to_env(credentials, update_env_file=True):
    """Save credentials to environment and .env file"""
    # Update current environment
    os.environ["YOUTUBE_ACCESS_TOKEN"] = credentials.token
    os.environ["YOUTUBE_REFRESH_TOKEN"] = credentials.refresh_token
    if credentials.expiry:
        os.environ["YOUTUBE_TOKEN_EXPIRY"] = credentials.expiry.isoformat()

    # Update .env file for persistence
    if update_env_file:
        try:
            set_key(".env", "YOUTUBE_ACCESS_TOKEN", credentials.token)
            set_key(".env", "YOUTUBE_REFRESH_TOKEN", credentials.refresh_token)
            if credentials.expiry:
                set_key(".env", "YOUTUBE_TOKEN_EXPIRY", credentials.expiry.isoformat())
            print("💾 Credentials saved to .env file")
        except Exception as e:
            print(f"⚠️ Could not save to .env file: {e}")


def authenticate_youtube():
    """Authenticate with YouTube using secure method"""
    try:
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

        # Create client config for desktop app
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["http://localhost:8080"],
            }
        }

        print("🔑 Starting YouTube authentication...")
        print("📱 This will open your browser automatically")
        print("🔐 Please authorize the application when prompted")

        # Create flow from client config
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

        try:
            # Try local server flow first (more user-friendly)
            print("🌐 Opening browser for authentication...")
            credentials = flow.run_local_server(
                port=8080, prompt="select_account", open_browser=True
            )
        except Exception as e:
            print(f"⚠️ Browser authentication failed: {e}")
            print("🔄 Falling back to manual code entry...")

            # Fallback to manual code entry
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            authorization_url, _ = flow.authorization_url(
                access_type="offline", include_granted_scopes="true"
            )

            print(f"\n🔗 Please visit this URL:")
            print(f"{authorization_url}")
            print(f"\nAfter authorization, copy the code from the page.")

            authorization_code = input("\nEnter the authorization code: ").strip()
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials

        # Save credentials securely (no files!)
        save_credentials_to_env(credentials)

        print("✅ Authentication successful!")

        # Test the connection
        youtube = build("youtube", "v3", credentials=credentials)

        # Get channel info to verify
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()

        if response["items"]:
            channel = response["items"][0]
            snippet = channel["snippet"]
            stats = channel["statistics"]

            print(f"\n📺 Channel Information:")
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


def clear_credentials():
    """Clear stored credentials for security"""
    env_vars = ["YOUTUBE_ACCESS_TOKEN", "YOUTUBE_REFRESH_TOKEN", "YOUTUBE_TOKEN_EXPIRY"]

    # Clear from current environment
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    # Remove from .env file
    try:
        from dotenv import unset_key

        for var in env_vars:
            unset_key(".env", var)
        print("🧹 Credentials cleared from environment and .env file")
    except Exception as e:
        print(f"⚠️ Could not clear .env file: {e}")


def security_check():
    """Perform security checks"""
    print("🔍 Security Check...")

    issues = []

    # Check for credential files that shouldn't exist
    credential_files = [
        "credentials/youtube_credentials.json",
        "client_secrets.json",
        "credentials/client_secrets.json",
        "youtube_credentials.json",
    ]

    for file_path in credential_files:
        if Path(file_path).exists():
            issues.append(f"Found credential file: {file_path}")

    # Check .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            gitignore_content = f.read()
            if ".env" not in gitignore_content:
                issues.append(".env not in .gitignore")
            if "credentials/" not in gitignore_content:
                issues.append("credentials/ not in .gitignore")
    else:
        issues.append("No .gitignore file found")

    if issues:
        print("⚠️ Security Issues Found:")
        for issue in issues:
            print(f"   - {issue}")

        print("\n🔧 Recommended fixes:")
        print("   1. Add .env and credentials/ to .gitignore")
        print("   2. Remove any credential files")
        print("   3. Use environment variables only")

        return False
    else:
        print("✅ No security issues found")
        return True


def main():
    """Main authentication flow"""
    print("🔐 Secure YouTube Authentication")
    print("=" * 40)
    print("🛡️ This script uses environment variables only - no credential files!")
    print()

    # Step 1: Security check
    print("1️⃣ Running security check...")
    security_check()
    print()

    # Step 2: Validate environment
    print("2️⃣ Checking environment setup...")
    if not validate_environment():
        return False
    print()

    # Step 3: Check existing credentials
    print("3️⃣ Checking existing credentials...")
    if check_existing_credentials():
        print("🎉 Authentication already complete!")
        print("💡 You can now run: python cli.py alex generate --upload")
        return True
    print()

    # Step 4: Authenticate
    print("4️⃣ Starting authentication...")
    if authenticate_youtube():
        print("\n🎉 Setup complete!")
        print("🔐 Credentials stored securely in environment variables")
        print("💡 Try: python cli.py alex generate --topic 'AI Future' --upload")
        return True
    else:
        print("\n❌ Authentication failed")
        return False


def interactive_menu():
    """Interactive menu for credential management"""
    while True:
        print("\n🔐 YouTube Credential Manager")
        print("=" * 30)
        print("1. 🔑 Authenticate")
        print("2. 📊 Check Status")
        print("3. 🔄 Refresh Credentials")
        print("4. 🧹 Clear Credentials")
        print("5. 🔍 Security Check")
        print("6. 🚪 Exit")

        choice = input("\nSelect an option (1-6): ").strip()

        if choice == "1":
            main()
        elif choice == "2":
            print("\n📊 Checking status...")
            if check_existing_credentials():
                print("✅ Credentials are valid and working")
            else:
                print("❌ No valid credentials found")
        elif choice == "3":
            print("\n🔄 Refreshing credentials...")
            if check_existing_credentials():
                print("✅ Credentials refreshed successfully")
            else:
                print("❌ No credentials to refresh")
        elif choice == "4":
            print("\n🧹 Clearing credentials...")
            clear_credentials()
        elif choice == "5":
            print("\n🔍 Running security check...")
            security_check()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    import sys

    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_menu()
    else:
        success = main()
        sys.exit(0 if success else 1)
