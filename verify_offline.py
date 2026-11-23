"""Proof of offline, private operation. Run: python verify_offline.py
1) static check: core code imports no networking module
2) runtime check: every socket operation is made to raise, then the detector must still work."""
import ast, socket, sys

NET = {"socket", "requests", "urllib", "urllib3", "http", "httpx", "aiohttp", "ftplib", "smtplib", "websocket", "websockets"}
tree = ast.parse(open("scamguard.py", encoding="utf-8").read())
found = {(n.names[0].name if isinstance(n, ast.Import) else n.module or "").split(".")[0]
         for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))} & NET
print("[1] network imports in scamguard.py:", sorted(found) or "none")

calls = []
def blocked(*a, **k):
    calls.append(a); raise OSError("network access blocked by verify_offline.py")
for name in ("connect", "connect_ex", "send", "sendall", "sendto", "bind"):
    setattr(socket.socket, name, blocked)
socket.create_connection = socket.getaddrinfo = socket.gethostbyname = blocked

from scamguard import Detector
d = Detector()
tests = ["Your SBI KYC expired, update at bit.ly/abc or account blocked", "Bhai kal milte hain 7 baje"]
print("[2] predictions with all sockets blocked:", [d.predict(t)["verdict"] for t in tests])
print("    network attempts:", len(calls))
ok = not found and not calls
print("RESULT:", "PASS - fully offline" if ok else "FAIL"); sys.exit(0 if ok else 1)
