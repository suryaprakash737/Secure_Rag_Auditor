import re
from collections.abc import Iterable


_IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

_SUSPICIOUS_IPS = {
    "192.168.1.105": {
        "reputation": "malicious",
        "threat_type": "brute_force",
    },
}

_SUSPICIOUS_DOMAINS = {
    "malware.example.com": {
        "reputation": "malicious",
        "threat_type": "command_and_control",
    },
}

_SUSPICIOUS_HASHES = {
    "44d88612fea8a8f36de82e1278abb02f": {
        "reputation": "malicious",
        "threat_type": "malware",
    },
}


def _unknown_result(indicator: str) -> dict:
    return {
        "indicator": indicator,
        "reputation": "unknown",
        "threat_type": "unknown",
    }


def enrich_ip(ip_address: str) -> dict:
    threat_data = _SUSPICIOUS_IPS.get(ip_address)
    if not threat_data:
        return _unknown_result(ip_address)

    return {
        "indicator": ip_address,
        "reputation": threat_data["reputation"],
        "threat_type": threat_data["threat_type"],
    }


def enrich_domain(domain: str) -> dict:
    threat_data = _SUSPICIOUS_DOMAINS.get(domain)
    if not threat_data:
        return _unknown_result(domain)

    return {
        "indicator": domain,
        "reputation": threat_data["reputation"],
        "threat_type": threat_data["threat_type"],
    }


def enrich_hash(file_hash: str) -> dict:
    threat_data = _SUSPICIOUS_HASHES.get(file_hash)
    if not threat_data:
        return _unknown_result(file_hash)

    return {
        "indicator": file_hash,
        "reputation": threat_data["reputation"],
        "threat_type": threat_data["threat_type"],
    }


def _metadata_values(metadata: Iterable[dict]) -> Iterable[str]:
    for item in metadata:
        for value in item.values():
            yield str(value)


def extract_ip_addresses(docs: list[str], metadata: list[dict]) -> list[str]:
    searchable_text = "\n".join([*docs, *_metadata_values(metadata)])
    return sorted(set(_IP_PATTERN.findall(searchable_text)))


def enrich_detected_ips(docs: list[str], metadata: list[dict]) -> list[dict]:
    return [enrich_ip(ip_address) for ip_address in extract_ip_addresses(docs, metadata)]
