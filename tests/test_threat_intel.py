from app.services.threat_intel_service import (
    enrich_detected_ips,
    enrich_domain,
    enrich_hash,
    enrich_ip,
    extract_ip_addresses,
)


def test_enrich_known_ip():
    result = enrich_ip("192.168.1.105")

    assert result == {
        "indicator": "192.168.1.105",
        "reputation": "malicious",
        "threat_type": "brute_force",
    }


def test_unknown_ip_returns_unknown():
    result = enrich_ip("10.0.0.1")

    assert result == {
        "indicator": "10.0.0.1",
        "reputation": "unknown",
        "threat_type": "unknown",
    }


def test_enrich_known_domain():
    result = enrich_domain("malware.example.com")

    assert result["reputation"] == "malicious"
    assert result["threat_type"] == "command_and_control"


def test_unknown_domain_returns_unknown():
    result = enrich_domain("example.org")

    assert result["indicator"] == "example.org"
    assert result["reputation"] == "unknown"
    assert result["threat_type"] == "unknown"


def test_enrich_known_hash():
    result = enrich_hash("44d88612fea8a8f36de82e1278abb02f")

    assert result["reputation"] == "malicious"
    assert result["threat_type"] == "malware"


def test_unknown_hash_returns_unknown():
    result = enrich_hash("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    assert result["indicator"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert result["reputation"] == "unknown"
    assert result["threat_type"] == "unknown"


def test_extract_ip_addresses_from_docs_and_metadata():
    docs = ["Failed SSH login attempt from IP 192.168.1.105"]
    metadata = [{"source_device": "sensor-10.0.0.5", "security_level": 2}]

    assert extract_ip_addresses(docs, metadata) == ["10.0.0.5", "192.168.1.105"]


def test_enrich_detected_ips_is_deterministic():
    docs = ["IP 192.168.1.105 contacted IP 10.0.0.1"]
    metadata = [{"source_device": "firewall"}]

    assert enrich_detected_ips(docs, metadata) == [
        {
            "indicator": "10.0.0.1",
            "reputation": "unknown",
            "threat_type": "unknown",
        },
        {
            "indicator": "192.168.1.105",
            "reputation": "malicious",
            "threat_type": "brute_force",
        },
    ]
