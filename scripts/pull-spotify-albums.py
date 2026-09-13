import base64
import hashlib
import http.server
import json
import os
import re
import secrets
import threading
import time
import urllib.parse
import webbrowser

import requests
import yaml

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-library-read"
ALBUMS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images", "albums")
OUTPUT_YML = os.path.join(os.path.dirname(__file__), "..", "data", "albums.yml")

client_id = os.environ.get("SPOTIFY_CLIENT_ID") or input("Spotify Client ID: ").strip()

verifier = secrets.token_urlsafe(64)
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b"=").decode()

auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "code_challenge_method": "S256",
    "code_challenge": challenge,
})

auth_code = None

class Callback(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("code")
        if code:
            auth_code = code[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorized. You can close this tab.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code.")

    def log_message(self, *a):
        pass

server = http.server.HTTPServer(("127.0.0.1", 8888), Callback)
threading.Thread(target=server.serve_forever, daemon=True).start()

print("Opening browser for Spotify login...")
webbrowser.open(auth_url)
print("If it does not open, paste this URL into your browser:\n")
print(auth_url)
print()

while auth_code is None:
    time.sleep(0.5)
server.shutdown()

resp = requests.post(
    "https://accounts.spotify.com/api/token",
    data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "code_verifier": verifier,
    },
    timeout=30,
)
resp.raise_for_status()
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

albums = []
limit = 50
offset = 0
while True:
    r = requests.get(
        "https://api.spotify.com/v1/me/albums",
        params={"limit": limit, "offset": offset},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    if not items:
        break
    for item in items:
        a = item["album"]
        artists = ", ".join(x["name"] for x in a["artists"])
        albums.append({
            "title": a["name"],
            "artist": artists,
            "year": (a.get("release_date") or "")[:4],
            "image_url": a["images"][0]["url"] if a.get("images") else "",
            "spotify_id": a["id"],
        })
    if len(items) < limit:
        break
    offset += limit

print(f"Fetched {len(albums)} saved albums from Spotify")


def slugify(text):
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:60]


def unique_slug(base, seen):
    slug, n = base, 1
    while slug in seen:
        n += 1
        slug = f"{base}-{n}"
    seen.add(slug)
    return slug


os.makedirs(ALBUMS_DIR, exist_ok=True)
entries = []
slugs = set()
for a in albums:
    base = slugify(f"{a['title']}-{a['artist'].split(',')[0]}")
    slug = unique_slug(base, slugs)
    img_path = os.path.join(ALBUMS_DIR, f"{slug}.jpg")
    image_ref = f"/images/albums/{slug}.jpg"
    if a["image_url"]:
        if not os.path.exists(img_path):
            downloaded = False
            for attempt in range(3):
                try:
                    ir = requests.get(a["image_url"], timeout=30)
                    if ir.ok:
                        with open(img_path, "wb") as f:
                            f.write(ir.content)
                        downloaded = True
                        break
                    print(f"  retry {attempt + 1}: HTTP {ir.status_code} for {a['title']}")
                except requests.RequestException as e:
                    print(f"  retry {attempt + 1}: {e} for {a['title']}")
                    time.sleep(2)
            if not downloaded:
                print(f"  cover download failed, falling back to remote URL for {a['title']}")
                image_ref = a["image_url"]
    else:
        image_ref = ""
    entries.append({
        "title": a["title"],
        "artist": a["artist"],
        "year": a["year"],
        "image": image_ref,
        "note": "",
    })

with open(OUTPUT_YML, "w") as f:
    f.write(
        "# Favourite albums — pulled from your Spotify saved library by scripts/pull-spotify-albums.py.\n"
        "# Add/rewrite the 'note' fields by hand; they are what show when you hover a cover.\n"
    )
    yaml.safe_dump(entries, f, allow_unicode=True, sort_keys=False, width=200)

print(f"Wrote {len(entries)} albums to {os.path.abspath(OUTPUT_YML)}")
print(f"Covers saved to {os.path.abspath(ALBUMS_DIR)}")
