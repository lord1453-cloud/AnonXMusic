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
        logger.info("Saving cookies from urls...")
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
        logger.info(f"Cookies saved in {self.cookie_dir}.")

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
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
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
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
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
        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists():
            return filename

        os.makedirs("downloads", exist_ok=True)
        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": f"downloads/{video_id}.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            "cookiefile": cookie,
            "extractor_args": {
                "youtube": {
                    "player_client": ["web_safari", "android", "mweb"]
                }
            },
        }

        ydl_opts = {
            **base_opts,
            "format": "bestaudio/best",
        }

        def _download():
            # 1. Önce YouTube'dan dene
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                for f in os.listdir("downloads"):
                    if f.startswith(video_id):
                        return f"downloads/{f}"
            except Exception as e:
                logger.warning(f"YouTube indirmesi engellendi, SoundCloud yedeğine geçiliyor: {e}")

            # 2. YouTube engellenirse SoundCloud / Alternatif akış üzerinden indir
            try:
                sc_opts = {
                    "outtmpl": f"downloads/{video_id}.%(ext)s",
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "geo_bypass": True,
                }
                with yt_dlp.YoutubeDL(sc_opts) as sc_ydl:
                    sc_ydl.download([f"scsearch:{video_id}"])
                for f in os.listdir("downloads"):
                    if f.startswith(video_id):
                        return f"downloads/{f}"
            except Exception as ex:
                logger.error(f"Tüm indirme yöntemleri başarısız oldu: {ex}")
                return None

            return filename

        return await asyncio.to_thread(_download)