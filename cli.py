"""Usage: python cli.py "message text"   (or pipe text via stdin)"""
import sys, json
from scamguard import Detector
print(json.dumps(Detector().predict(" ".join(sys.argv[1:]) or sys.stdin.read()), indent=2, ensure_ascii=False))
