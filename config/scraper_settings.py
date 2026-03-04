from pydantic_settings import BaseSettings


class ScraperSettings(BaseSettings):

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s %(levelname)s %(name)s | %(message)s"
    log_to_file: bool = True
    log_file_path: str = "logs/scraper.log"

    # Site details
    site_url: str = "https://www.slobodenpecat.mk/"
    site_name: str = "sloboden_pechat"
    api_base_url: str = "https://www.slobodenpecat.mk/wp-json/wp/v2/posts"

    # Scraping settings
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    max_pages_per_category: int = 50

    # Rate limiting
    requests_per_second: float = 2

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # HTTP headers
    headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    category_ids: dict = {
        "makedonija": 57,
        "skopje": 1089,
        "region": 1090,
        "ekonomija": 67,
        "kultura": 1373,
        "hronika": 1092,
        "vi-preporachuvame": 9081,
        "svet": 1091,
        "milenici": 89861,
        "semejstvo": 78,
        "zena": 7497,
        "zabava": 1374,
        "tehnologija": 72,
        "zivot": 38079,
        "scena": 42379,
        "hrana": 76,
        "zdravje": 74,
        "retro": 42381,
        "horoskop": 81,
        "avtomagazin": 73,
        "film-i-muzika": 71,
        "kolumni": 31,
        "golemi-prikazni": 122889,
        "fudbal": 83,
        "kosarka": 84,
        "rakomet": 85,
        "ostanato-sport": 86
    }

    model_config = {
        "env_file": ".env"
    }


settings = ScraperSettings()
