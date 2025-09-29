import re
from typing import Any, Dict, Optional


DOMAIN_RE = re.compile(r"(?<![\w.-])((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})(?![\w.-])")


def extract_domain_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    cf = payload.get("custom_fields")
    if isinstance(cf, list):
        for f in cf:
            name = f.get("name").lower()
            if name == "домен":
                val = f.get("text_value")
                if isinstance(val, str):
                    m = DOMAIN_RE.search(val)
                    if m:
                        return m.group(1)


def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    domain = domain.replace('http://', '').replace('https://', '')
    domain = domain.split("/", 1)[0]
    return domain


def clip_friendly(name: str) -> str:
    name = "" if name is None else str(name)
    return name[:250]


def build_monitor_context(raw_domain: str, scheme: str = "https", treat_www_as_same: bool = True) -> dict:
    domain = normalize_domain(raw_domain)
    url_main = f"{scheme}://{domain}"
    return {
        "domain": domain,
        "monitor_url": url_main,
        "friendly_name": domain,
    }