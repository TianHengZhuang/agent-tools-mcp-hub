"""
JWT / Base64 Token Decoder Tool
Decodes JWT headers and payload claims without cryptographic verification.
"""
import base64
import json
import time
from typing import Dict, Any

def _base64url_decode(input_str: str) -> str:
    """Decodes a base64url-encoded string with appropriate padding."""
    rem = len(input_str) % 4
    if rem > 0:
        input_str += '=' * (4 - rem)
    return base64.urlsafe_b64decode(input_str.encode('utf-8')).decode('utf-8', errors='replace')

def run_tool(token: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Decodes a JWT token into its header and payload components.
    
    Args:
        token (str): JWT string (header.payload.signature).
        
    Returns:
        Dict[str, Any]: Decoded claims, header, and expiration metadata.
    """
    if not token or not isinstance(token, str):
        return {
            "success": False,
            "error": "The 'token' parameter must be a non-empty string."
        }
    
    token = token.strip()
    parts = token.split('.')
    
    if len(parts) != 3:
        return {
            "success": False,
            "error": "Invalid JWT format. Expected exactly 3 period-separated segments (header.payload.signature)."
        }
    
    try:
        header_raw = _base64url_decode(parts[0])
        payload_raw = _base64url_decode(parts[1])
        
        header = json.loads(header_raw)
        payload = json.loads(payload_raw)
        
        # Expiration analysis
        exp = payload.get("exp")
        is_expired = None
        expires_in_seconds = None
        if isinstance(exp, (int, float)):
            now = time.time()
            is_expired = now > exp
            expires_in_seconds = int(exp - now)
            
        return {
            "success": True,
            "data": {
                "header": header,
                "payload": payload,
                "signature_present": bool(parts[2]),
                "is_expired": is_expired,
                "expires_in_seconds": expires_in_seconds
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse and decode JWT segments: {str(e)}"
        }

if __name__ == "__main__":
    sample = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjI1MTYyMzkwMjJ9.4zC1j8u..."
    print(run_tool(sample))
