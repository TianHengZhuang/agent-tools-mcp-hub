"""
Spotify Current Track and Playlist Tool for AI Agents and MCP Hub.
"""
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any

def run_tool(action: str, limit: int = 10, **kwargs: Any) -> Dict[str, Any]:
    """
    Standard agent dispatcher entrypoint for Spotify.
    """
    token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    
    if not token:
        return {
            "success": False,
            "error": "SPOTIFY_ACCESS_TOKEN environment variable is required."
        }
        
    if action not in ["current_track", "playlists"]:
        return {
            "success": False,
            "error": f"Invalid action '{action}'. Must be 'current_track' or 'playlists'."
        }
        
    try:
        limit = int(limit)
        if limit < 1:
            return {"success": False, "error": "limit must be at least 1."}
    except ValueError:
        return {"success": False, "error": "limit must be an integer."}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "AgentToolsHub/1.0"
    }

    if action == "current_track":
        url = "https://api.spotify.com/v1/me/player/currently-playing"
    else:
        url = f"https://api.spotify.com/v1/me/playlists?limit={limit}"
        
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 204:  # No Content (e.g. not playing anything)
                if action == "current_track":
                    return {"success": True, "data": None, "message": "No track is currently playing."}
                return {"success": True, "data": None}
                
            data = json.loads(response.read().decode("utf-8"))
            return {"success": True, "data": data}
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        if e.code == 401:
            error_msg = "Unauthorized: Invalid or expired access token."
        elif e.code == 403:
            error_msg = "Forbidden: Insufficient scopes or bad OAuth request."
        elif e.code == 429:
            error_msg = "Too Many Requests: Rate limited by Spotify."
            
        try:
            body = e.read().decode("utf-8")
            if body:
                error_json = json.loads(body)
                if "error" in error_json and "message" in error_json["error"]:
                    error_msg += f" - {error_json['error']['message']}"
        except Exception:
            pass
            
        return {"success": False, "error": error_msg}
        
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Network connection error: {str(e.reason)}"}
        
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    print("Spotify Player Tool loaded.")
    print("Running with action='current_track' (expecting missing token error unless set):")
    result = run_tool(action="current_track")
    print(json.dumps(result, indent=2))
