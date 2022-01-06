from fastapi_auth0 import Auth0

from app.core.env import ENV

auth = Auth0(
    domain=ENV.AUTH0_DOMAIN,
    api_audience=ENV.AUTH0_API_AUDIENCE,
)
