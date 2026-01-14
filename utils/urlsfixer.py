# your_app/utils.py

from urllib.parse import urlparse, urlunparse

def build_https_url(request, relative_url):
    if request:
        full_url = request.build_absolute_uri(relative_url)
        parsed = urlparse(full_url)
        # Replace scheme with https, keep host and path from the request
        secure_url = urlunparse(parsed._replace(scheme='https'))
        return secure_url
    else:
        # Fallback - can return relative url or raise error
        return relative_url
