# 🎵 Spotify Player Tool

A tool to fetch the currently playing track and the user's private/public playlists from Spotify.

## Setup

> **Note**: This tool requires a **User Access Token** (via the Authorization Code flow) rather than a simple Client Credentials App Token, because it accesses user-specific data (your current track and private playlists).

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and create an app.
2. Obtain a User OAuth access token with the `user-read-currently-playing` and `playlist-read-private` scopes.
3. Set the token as an environment variable:
   ```bash
   export SPOTIFY_ACCESS_TOKEN="your_user_token_here"
   ```

## Usage (Python)

```python
import sys
import os
sys.path.append("tools/spotify_player")
from tool import run_tool

os.environ["SPOTIFY_ACCESS_TOKEN"] = "your_token_here"

# Fetch current track
current_track = run_tool(action="current_track")
print(current_track)

# Fetch playlists
playlists = run_tool(action="playlists", limit=5)
print(playlists)
```
