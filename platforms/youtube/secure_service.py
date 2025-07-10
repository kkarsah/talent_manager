# platforms/youtube/secure_service.py
"""
Secure YouTube Service - Environment Variable Based
No credentials stored in files
"""

import os
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from dotenv import set_key

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# OAuth 2.0 scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]


class SecureYouTubeService:
    """Secure YouTube API integration using environment variables only"""

    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "YouTube API credentials not configured. "
                "Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET in environment."
            )

        self.service = None
        self.credentials = None

    def load_credentials_from_env(self) -> Optional[Credentials]:
        """Load credentials from environment variables"""
        token = os.getenv("YOUTUBE_ACCESS_TOKEN")
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
        token_expiry = os.getenv("YOUTUBE_TOKEN_EXPIRY")

        if not token or not refresh_token:
            logger.info("No YouTube credentials found in environment")
            return None

        # Parse expiry
        expiry = None
        if token_expiry:
            try:
                expiry = datetime.fromisoformat(token_expiry.replace("Z", "+00:00"))
            except ValueError:
                logger.warning("Invalid token expiry format, ignoring")

        credentials = Credentials(
            token=token,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            expiry=expiry,
        )

        return credentials

    def save_credentials_to_env(
        self, credentials: Credentials, persist_to_file: bool = True
    ):
        """Save credentials to environment variables and optionally .env file"""
        # Update current environment
        os.environ["YOUTUBE_ACCESS_TOKEN"] = credentials.token
        os.environ["YOUTUBE_REFRESH_TOKEN"] = credentials.refresh_token
        if credentials.expiry:
            os.environ["YOUTUBE_TOKEN_EXPIRY"] = credentials.expiry.isoformat()

        # Optionally persist to .env file for next session
        if persist_to_file:
            try:
                set_key(".env", "YOUTUBE_ACCESS_TOKEN", credentials.token)
                set_key(".env", "YOUTUBE_REFRESH_TOKEN", credentials.refresh_token)
                if credentials.expiry:
                    set_key(
                        ".env", "YOUTUBE_TOKEN_EXPIRY", credentials.expiry.isoformat()
                    )
                logger.info("Credentials saved to .env file")
            except Exception as e:
                logger.warning(f"Could not save to .env file: {e}")

    async def load_credentials(self) -> bool:
        """Load and refresh credentials if needed"""
        try:
            credentials = self.load_credentials_from_env()
            if not credentials:
                return False

            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                logger.info("Refreshing expired credentials")
                credentials.refresh(Request())
                # Save refreshed credentials
                self.save_credentials_to_env(credentials)

            self.credentials = credentials
            self.service = build("youtube", "v3", credentials=credentials)

            logger.info("YouTube credentials loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if YouTube is authenticated"""
        return self.service is not None and self.credentials is not None

    async def authenticate_desktop(self) -> str:
        """Desktop application OAuth flow"""
        try:
            # Create client config for desktop app
            client_config = {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                }
            }

            # Create flow
            flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

            # Generate authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type="offline", include_granted_scopes="true"
            )

            print(f"\n🔗 Please visit this URL to authorize the application:")
            print(f"{authorization_url}")
            print(
                f"\nAfter authorization, you'll see an authorization code on the page."
            )

            # Get authorization code from user
            authorization_code = input("\nEnter the authorization code: ").strip()

            # Exchange code for credentials
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials

            # Save credentials securely
            self.save_credentials_to_env(credentials)

            # Build service
            self.service = build("youtube", "v3", credentials=credentials)
            self.credentials = credentials

            logger.info("YouTube authentication successful")
            return "✅ Authentication successful!"

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return f"❌ Authentication failed: {e}"

    async def authenticate_local_server(self) -> str:
        """Local server OAuth flow (opens browser automatically)"""
        try:
            # Create client config
            client_config = {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080"],
                }
            }

            # Create flow
            flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

            print("🌐 Opening browser for authentication...")
            print("If browser doesn't open, visit the URL that will be displayed.")

            # Run local server (this opens browser automatically)
            credentials = flow.run_local_server(
                port=8080, open_browser=True, prompt="select_account"
            )

            # Save credentials securely
            self.save_credentials_to_env(credentials)

            # Build service
            self.service = build("youtube", "v3", credentials=credentials)
            self.credentials = credentials

            logger.info("YouTube authentication successful")
            return "✅ Authentication successful!"

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return f"❌ Authentication failed: {e}"

    async def authenticate(self) -> str:
        """Main authentication method - tries local server first, falls back to desktop"""
        try:
            # Try local server flow first (more user-friendly)
            return await self.authenticate_local_server()
        except Exception as e:
            logger.warning(f"Local server auth failed: {e}")
            logger.info("Falling back to desktop authentication")
            return await self.authenticate_desktop()

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        category_id: str = "27",  # Education
        privacy_status: str = "public",
        thumbnail_path: Optional[str] = None,
    ) -> Optional[str]:
        """Upload video to YouTube"""

        if not self.service:
            if not await self.load_credentials():
                raise RuntimeError(
                    "YouTube not authenticated. Run authentication first."
                )

        try:
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": privacy_status},
            }

            # Upload video
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

            request = self.service.videos().insert(
                part=",".join(body.keys()), body=body, media_body=media
            )

            response = None
            error = None
            retry = 0
            max_retries = 3

            while response is None and retry < max_retries:
                try:
                    status, response = request.next_chunk()
                    if response is not None:
                        if "id" in response:
                            video_id = response["id"]
                            logger.info(f"Video uploaded successfully: {video_id}")

                            # Upload thumbnail if provided
                            if thumbnail_path and os.path.exists(thumbnail_path):
                                await self._upload_thumbnail(video_id, thumbnail_path)

                            return video_id
                        else:
                            logger.error(f"Upload failed: {response}")
                            return None
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        retry += 1
                        logger.warning(f"Recoverable error, retrying: {e}")
                    else:
                        raise e

            return None

        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            return None

    async def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload thumbnail for video"""
        try:
            request = self.service.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(thumbnail_path)
            )
            request.execute()
            logger.info(f"Thumbnail uploaded for video {video_id}")
        except Exception as e:
            logger.warning(f"Thumbnail upload failed: {e}")

    async def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the authenticated channel"""
        if not self.service:
            if not await self.load_credentials():
                return None

        try:
            request = self.service.channels().list(part="snippet,statistics", mine=True)
            response = request.execute()

            if response["items"]:
                channel = response["items"][0]
                return {
                    "id": channel["id"],
                    "title": channel["snippet"]["title"],
                    "description": channel["snippet"]["description"],
                    "subscriber_count": int(
                        channel["statistics"].get("subscriberCount", 0)
                    ),
                    "video_count": int(channel["statistics"].get("videoCount", 0)),
                    "view_count": int(channel["statistics"].get("viewCount", 0)),
                }
            return None

        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return None

    async def get_video_analytics(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific video"""
        if not self.service:
            if not await self.load_credentials():
                return None

        try:
            request = self.service.videos().list(part="snippet,statistics", id=video_id)
            response = request.execute()

            if response["items"]:
                video = response["items"][0]
                stats = video["statistics"]
                return {
                    "video_id": video_id,
                    "title": video["snippet"]["title"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "published_at": video["snippet"]["publishedAt"],
                }
            return None

        except Exception as e:
            logger.error(f"Failed to get video analytics: {e}")
            return None

    def clear_credentials(self):
        """Clear credentials from environment (for security)"""
        # Clear from current environment
        env_vars = [
            "YOUTUBE_ACCESS_TOKEN",
            "YOUTUBE_REFRESH_TOKEN",
            "YOUTUBE_TOKEN_EXPIRY",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

        # Clear service
        self.service = None
        self.credentials = None

        logger.info("YouTube credentials cleared from environment")

    def get_security_status(self) -> Dict[str, Any]:
        """Get security status of credential storage"""
        return {
            "credentials_in_environment": bool(os.getenv("YOUTUBE_ACCESS_TOKEN")),
            "credentials_file_exists": False,  # We don't use files
            "service_authenticated": self.is_authenticated(),
            "storage_method": "environment_variables",
            "security_level": "high",
        }
