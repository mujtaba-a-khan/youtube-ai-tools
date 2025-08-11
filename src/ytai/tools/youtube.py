from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from dataclasses import dataclass
import re

@dataclass
class Video:
    video_id: str
    title: str
    channel: str
    published_at: str
    view_count: int | None
    url: str
    description: str | None

class YouTubeClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY is missing")
        self.api_key = api_key
        self._yt = build("youtube", "v3", developerKey=api_key)

    @staticmethod
    def extract_video_id(url_or_id: str) -> str:
        # Accepts raw ID or any YouTube URL form
        patterns = [
            r"(?:v=|/v/|youtu\.be/|/shorts/)([\w-]{11})",
            r"^([\w-]{11})$",
        ]
        for p in patterns:
            m = re.search(p, url_or_id)
            if m:
                return m.group(1)
        raise ValueError("Could not extract video id from input")

    def get_trending(self, region: str = "US", max_results: int = 10) -> List[Video]:
        req = self._yt.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region,
            maxResults=max_results,
        )
        resp = req.execute()
        items = []
        for it in resp.get("items", []):
            sn = it.get("snippet", {})
            st = it.get("statistics", {})
            vid = it.get("id")
            items.append(
                Video(
                    video_id=vid,
                    title=sn.get("title", ""),
                    channel=sn.get("channelTitle", ""),
                    published_at=sn.get("publishedAt", ""),
                    view_count=int(st.get("viewCount", 0)) if st.get("viewCount") else None,
                    url=f"https://www.youtube.com/watch?v={vid}",
                    description=sn.get("description"),
                )
            )
        return items

    def search(self, query: str, max_results: int = 10, region: Optional[str] = None) -> List[Video]:
        req = self._yt.search().list(
            part="snippet",
            q=query,
            type="video",
            regionCode=region,
            maxResults=max_results,
            order="relevance",
        )
        resp = req.execute()
        out: List[Video] = []
        for it in resp.get("items", []):
            sn = it.get("snippet", {})
            vid = it.get("id", {}).get("videoId")
            out.append(
                Video(
                    video_id=vid,
                    title=sn.get("title", ""),
                    channel=sn.get("channelTitle", ""),
                    published_at=sn.get("publishedAt", ""),
                    view_count=None,
                    url=f"https://www.youtube.com/watch?v={vid}",
                    description=sn.get("description"),
                )
            )
        return out

    def get_video_snippet(self, video_id: str) -> Dict[str, Any]:
        req = self._yt.videos().list(part="snippet,statistics", id=video_id)
        return req.execute()

    def get_transcript(self, video_id: str, languages: Optional[List[str]] = None) -> Tuple[str | None, List[Dict[str, Any]]]:
        languages = languages or ["en", "en-US"]
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            text = " ".join([chunk["text"] for chunk in data if chunk.get("text")])
            return text, data
        except (TranscriptsDisabled, NoTranscriptFound):
            return None, []
        except Exception:
            # Could be rate limit or something else.
            return None, []