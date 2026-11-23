"""ScamGuard core: text normalisation, explainable red flags and the local Detector.
Pure offline code: no network modules are imported anywhere in this file."""
import re, time, unicodedata
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).with_name("model.joblib")
CATEGORY = {"KYC": "KYC/Bank", "LOTTERY": "Lottery/Prize", "LOAN": "Loan/Credit",
            "JOB": "Job/Investment", "OTHER": "Other"}

SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy",
              "shorturl.at", "tiny.cc", "ow.ly", "short.fyi", "bl.ink", "rebrand.ly")
BAD_TLDS = ("xyz", "top", "club", "online", "site", "link", "info", "cc", "fyi", "icu", "live", "click")
URL_RE = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+(?:\.[\w-]+)*\.(?:com|in|co|net|org|xyz|top|club|online|"
                    r"site|link|info|ly|gl|me|app|cc|fyi|icu|live|click|page|is|gd)\b(?:/\S*)?", re.I)
TOLL_RE = re.compile(r"(?<!\d)1800[\s-]?\d{3}[\s-]?\d{3,4}(?!\d)")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)")
AMT_RE = re.compile(r"(?:rs\.?|inr|₹)\s*(\d[\d,]*(?:\.\d+)?)(\s*(?:lakh|lacs?|crore|cr)\b)?|"
                    r"(\d[\d,]*)\s*(?:rs|rupees|lakh|lacs?)\b", re.I)
HOMOGLYPH = str.maketrans("аеорсхіѕԁ", "aeopcxisd")
LEET = str.maketrans("013457@$", "oieastas")
SPACED = re.compile(r"\b(?:[a-z][\s.\-_*]){2,}[a-z]\b")
ZERO_W = re.compile("[\u200b-\u200f\u2060\ufeff]")


def _url(m):
    u = m.group(0).lower()
    host = re.sub(r"^(?:https?://)?(?:www\.)?", "", u).split("/")[0]
    if host.startswith(SHORTENERS):
        return " zurl zshort "
    tld = host.rsplit(".", 1)[-1]
    sus = "-" in host or tld in BAD_TLDS or bool(re.search(r"[a-z]\d+[a-z]|\d{3,}", host))
    return f" zurl {'zsus ' if sus else ''}{re.sub(r'[^a-z]+', ' ', host)} "


def _amt(m):
    digits = (m.group(1) or m.group(3) or "0").replace(",", "").split(".")[0] or "0"
    big = m.group(2) or "lakh" in m.group(0).lower() or int(digits) >= 10000
    return " zamt zbig " if big else " zamt "


def _leet(m):
    w = m.group(0)
    return w if re.match(r"\d{2}|\d+[a-z]{1,3}$", w) else w.translate(LEET)


def normalize(text: str) -> str:
    """Canonical form: defeats leetspeak, spaced/dotted letters, homoglyphs; masks links, phones, amounts."""
    t = ZERO_W.sub("", unicodedata.normalize("NFKC", text)).translate(HOMOGLYPH).lower()
    t = SPACED.sub(lambda m: re.sub(r"[\s.\-_*]", "", m.group(0)), t)
    t = URL_RE.sub(_url, t)
    t = TOLL_RE.sub(" ztoll ", t)
    t = PHONE_RE.sub(" zphone ", t)
    t = AMT_RE.sub(_amt, t)
    t = re.sub(r"(?<=[a-z])[@$](?=[a-z])", lambda m: m.group(0).translate(LEET), t)
    t = re.sub(r"\b(?=\w*[a-z])(?=\w*\d)\w+\b", _leet, t)
    t = re.sub(r"\b\d{4,8}\b", " znum ", t)
    return re.sub(r"\s+", " ", t).strip()


FLAGS = [  # (regex on normalised text, explanation)
    (r"\bzshort\b", "Shortened link hides the real destination"),
    (r"\bzsus\b", "Link domain looks fake or suspicious"),
    (r"urgent|immediately|expire|within \d+ ?(?:hrs?|hours|min)|tonight|turant|jaldi|last chance|final reminder|abhi",
     "Creates urgency / pressure"),
    (r"block|suspend|deactivat|disconnect|freez|band ho|kat jayega|arrest|disabled|on hold|inform your contacts",
     "Threatens to block, cut off or punish"),
    (r"(?:share|send|give).{0,25}(?:otp|pin|cvv|password)|bank details|card number|account number",
     "Asks for OTP, PIN or bank details"),
    (r"\b(?:fee|charge|charges|deposit|registration|processing|insurance|clearance)\b",
     "Asks for money upfront"),
    (r"\bwon\b|winner|lottery|lucky draw|prize|inaam|jeet|congratulations|badhai|gift voucher",
     "Unexpected prize or reward"),
    (r"guarantee|no documents|per day|daily|double your|0% interest|without cibil|ghar baithe|roz\b|no experience",
     "Offer is too good to be true"),
    (r"(?:call|contact|whatsapp|msg|message).{0,20}zphone", "Pushes you to contact an unknown number"),
]
SAFE_FLAGS = [
    (r"do not share|never share|don.t share|not share", "Warns you not to share the OTP (typical of genuine alerts)"),
    (r"(?:debited|credited).{0,40}(?:a/c|acct|account)|(?:a/c|account).{0,40}(?:debited|credited)",
     "Matches a normal transaction alert with no link or request"),
]


def reasons(norm: str, scam: bool, limit=4):
    out = [msg for rx, msg in (FLAGS if scam else SAFE_FLAGS) if re.search(rx, norm)]
    return out[:limit] or (["Language patterns match known scams"] if scam else ["No scam patterns found"])


class Detector:
    def __init__(self, path=MODEL_PATH):
        self.pipe = joblib.load(path)

    def predict(self, text: str) -> dict:
        t0 = time.perf_counter()
        norm = normalize(text or "")
        if not norm:
            return {"verdict": "SAFE", "category": None, "confidence": 50.0, "reasons": ["Empty message"], "ms": 0}
        probs = dict(zip(self.pipe.classes_, self.pipe.predict_proba([text])[0]))
        p_scam = 1 - probs["SAFE"]
        scam = p_scam >= 0.5
        cat = None
        if scam:
            cat = max((c for c in probs if c != "SAFE"), key=probs.get)
            if probs[cat] / p_scam < 0.5:  # no clear scam type -> honest "Other"
                cat = "OTHER"
            cat = CATEGORY[cat]
        return {"verdict": "SCAM" if scam else "SAFE", "category": cat,
                "confidence": round(float(100 * (p_scam if scam else 1 - p_scam)), 1),
                "reasons": reasons(norm, scam), "ms": round((time.perf_counter() - t0) * 1000, 1)}
