from datetime import datetime
import rtt_client

_token = None
_token_expiry = None
EXPIRY_BUFFER_S = 60
def get_token():
    global _token, _token_expiry

    now = datetime.now().timestamp()
    if _token is not None and _token_expiry is not None and now < _token_expiry:
        return _token

    token,   valid_until =rtt_client.get_access_token()
    expiry = datetime.fromisoformat(valid_until).timestamp() - EXPIRY_BUFFER_S
    _token =token
    _token_expiry= expiry
    return _token