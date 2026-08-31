"""
Source Verification Module
Distinguishes between official government/recruitment portals and secondary aggregator sources.
Never presents unverified aggregator claims as official fact.
"""
from urllib.parse import urlparse
from typing import Tuple

OFFICIAL_GOV_TLDS = [
    ".gov.in", ".nic.in", ".ac.in", ".edu.in", ".res.in",
    ".mil.in", ".gov", ".mil"
]

KNOWN_OFFICIAL_DOMAINS = [
    "upsc.gov.in", "ssc.gov.in", "ssc.nic.in", "ibps.in",
    "rrbcdg.gov.in", "drdo.gov.in", "isro.gov.in", "drdo.res.in",
    "nta.ac.in", "joinindianarmy.nic.in", "joinindiannavy.gov.in",
    "indianairforce.nic.in", "afcat.cdac.in", "cdac.in",
    "sail.co.in", "ongcindia.com", "bhel.com", "iocl.com",
    "ntpc.co.in", "powergrid.in", "coalindia.in", "hal-india.co.in",
    "barc.gov.in", "npcil.nic.in", "bel-india.in", "ecil.co.in",
    "nielit.gov.in", "bis.gov.in", "fssai.gov.in", "sebi.gov.in",
    "rbi.org.in", "sbi.co.in", "nabard.org", "epfindia.gov.in",
    "esic.gov.in", "aiims.edu"
]

KNOWN_SECONDARY_DOMAINS = [
    "sarkariresult.com", "freejobalert.com", "jagranjosh.com",
    "indgovtjobs.in", "rojgarsamachar.gov.in", "testbook.com",
    "adda247.com", "oliveboard.in", "careerpower.in", "shiksha.com",
    "collegedunia.com", "freshersworld.com", "freshersnow.com"
]


def classify_source_domain(url: str) -> Tuple[str, str, float]:
    """
    Classifies a URL into (source_type, verification_status, confidence).
    source_type: 'official', 'secondary', 'telegram_only', 'unknown'
    verification_status: 'verified', 'unverified'
    """
    if not url:
        return "telegram_only", "unverified", 0.3

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        # Check official Gov TLDs
        for tld in OFFICIAL_GOV_TLDS:
            if netloc.endswith(tld):
                return "official", "verified", 1.0

        # Check known official domain names
        for domain in KNOWN_OFFICIAL_DOMAINS:
            if netloc == domain or netloc.endswith("." + domain):
                return "official", "verified", 0.95

        # Check known secondary job aggregator domains
        for domain in KNOWN_SECONDARY_DOMAINS:
            if netloc == domain or netloc.endswith("." + domain):
                return "secondary", "unverified", 0.65

        # Unknown domain
        return "secondary", "unverified", 0.5
    except Exception:
        return "unknown", "unverified", 0.2
