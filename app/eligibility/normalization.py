"""
Comprehensive Government Job Normalization & Taxonomy Engine
Normalizes education levels, degree certificates, engineering disciplines,
government reservation categories, and non-job signals.
"""
import re
from typing import List, Set, Tuple, Optional, Dict, Any

# ==============================================================================
# 1. CANONICAL EDUCATION LEVEL HIERARCHY
# ==============================================================================
# Canonical ordering (higher index = higher educational attainment)
EDUCATION_LEVELS = [
    "any",
    "10th",
    "12th",
    "iti",
    "diploma",
    "bachelors",
    "masters",
    "doctorate",
]

# Patterns mapping raw strings to canonical levels
LEVEL_PATTERNS: List[Tuple[str, str]] = [
    (r"\b(ph\.?d|doctorate|doctoral)\b", "doctorate"),
    (r"\b(master|masters|m\.?tech|m\.?e\.?|mca|mba|m\.?sc|m\.?com|post\s*graduate|pg|pg\s*degree|post\s*graduation)\b", "masters"),
    (r"\b(b\.?tech|b\.?e\.?|btech|be|b\.?sc|bsc|bca|b\.?com|b\.?a\b|bachelor|bachelors|graduate|graduation|degree|undergraduate|ug)\b", "bachelors"),
    (r"\b(diploma|polytechnic|3\s*year\s*diploma)\b", "diploma"),
    (r"\b(iti|industrial\s*training\s*institute|ncvt|scvt)\b", "iti"),
    (r"\b(12th|intermediate|\+2|hsc|senior\s*secondary|higher\s*secondary|class\s*12|class\s*xii|10\+2)\b", "12th"),
    (r"\b(10th|matriculation|matric|secondary\s*school|high\s*school|class\s*10|class\s*x|ssc)\b", "10th"),
]

def get_education_level_index(level_str: str) -> int:
    """Returns canonical level rank index (0-7). Defaults to bachelors (5)."""
    norm = level_str.strip().lower()
    if norm in EDUCATION_LEVELS:
        return EDUCATION_LEVELS.index(norm)
    return 5  # default bachelors


def extract_education_levels(qual_strings: List[str]) -> List[str]:
    """Finds all canonical education levels mentioned across qualification strings."""
    found_levels = []
    for q in qual_strings:
        ql = q.lower()
        for pat, lvl in LEVEL_PATTERNS:
            if re.search(pat, ql):
                found_levels.append(lvl)
                break
    return found_levels


# ==============================================================================
# 2. OPEN GRADUATION & ANY DEGREE PATTERNS
# ==============================================================================
OPEN_GRADUATE_PATTERNS = [
    r"\bany\s+graduate\b",
    r"\bany\s+degree\b",
    r"\bany\s+graduation\b",
    r"\bany\s+bachelor\b",
    r"\bgraduate\s+in\s+any\s+discipline\b",
    r"\bgraduation\s+in\s+any\s+discipline\b",
    r"\bdegree\s+in\s+any\s+discipline\b",
    r"\bdegree\s+in\s+any\s+field\b",
    r"\bdegree\s+in\s+any\s+stream\b",
    r"\bdegree\s+in\s+any\s+subject\b",
    r"\bgraduate\s+degree\s+in\s+any\s+discipline\b",
    r"\bdegree\s+from\s+(?:a\s+)?recognized\s+university\b",
    r"\bgraduate\s+from\s+(?:a\s+)?recognized\s+university\b",
    r"\bgraduation\s+from\s+(?:a\s+)?recognized\s+university\b",
    r"\ba\s+degree\s+from\s+(?:a\s+)?recognized\s+university\b",
    r"\ba\s+degree\s+or\s+equivalent\b",
    r"\bdegree\s+or\s+equivalent\b",
    r"\bgraduation\s+or\s+equivalent\b",
    r"\bany\s+recognized\s+degree\b",
    r"\bany\s+discipline\b",
    r"^\s*degree\s*$",
    r"^\s*graduation\s*$",
    r"^\s*graduate\s*$",
    r"^\s*graduate\s+pass\s*$",
]

def is_open_graduation_requirement(qual_str: str) -> bool:
    """Returns True if the qualification represents an open degree requirement accepting any graduate."""
    ql = qual_str.lower().strip()

    # Guard: if it explicitly restricts to a non-technical/specialized discipline
    restrictive_disciplines = [
        r"\b(?:with|in)\s+(?:economics|statistics|english|journalism|mass\s*communication|law|commerce|arts|agriculture|horticulture|forestry|nursing|medicine|pharmacy|veterinary|botany|zoology)\b",
    ]
    for rpat in restrictive_disciplines:
        if re.search(rpat, ql):
            return False

    for pat in OPEN_GRADUATE_PATTERNS:
        if re.search(pat, ql):
            return True
    return False


# ==============================================================================
# 3. DOMAIN & DISCIPLINE SEPARATION (Medical, Law, Teaching vs Tech/General)
# ==============================================================================
# Degrees that are strictly medical/nursing/paramedical and should NEVER match general B.Sc / B.Tech
MEDICAL_NURSING_PATTERNS = [
    r"\b(nursing|gnm|anm|b\.?sc\.?\s*nursing|m\.?sc\.?\s*nursing|post\s*basic\s*b\.?sc\.?\s*nursing)\b",
    r"\b(mbbs|bds|m\.?d\.?|m\.?s\.?|dnb|paramedical|physiotherapy|dental|medical\s*officer|ayush|bams|bhms)\b",
    r"\b(pharmacy|b\.?pharm|b\.?pharma|m\.?pharm|d\.?pharm)\b",
]

LAW_PATTERNS = [
    r"\b(ll\.?b|ll\.?m|bachelor\s*of\s*law|degree\s*in\s*law|law\s*graduate)\b",
]

TEACHING_PATTERNS = [
    r"\b(b\.?ed|m\.?ed|d\.?el\.?ed|btc|ugc\s*net|jrf|ctet|tet)\b",
]

def is_medical_or_nursing_qualification(text: str) -> bool:
    tl = text.lower()
    return any(re.search(pat, tl) for pat in MEDICAL_NURSING_PATTERNS)


def is_law_qualification(text: str) -> bool:
    tl = text.lower()
    return any(re.search(pat, tl) for pat in LAW_PATTERNS)


def is_teaching_qualification(text: str) -> bool:
    tl = text.lower()
    return any(re.search(pat, tl) for pat in TEACHING_PATTERNS)


# ==============================================================================
# 4. DEGREE SYNONYMS & CANONICAL MAPPING
# ==============================================================================
# Standardizes degree representations
CANONICAL_DEGREE_SYNONYMS: Dict[str, List[str]] = {
    "B.Tech": [
        "b.tech", "btech", "b.e.", "be", "bachelor of technology",
        "bachelor of engineering", "engineering degree", "degree in engineering",
        "full-time engineering degree", "full time engineering degree",
        "b.e./b.tech", "b.tech/b.e.", "b.e / b.tech", "b.tech / b.e",
        "bachelor's degree in engineering", "bachelors in engineering",
        "undergraduate engineering degree"
    ],
    "B.E.": [
        "b.e.", "be", "b.tech", "btech", "bachelor of engineering",
        "bachelor of technology", "engineering degree", "degree in engineering",
        "full-time engineering degree", "b.e./b.tech", "b.tech/b.e."
    ],
    "Graduation": [
        "graduation", "graduate", "degree", "bachelor's degree", "bachelor degree",
        "bachelors", "undergraduate degree", "graduate pass", "any graduate",
        "any degree", "any graduation", "graduation in any discipline",
        "graduate in any discipline", "degree in any discipline",
        "graduate degree in any discipline", "degree from a recognized university",
        "a degree from a recognized university", "bachelor's degree in any discipline"
    ],
    "B.Sc": [
        "b.sc", "bsc", "bachelor of science", "b.sc (cs)", "b.sc (it)",
        "b.sc. computer science", "b.sc computer science", "b.sc it"
    ],
    "BCA": [
        "bca", "b.c.a.", "bachelor of computer applications", "bachelor in computer application"
    ],
    "MCA": [
        "mca", "m.c.a.", "master of computer applications", "master in computer application"
    ],
    "M.Tech": [
        "m.tech", "mtech", "m.e.", "me", "master of technology",
        "master of engineering", "post graduate engineering degree"
    ],
    "Diploma": [
        "diploma", "polytechnic", "3-year diploma", "3 year diploma",
        "diploma in engineering", "engineering diploma"
    ],
    "ITI": [
        "iti", "industrial training institute", "ncvt", "scvt", "iti pass"
    ],
    "12th": [
        "12th", "12th pass", "intermediate", "10+2", "+2", "hsc",
        "higher secondary", "senior secondary", "class 12", "class xii"
    ],
    "10th": [
        "10th", "10th pass", "matriculation", "matric", "high school",
        "secondary school", "class 10", "class x", "ssc"
    ],
}

def normalize_degree(qual_str: str) -> Optional[str]:
    """
    Normalizes a qualification string to a canonical degree key if recognized.
    Prevents medical/nursing/law from mapping to general degrees.
    """
    ql = qual_str.lower().strip()
    
    # Check medical guard
    if is_medical_or_nursing_qualification(ql):
        return "Medical/Nursing"
    if is_law_qualification(ql):
        return "Law"

    for canonical, synonyms in CANONICAL_DEGREE_SYNONYMS.items():
        for syn in synonyms:
            # Word boundary regex check
            esc = re.escape(syn).replace(r"\.", r"\.?")
            if re.search(r"(?<!\w)" + esc + r"(?!\w)", ql):
                return canonical
    return None


# ==============================================================================
# 5. BRANCH SYNONYMS & CANONICAL EQUIVALENCES
# ==============================================================================
CANONICAL_BRANCH_ALIASES: Dict[str, List[str]] = {
    "Computer Science": [
        "computer science", "cse", "cs", "computer science & engineering",
        "computer science and engineering", "computer engineering",
        "computer science engineering", "comp sc", "information science",
        "information science & engineering", "information science and engineering"
    ],
    "Information Technology": [
        "information technology", "it", "it engineering",
        "information technology engineering", "information tech"
    ],
    "CS & IT": [
        "computer science & information technology", "computer science and information technology",
        "cs & it", "cs/it", "it & cs", "computer science / information technology",
        "computer science & it", "it & computer science"
    ],
    "Electronics": [
        "electronics", "electronics & communication", "electronics and communication",
        "electronics & communication engineering", "electronics and communication engineering",
        "ece", "electronics & telecommunication", "electronics and telecommunication",
        "electronics & telecommunication engineering", "electronics and telecommunications engineering",
        "e&t", "etc", "electronics & telecom", "electronics and telecom",
        "telecommunication engineering", "telecommunication", "e & t"
    ],
    "Artificial Intelligence": [
        "artificial intelligence", "ai", "machine learning", "ml",
        "ai & ml", "ai and ml", "ai/ml", "data science", "ds",
        "artificial intelligence & machine learning", "artificial intelligence & data science",
        "ai & data science"
    ],
    "Electrical": [
        "electrical engineering", "electrical", "ee", "electrical & electronics",
        "electrical and electronics", "electrical & electronics engineering",
        "electrical and electronics engineering", "eee"
    ],
    "Mechanical": [
        "mechanical engineering", "mechanical", "me", "production engineering"
    ],
    "Civil": [
        "civil engineering", "civil", "ce", "structural engineering"
    ],
    "Chemical": [
        "chemical engineering", "chemical", "che"
    ],
}

ANY_BRANCH_PHRASES = {
    "any branch", "all branches", "any discipline", "all disciplines",
    "any engineering", "any stream", "any specialization",
    "any engineering branch", "all engineering branches",
    "any engineering discipline", "all engineering disciplines",
    "relevant discipline", "any relevant discipline", "all streams",
    "any subject", "all subjects"
}


def get_all_branch_aliases(branch_str: str) -> Set[str]:
    """Returns all lowercase alias variations for a given branch name."""
    b_clean = branch_str.strip().lower()
    res = {b_clean}
    
    # Strip dots/dashes
    res.add(re.sub(r"[\s\.\-]+", "", b_clean))

    for canonical, synonyms in CANONICAL_BRANCH_ALIASES.items():
        syn_lower = [s.lower() for s in synonyms]
        syn_lower.append(canonical.lower())
        if any(s == b_clean or re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", b_clean) for s in syn_lower):
            res.update(syn_lower)

    return res


def extract_disciplines_from_text(text: str) -> List[str]:
    """
    Extracts canonical engineering & technical disciplines mentioned in post titles,
    qualifications, or notification text (e.g., 'Civil', 'Mechanical', 'Electrical', 'Electronics', 'Computer Science').
    """
    if not text:
        return []
    t_lower = text.lower()
    disciplines = []

    # Civil
    if re.search(r"\b(civil|structural)\b", t_lower) or re.search(r"[\(/]\s*ce\s*[\)/]", t_lower):
        disciplines.append("Civil")

    # Mechanical
    if re.search(r"\b(mechanical|production|automobile)\b", t_lower) or re.search(r"[\(/]\s*me\s*[\)/]", t_lower):
        disciplines.append("Mechanical")

    # Electrical
    if re.search(r"\b(electrical|eee)\b", t_lower) or re.search(r"[\(/]\s*ee\s*[\)/]", t_lower):
        disciplines.append("Electrical")

    # Electronics
    if re.search(r"\b(electronics|telecommunication|telecom|ece|etc)\b", t_lower) or "e&tc" in t_lower or "e&c" in t_lower:
        disciplines.append("Electronics")

    # Computer Science & IT
    if re.search(r"\b(computer\s*science|computer\s*engineering|cse|information\s*technology|it\s*engineering|information\s*science)\b", t_lower) or re.search(r"[\(/]\s*(?:cse|it|cs)\s*[\)/]", t_lower):
        disciplines.append("Computer Science")

    # Chemical
    if re.search(r"\b(chemical)\b", t_lower) or re.search(r"[\(/]\s*che\s*[\)/]", t_lower):
        disciplines.append("Chemical")

    # Agriculture
    if re.search(r"\b(agriculture|agricultural)\b", t_lower):
        disciplines.append("Agriculture")

    # Mining
    if re.search(r"\b(mining)\b", t_lower):
        disciplines.append("Mining")

    # Metallurgy
    if re.search(r"\b(metallurgy|metallurgical|material\s*science)\b", t_lower):
        disciplines.append("Metallurgy")

    return disciplines


def branches_overlap(job_branches: List[str], user_branches: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Checks if any branch in job_branches matches user_branches using canonical aliases.
    If the JOB accepts 'Any Branch' / 'All Disciplines', it matches.
    If the JOB requires specific branches, at least one must match the user's declared engineering/technical disciplines.
    """
    if not job_branches:
        return False, None

    # Check if the JOB accepts All Branches / Any Discipline
    for jb in job_branches:
        jb_lower = jb.strip().lower()
        if any(phrase in jb_lower for phrase in ANY_BRANCH_PHRASES):
            return True, f"Job allows All Branches / Any Discipline ({jb})"

    # User's actual technical branches (exclude 'any branch' placeholder from branch alias expansion)
    user_actual_branches = [ub for ub in user_branches if ub.strip().lower() not in ANY_BRANCH_PHRASES]
    user_expanded: Set[str] = set()
    for ub in user_actual_branches:
        user_expanded.update(get_all_branch_aliases(ub))

    for jb in job_branches:
        jb_lower = jb.strip().lower()
        jb_expanded = get_all_branch_aliases(jb)
        overlap = jb_expanded & user_expanded
        if overlap:
            matched_item = next(iter(overlap))
            return True, f"Branch '{jb}' matches '{matched_item}'"

        # Regex token boundary fallback
        for ue in user_expanded:
            if len(ue) >= 3:
                p1 = rf"(?<!\w){re.escape(ue)}(?!\w)"
                p2 = rf"(?<!\w){re.escape(jb_lower)}(?!\w)"
                if re.search(p1, jb_lower) or re.search(p2, ue):
                    return True, f"Branch '{jb}' matches '{ue}'"

    return False, None


# ==============================================================================
# 6. NON-JOB ANNOUNCEMENT DETECTOR (Admit Cards, Results, Answer Keys)
# ==============================================================================
NON_JOB_TITLE_PATTERNS = [
    r"\badmit\s*card\b",
    r"\bhall\s*ticket\b",
    r"\bcall\s*letter\b",
    r"\banswer\s*key\b",
    r"\bresult\s*out\b",
    r"\bresult\s*announced\b",
    r"\bscore\s*card\b",
    r"\bexam\s*date\s*(?:notice|out)?\b",
    r"\bpet\s*/\s*pst\s*admit\b",
    r"\bphysical\s*admit\s*card\b",
    r"\bcutoff\s*marks\b",
    r"\bsyllabus\b",
    r"\bexam\s*schedule\b",
    r"\binterview\s*schedule\b",
]

def is_non_job_announcement(title: Optional[str], text: Optional[str], url: Optional[str]) -> bool:
    """
    Deterministically identifies if content represents an exam result, admit card,
    answer key, or syllabus rather than an active recruitment vacancy.
    """
    candidates = []
    if title:
        candidates.append(title.lower())
    if url:
        candidates.append(url.lower())
    if text:
        # Check first 3 lines of text
        lines = [line.strip().lower() for line in text.strip().split("\n") if line.strip()][:5]
        candidates.extend(lines)

    for c in candidates:
        for pat in NON_JOB_TITLE_PATTERNS:
            if re.search(pat, c):
                # Ensure it's not a vacancy notification merely mentioning an exam date
                if "vacancy" in c or "recruitment" in c or "notification out" in c or "posts" in c:
                    # If it explicitly says 'admit card out' or 'answer key out', it's non-job
                    if re.search(r"\b(admit\s*card|answer\s*key|result)\s*out\b", c):
                        return True
                    if re.search(r"\bdownload\s*(?:admit\s*card|hall\s*ticket|answer\s*key)\b", c):
                        return True
                else:
                    return True
    return False


# ==============================================================================
# 7. GOVERNMENT CATEGORY & RESERVATION NORMALIZATION
# ==============================================================================
CATEGORY_ALIASES: Dict[str, str] = {
    "general": "General",
    "ur": "General",
    "unreserved": "General",
    "oc": "General",
    "open": "General",
    "obc": "OBC",
    "obc-ncl": "OBC",
    "other backward class": "OBC",
    "other backward classes": "OBC",
    "sc": "SC",
    "scheduled caste": "SC",
    "st": "ST",
    "scheduled tribe": "ST",
    "ews": "EWS",
    "economically weaker section": "EWS",
    "pwd": "PwD",
    "pwbd": "PwD",
    "ph": "PwD",
    "divyang": "PwD",
    "esm": "Ex-Serviceman",
    "ex-serviceman": "Ex-Serviceman",
    "ex serviceman": "Ex-Serviceman",
}

def normalize_category(cat: str) -> str:
    """Normalizes government category strings into standard keys."""
    cl = cat.strip().lower()
    return CATEGORY_ALIASES.get(cl, cat.strip())
