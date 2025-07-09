# platforms/youtube/service.py

import os
import logging
from typing import Dict, Optional, List, Any
from pathlib import Path
import json
from datetime import datetime

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


class YouTubeService:
    """YouTube API integration for video uploads and management"""

    def __init__(self):
        self.credentials_file_path = os.getenv(
            "YOUTUBE_CREDENTIALS_FILE", "credentials/youtube_credentials.json"
        )
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        
        # Support both desktop and web app flows
        self.auth_mode = os.getenv("YOUTUBE_AUTH_MODE", "desktop")  # desktop or web
        
        if self.auth_mode == "desktop":
            self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        else:
            self.redirect_uri = os.getenv(
                "YOUTUBE_REDIRECT_URI", "http://localhost:8000/auth/youtube/callback"
            )

        if not self.client_id or not self.client_secret:
            raise ValueError("YouTube API credentials not configured")

        self.service = None
        self.credentials = None
        self.credentials_file = Path("credentials/youtube_credentials.json")
        self.credentials_file.parent.mkdir(exist_ok=True)

    async def authenticate(self) -> str:
        """Main authentication method - chooses best flow based on auth_mode"""
        if self.auth_mode == "desktop":
            return await self.authenticate_desktop()
        else:
            return await self.authenticate_web()

    async def authenticate_desktop(self) -> str:
        """Desktop application OAuth flow - best for CLI"""
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
                access_type="offline", 
                include_granted_scopes="true"
            )

            print(f"\n🔗 Please visit this URL to authorize the application:")
            print(f"{authorization_url}")
            print(f"\nAfter authorization, you'll see an authorization code on the page.")
            
            # Get authorization code from user
            authorization_code = input("\nEnter the authorization code: ").strip()

            # Exchange code for credentials
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials

            # Save credentials
            await self._save_credentials(credentials)

            # Build service
            self.service = build("youtube", "v3", credentials=credentials)
            self.credentials = credentials

            logger.info("YouTube authentication successful")
            return "✅ Authentication successful!"

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return f"❌ Authentication failed: {e}"

    async def authenticate_web(self) -> str:
        """Web application OAuth flow - returns URL for manual process"""
        try:
            # Create client config for web app
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            }

            # Create flow
            flow = InstalledAppFlow.from_client_config(
                client_config, scopes=SCOPES, redirect_uri=self.redirect_uri
            )

            # Generate authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type="offline", include_granted_scopes="true"
            )

            # Store flow for callback
            self._current_flow = flow

            logger.info(f"Generated YouTube auth URL: {authorization_url}")
            return authorization_url

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return f"❌ Authentication failed: {e}"

    async def authenticate_local_server(self) -> str:
        """Alternative: Use local server for automatic flow (opens browser)"""
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
                port=8080, 
                open_browser=True,
                prompt="select_account"
            )

            # Save credentials
            await self._save_credentials(credentials)

            # Build service
            self.service = build("youtube", "v3", credentials=credentials)
            self.credentials = credentials

            logger.info("YouTube authentication successful")
            return "✅ Authentication successful!"

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return f"❌ Authentication failed: {e}"

    async def handle_callback(self, authorization_code: str) -> bool:
        """Handle OAuth callback for web flow"""
        try:
            if not hasattr(self, "_current_flow"):
                raise ValueError("No active OAuth flow found")

            # Exchange code for credentials
            self._current_flow.fetch_token(code=authorization_code)
            credentials = self._current_flow.credentials

            # Save credentials
            await self._save_credentials(credentials)

            # Build service
            self.service = build("youtube", "v3", credentials=credentials)
            self.credentials = credentials

            logger.info("YouTube authentication successful")
            return True

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False

    async def load_credentials(self) -> bool:
        """Load existing credentials from file"""
        try:
            if self.credentials_file.exists():
                credentials = Credentials.from_authorized_user_file(
                    str(self.credentials_file), SCOPES
                )

                # Refresh if expired
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    await self._save_credentials(credentials)

                self.credentials = credentials
                self.service = build("youtube", "v3", credentials=credentials)

                logger.info("YouTube credentials loaded successfully")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return False

    async def _save_credentials(self, credentials: Credentials):
        """Save credentials to file"""
        with open(self.credentials_file, "w") as f:
            f.write(credentials.to_json())
        logger.info(f"Credentials saved to {self.credentials_file}")

    def is_authenticated(self) -> bool:
        """Check if YouTube is authenticated"""
        return self.service is not None and self.credentials is not None

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
                    "YouTube not authenticated. Call authenticate() first."
                )

        try:
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id,
                    "defaultLanguage": "en",
                    "defaultAudioLanguage": "en",
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "embeddable": True,
                    "license": "youtube",
                    "publicStatsViewable": True,
                },
            }

            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=1024 * 1024,  # 1MB chunks
                resumable=True,
                mimetype="video/*",
            )

            # Start upload
            logger.info(f"Starting YouTube upload: {title}")
            print(f"📤 Uploading video: {title}")
            
            request = self.service.videos().insert(
                part=",".join(body.keys()), body=body, media_body=media
            )

            # Execute resumable upload with progress
            response = None
            error = None
            retry = 0

            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        print(f"📊 Upload progress: {progress}%")
                        logger.info(f"Upload progress: {progress}%")

                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retry on server errors
                        if retry < 3:
                            retry += 1
                            logger.warning(f"Upload error, retrying ({retry}/3): {e}")
                            print(f"⚠️ Upload error, retrying ({retry}/3)")
                            continue
                    raise

            if response:
                video_id = response["id"]
                video_url = f"https://youtube.com/watch?v={video_id}"
                logger.info(f"Upload successful! Video ID: {video_id}")
                print(f"✅ Upload successful!")
                print(f"🎥 Video URL: {video_url}")

                # Upload thumbnail if provided
                if thumbnail_path and Path(thumbnail_path).exists():
                    try:
                        await self.upload_thumbnail(video_id, thumbnail_path)
                        print(f"🖼️ Thumbnail uploaded successfully")
                    except Exception as e:
                        logger.warning(f"Thumbnail upload failed: {e}")
                        print(f"⚠️ Thumbnail upload failed: {e}")

                return video_id

            return None

        except HttpError as e:
            logger.error(f"YouTube upload failed: {e}")
            print(f"❌ Upload failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected upload error: {e}")
            print(f"❌ Unexpected error: {e}")
            return None

    async def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload thumbnail for a video"""
        try:
            media = MediaFileUpload(thumbnail_path, mimetype="image/*")
            
            request = self.service.thumbnails().set(
                videoId=video_id, media_body=media
            )
            
            response = request.execute()
            logger.info(f"Thumbnail uploaded for video {video_id}")
            return True

        except Exception as e:
            logger.error(f"Thumbnail upload failed: {e}")
            return False

    async def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the authenticated channel"""
        if not self.service:
            return None

        try:
            request = self.service.channels().list(
                part="snippet,statistics", mine=True
            )
            response = request.execute()

            if response["items"]:
                channel = response["items"][0]
                snippet = channel["snippet"]
                stats = channel["statistics"]

                return {
                    "id": channel["id"],
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "subscriber_count": int(stats.get("subscriberCount", 0)),
                    "video_count": int(stats.get("videoCount", 0)),
                    "view_count": int(stats.get("viewCount", 0)),
                    "thumbnail": snippet["thumbnails"]["medium"]["url"],
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return None

    async def list_recent_videos(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List recent videos from the channel"""
        if not self.service:
            return []

        try:
            # Get channel info first
            channel_info = await self.get_channel_info()
            if not channel_info:
                return []

            # Search for recent videos
            search_request = self.service.search().list(
                part="snippet",
                channelId=channel_info["id"],
                maxResults=max_results,
                order="date",
                type="video",
            )
            search_response = search_request.execute()

            # Get video statistics
            video_ids = [item["id"]["videoId"] for item in search_response["items"]]
            
            if not video_ids:
                return []

            videos_request = self.service.videos().list(
                part="snippet,statistics", id=",".join(video_ids)
            )
            videos_response = videos_request.execute()

            videos = []
            for video in videos_response["items"]:
                snippet = video["snippet"]
                stats = video["statistics"]

                videos.append(
                    {
                        "id": video["id"],
                        "title": snippet["title"],
                        "description": snippet["description"],
                        "published_at": snippet["publishedAt"],
                        "thumbnail": snippet["thumbnails"]["medium"]["url"],
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                    }
                )

            return videos

        except Exception as e:
            logger.error(f"Failed to list recent videos: {e}")
            return []

    async def get_video_stats(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific video"""
        if not self.service:
            return None

        try:
            request = self.service.videos().list(
                part="statistics,snippet", id=video_id
            )
            response = request.execute()

            if response["items"]:
                video = response["items"][0]
                snippet = video["snippet"]
                stats = video["statistics"]

                return {
                    "id": video_id,
                    "title": snippet["title"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "dislikes": int(stats.get("dislikeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "published_at": snippet["publishedAt"],
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get video stats: {e}")
            return None

    async def delete_video(self, video_id: str) -> bool:
        """Delete a video from YouTube"""
        if not self.service:
            return False

        try:
            request = self.service.videos().delete(id=video_id)
            request.execute()
            logger.info(f"Video {video_id} deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to delete video {video_id}: {e}")
            return False

    async def update_video(
        self, 
        video_id: str, 
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        privacy_status: Optional[str] = None
    ) -> bool:
        """Update video metadata"""
        if not self.service:
            return False

        try:
            # Get current video data
            request = self.service.videos().list(part="snippet,status", id=video_id)
            response = request.execute()

            if not response["items"]:
                logger.error(f"Video {video_id} not found")
                return False

            video = response["items"][0]
            snippet = video["snippet"]
            status = video["status"]

            # Update fields if provided
            if title:
                snippet["title"] = title
            if description:
                snippet["description"] = description
            if tags:
                snippet["tags"] = tags
            if privacy_status:
                status["privacyStatus"] = privacy_status

            # Update video
            update_request = self.service.videos().update(
                part="snippet,status",
                body={
                    "id": video_id,
                    "snippet": snippet,
                    "status": status
                }
            )
            update_request.execute()

            logger.info(f"Video {video_id} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update video {video_id}: {e}")
            return False

    # Authentication file method (alternative approach)
    async def authenticate_with_file(self) -> str:
        """Authenticate using credentials file (if you have client_secrets.json)"""
        try:
            credentials_path = Path(self.credentials_file_path)
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_file_path}"
                )

            # Create flow from credentials file
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )

            # Run local server flow
            credentials = flow.run_local_server(port=8080)

            # Save credentials for future use
            await self._save_credentials(credentials)

            # Build service
            self.service = build("youtube", "v3", credentials=credentials)
            self.credentials = credentials

            logger.info("YouTube authentication successful!")
            return "Authentication successful"

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            raise

    def get_auth_instructions(self) -> str:
        """Get instructions for setting up authentication"""
        return """
🔑 YouTube Authentication Setup:

1. Desktop App (Recommended for CLI):
   - Set YOUTUBE_AUTH_MODE=desktop in your .env file
   - Use: python cli.py youtube-auth
   - Copy/paste the authorization code

2. Local Server (Automatic):
   - Use: python -c "from platforms.youtube.service import YouTubeService; import asyncio; asyncio.run(YouTubeService().authenticate_local_server())"
   - Browser opens automatically

3. Web App (Manual):
   - Set YOUTUBE_AUTH_MODE=web in your .env file
   - Update Google Console redirect URI to: http://localhost:8000/auth/youtube/callback
   - Use: python cli.py youtube-auth

Choose the method that works best for your setup!
        """