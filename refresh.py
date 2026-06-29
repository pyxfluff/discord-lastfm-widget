# pyxfluff 2026

import httpx

from time import sleep
from pathlib import Path
from orjson import loads
from rich.console import Console
from datetime import datetime, timezone, timedelta

# Init
logger = Console(force_terminal=True)

# Config
config = loads((Path(__file__).parent / "config.json").read_text())

lastfm_key = config["lfm_key"]
refresh_mins = config["refresh_mins"]

def get_lastfm_data(u):
    profile_info = httpx.get(
        f"https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={u["name"]}&api_key={lastfm_key}&format=json"
    ).raise_for_status().json()["user"]
    serialized = {}

    serialized["name"] = profile_info["realname"]
    serialized["username"] = profile_info["name"]
    serialized["pfp"] = profile_info["image"][2]["#text"]
    serialized["tracks"] = profile_info["track_count"]
    serialized["albums"] = profile_info["album_count"]
    serialized["artists"] = profile_info["artist_count"]

    logger.print("[green]Retrieved basic profile info![/]")

    # get 30d count
    page = 1
    plays = 0
    at_plays = 0
    while True:
        stop = False
        data = httpx.get(
            f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={u["name"]}&api_key={lastfm_key}&format=json&limit=200&page={page}"
        ).raise_for_status().json()

        logger.print(f"[blue]Retrieved historical scrobbles (page {page})[/]")

        at_plays = data["recenttracks"]["@attr"]["total"]

        for track in data["recenttracks"]["track"]:
            if "date" not in track:
                continue

            if int(track["date"]["uts"]) < int(
                (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
            ):
                stop = True
                break

            plays += 1

        if stop:
            break

        page += 1

    logger.print("[green]finished![/]")

    serialized["plays_30d"] = plays
    serialized["plays"] = at_plays
    serialized["loved_tracks"] = httpx.get(
        f"https://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user={u["name"]}&api_key={lastfm_key}&limit=1&format=json"
    ).json()["lovedtracks"]["@attr"]["total"]

    logger.print("[green]Retrieved loved tracks count!")

    return serialized



def push_data_to_discord(u):
    data = get_lastfm_data(u)

    logger.print(f"[yellow]Pushing data to discord ({u["id"]})")

    httpx.patch(
        f"https://discord.com/api/v9/applications/{u["app_id"]}/users/{u["id"]}/identities/0/profile",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bot {u["token"]}",
            "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 1.0.0)",
        },
        json={
            "data": {
                "dynamic": [
                    {
                        "type": 3,
                        "name": "profile_picture_url",
                        "value": {"url": data["pfp"]},
                    },
                    {"type": 1, "name": "header_1", "value": data["name"]},
                    {"type": 1, "name": "header_2", "value": f"@{data["username"]}"},
                    {"type": 1, "name": "scrobbles_all_time", "value": data["plays"]},
                    {"type": 2, "name": "loved_tracks", "value": data["loved_tracks"]},
                    {"type": 1, "name": "scrobbles_recently", "value": data["plays_30d"]},
                    {"type": 1, "name": "tracks", "value": data["tracks"]},
                    {"type": 1, "name": "albums", "value": data["albums"]},
                    {"type": 1, "name": "artists", "value": data["artists"]},
                    {
                        "type": 3,
                        "name": "preview_background",
                        "value": {"url": "https://pyxfluff.dev/images/pfp_2026.png"}
                    }
                ]
            }
        }
    )

while True:
    logger.print("[yellow]Starting hourly check[/]")

    for user in config["users"]:
        logger.print(f"[blue]Checking [bold]{user["name"]}[/b][/]")

        push_data_to_discord(user)

        logger.print("[green]Finished![/]")
    
    logger.print(f"[blue]Sleeping for {refresh_mins} minutes")
    sleep(refresh_mins * 60)
    
