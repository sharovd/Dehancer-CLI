import codecs

ENCODING_UTF_8 = codecs.lookup("utf-8").name

DEHANCER_ONLINE_BASE_URL = "https://online.dehancer.com"
DEHANCER_ONLINE_API_BASE_URL = f"{DEHANCER_ONLINE_BASE_URL}/api/v1"

HEADER_USER_AGENT = "Mozilla/5.0"
HEADER_ACCEPT_LANGUAGE_EN = "en-US,en;q=0.5"
HEADER_ACCEPT_ENCODING = "gzip, deflate, br, zstd"
HEADER_JSON_CONTENT_TYPE = "application/json"
HEADER_PRIORITY_U_0 = "u=0"
HEADER_TRANSFER_ENCODING_TRAILERS = "trailers"
BASE_HEADERS = {
    "User-Agent": HEADER_USER_AGENT,
    "Accept-Language": HEADER_ACCEPT_LANGUAGE_EN,
    "Referer": f"{DEHANCER_ONLINE_BASE_URL}",
    "Origin": f"{DEHANCER_ONLINE_BASE_URL}",
}
SECURITY_HEADERS = {
    "DNT": "1",  # Do Not Track
    "Sec-GPC": "1",  # Google's "SameSite" Cookie Policy
    "Sec-Fetch-Dest": "empty",  # Destination
    "Sec-Fetch-Mode": "cors",  # Cross-Origin Resource Sharing
    "Sec-Fetch-Site": "cross-site",  # Cross-Site Request
}

IMAGE_VALID_TYPES = {
    "jpeg": "image/jpeg",
    "tiff": "image/tiff",
    "heif": "image/heif",
    "heic": "image/heic",
    "avif": "image/avif",
    "webp": "image/webp",
    "dng": "image/x-adobe-dng",
    "png": "image/png",
}

PRESET_DEFAULT_STATE = {
    "contrast": 0,
    "exposure": 0,
    "temperature": 0,
    "tint": 0,
    "color_boost": 0,
    "bloom": 0,
    "halation": 0,
    "grain": 0,
}
