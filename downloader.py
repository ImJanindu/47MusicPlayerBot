from os import path
from youtube_dl import YoutubeDL

ydl_opts = {
    "format": "bestaudio/best",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)

def download(url: str) -> str:
    info = ydl.extract_info(url, False)
    ydl.download([url])
    return path.join("downloads", f"{info['id']}.{info['ext']}")
