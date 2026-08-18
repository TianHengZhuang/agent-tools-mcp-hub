# JWT / Base64 Token Decoder Tool

An MCP-compatible agent tool that decodes and inspects JSON Web Tokens (JWT) headers and payload claims without verifying cryptographic signatures.

## Parameters
- `token` (`string`, required): The raw JWT token string (`header.payload.signature`).

## Output
Returns JSON containing:
- `header`: Parsed JWT header (e.g. algorithm, token type).
- `payload`: Decoded claims dictionary (e.g. `sub`, `iss`, `aud`, `exp`).
- `is_expired`: Boolean indicating if the `exp` timestamp has passed.
- `expires_in_seconds`: Remaining lifespan in seconds (or negative if expired).
