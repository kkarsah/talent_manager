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
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
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
        """Start OAuth flow and return authorization URL"""

        # Create client config
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

    async def handle_callback(self, authorization_code: str) -> bool:
        """Handle OAuth callback and store credentials"""
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
        """Load existing credentials"""
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
            request = self.service.videos().insert(
                part=",".join(body.keys()), body=body, media_body=media
            )

            # Execute resumable upload
            response = None
            error = None
            retry = 0

            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")

                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retry on server errors
                        if retry < 3:
                            retry += 1
                            logger.warning(f"Upload error, retrying ({retry}/3): {e}")
                            continue
                    raise

            if response:
                video_id = response["id"]
                logger.info(f"Upload successful! Video ID: {video_id}")

                # Upload thumbnail if provided
                if thumbnail_path and Path(thumbnail_path).exists():
                    await self._upload_thumbnail(video_id, thumbnail_path)

                return video_id

            return None

        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            raise

    async def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail"""
        try:
            request = self.service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
            )
            request.execute()
            logger.info(f"Thumbnail uploaded for video {video_id}")

        except Exception as e:
            logger.warning(f"Thumbnail upload failed: {e}")

    async def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get basic video analytics"""
        if not self.service:
            if not await self.load_credentials():
                raise RuntimeError("YouTube not authenticated")

        try:
            # Get video statistics
            response = (
                self.service.videos()
                .list(part="statistics,snippet", id=video_id)
                .execute()
            )

            if response["items"]:
                video = response["items"][0]
                stats = video["statistics"]
                snippet = video["snippet"]

                return {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "published_at": snippet["publishedAt"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "duration": snippet.get("duration"),
                    "tags": snippet.get("tags", []),
                }

            return {}

        except Exception as e:
            logger.error(f"Failed to get video analytics: {e}")
            return {}

    async def get_channel_info(self) -> Dict[str, Any]:
        """Get channel information"""
        if not self.service:
            if not await self.load_credentials():
                raise RuntimeError("YouTube not authenticated")

        try:
            response = (
                self.service.channels()
                .list(part="snippet,statistics", mine=True)
                .execute()
            )

            if response["items"]:
                channel = response["items"][0]
                snippet = channel["snippet"]
                stats = channel["statistics"]

                return {
                    "channel_id": channel["id"],
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "subscriber_count": int(stats.get("subscriberCount", 0)),
                    "video_count": int(stats.get("videoCount", 0)),
                    "view_count": int(stats.get("viewCount", 0)),
                    "thumbnail": snippet["thumbnails"]["default"]["url"],
                }

            return {}

        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return {}

    async def list_recent_videos(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List recent videos from the channel"""
        if not self.service:
            if not await self.load_credentials():
                raise RuntimeError("YouTube not authenticated")

        try:
            # Get channel uploads playlist
            channel_response = (
                self.service.channels().list(part="contentDetails", mine=True).execute()
            )

            if not channel_response["items"]:
                return []

            uploads_playlist_id = channel_response["items"][0]["contentDetails"][
                "relatedPlaylists"
            ]["uploads"]

            # Get recent videos
            playlist_response = (
                self.service.playlistItems()
                .list(
                    part="snippet",
                    playlistId=uploads_playlist_id,
                    maxResults=max_results,
                )
                .execute()
            )

            videos = []
            for item in playlist_response["items"]:
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]

                # Get video statistics
                stats_response = (
                    self.service.videos().list(part="statistics", id=video_id).execute()
                )

                stats = (
                    stats_response["items"][0]["statistics"]
                    if stats_response["items"]
                    else {}
                )

                videos.append(
                    {
                        "video_id": video_id,
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

    def is_authenticated(self) -> bool:
        """Check if YouTube is authenticated"""
        return self.service is not None and self.credentials is not None
