# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path

from py_yt import Playlist, VideosSearch

from anony import logger
from anony.helpers import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.track_titles = {}
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        if not urls:
            return
        os.makedirs(self.cookie_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            for url in urls:
                name = url.split("/")[-1]
                link = "https://batbin.me/raw/" + name
                try:
                    async with session.get(link) as resp:
                        resp.raise_for_status()
                        with open(f"{self.cookie_dir}/{name}.txt", "wb") as fw:
                            fw.write(await resp.read())
                except Exception:
                    pass

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def invalid(self, url: str) -> bool:
        return bool(re.match(self.iregex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
        except Exception:
            return None
        if results and results["result"]:
            data = results["result"][0]
            v_id = data.get("id")
            v_title = data.get("title", query)
            if v_id:
                self.track_titles[v_id] = v_title
            return Track(
                id=v_id,
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=v_title[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                v_id = data.get("id")
                v_title = data.get("title", "")
                if v_id:
                    self.track_titles[v_id] = v_title
                track = Track(
                    id=v_id,
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=v_title[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception:
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        os.makedirs("downloads", exist_ok=True)
        song_title = self.track_titles.get(video_id, "")

        for f in os.listdir("downloads"):
            if f.startswith(video_id):
                return os.path.join("downloads", f)

        url = self.base + video_id

        def _download():
            # 1. YouTube Android / Web-Embedded (Reload hatası vermez)
            opts = {
                "format": "bestaudio/best",
                "outtmpl": f"downloads/{video_id}.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web_embedded"]
                    }
                },
            }
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                for f in os.listdir("downloads"):
                    if f.startswith(video_id):
                        return os.path.join("downloads", f)
            except Exception as ex:
                logger.warning("YouTube indirme hatası: %s", ex)

            # 2. Yedek: SoundCloud
            if song_title:
                try:
                    sc_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": f"downloads/{video_id}.%(ext)s",
                        "quiet": True,
                        "no_warnings": True,
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                    }
                    with yt_dlp.YoutubeDL(sc_opts) as ydl:
                        ydl.download([f"scsearch1:{song_title}"])
                    for f in os.listdir("downloads"):
                        if f.startswith(video_id):
                            return os.path.join("downloads", f)
                except Exception as e:
                    logger.warning("SoundCloud indirme hatası: %s", e)

            return None

        return await asyncio.to_thread(_download)