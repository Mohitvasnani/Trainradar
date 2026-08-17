"""
RTT access token lifecycle.

RTT issues a short-life access token in exchange for the long-life refresh
token held in .env. This module holds the current access token and refreshes
it only when it has expired, so a burst of requests costs one token call
rather than one per request.
"""

from datetime import datetime

import rtt_client


_token = None
_token_expiry = None

# Refresh this many seconds before the token actually expires, so a request
# never goes out holding a token that dies mid-flight.
EXPIRY_BUFFER_S = 60


def get_token():
    """Return a valid access token, refreshing it if expired or missing."""
    global _token, _token_expiry

    now = datetime.now().timestamp()
    if _token is not None and _token_expiry is not None and now < _token_expiry:
        return _token

    token, valid_until = rtt_client.get_access_token()

    # Parse before assigning, so a malformed expiry cannot leave a token
    # cached with no expiry recorded against it.
    expiry = datetime.fromisoformat(valid_until).timestamp() - EXPIRY_BUFFER_S

    _token = token
    _token_expiry = expiry
    return _token