"""Local UI: python app.py  ->  http://127.0.0.1:8000  (binds to loopback only, standard library only)."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from scamguard import Detector

DET = Detector()
PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>ScamGuard</title><style>
:root{--ink:#10243e;--mute:#5b6b7e;--line:#d5dde6;--bg:#f3f6f9;--bad:#c4122f;--good:#12794a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,Segoe UI,Roboto,sans-serif}
main{max-width:640px;margin:0 auto;padding:28px 18px 48px}h1{font-size:26px;margin:0}p.sub{color:var(--mute);margin:4px 0 18px}
.pill{display:inline-block;font-size:13px;border:1px solid var(--good);color:var(--good);border-radius:99px;padding:1px 10px;margin-left:8px;vertical-align:middle}
textarea{width:100%;min-height:130px;padding:12px;border:1px solid var(--line);border-radius:8px;font:inherit;resize:vertical}
textarea:focus,button:focus-visible{outline:3px solid #7aa7e0;outline-offset:1px}
.row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}button{font:inherit;border-radius:8px;border:1px solid var(--ink);padding:9px 16px;cursor:pointer}
#go{background:var(--ink);color:#fff}.ex{background:#fff;border-color:var(--line);font-size:14px;padding:5px 10px}
#out{display:none;margin-top:18px;background:#fff;border:1px solid var(--line);border-left:8px solid var(--c);border-radius:8px;padding:16px 18px}
#v{font-size:44px;font-weight:800;color:var(--c);line-height:1}#cat{font-size:18px;margin-left:10px}
.bar{height:10px;background:var(--line);border-radius:9px;margin:12px 0 4px;overflow:hidden}.bar i{display:block;height:100%;background:var(--c);transition:width .35s}
ul{margin:10px 0 0;padding-left:20px}small{color:var(--mute)}</style>
<main><h1>ScamGuard<span class=pill>Runs on this device</span></h1>
<p class=sub>Paste an SMS or WhatsApp message. Nothing leaves your computer.</p>
<textarea id=t placeholder="Paste a message here" autofocus></textarea>
<div class=row><button id=go>Check message</button></div>
<div class=row id=ex></div>
<section id=out aria-live=polite><span id=v></span><span id=cat></span>
<div class=bar><i id=b></i></div><small id=conf></small><ul id=why></ul></section></main>
<script>
const S=["Dear customer, your SBI KYC has expired. Update now or account will be blocked: bit.ly/sbi-kyc",
"Congratulations! Aapne Rs.25 lakh ka lucky draw jeeta hai. Claim: +91 9876543210",
"U.P.I. refund pending, Upd4te b4nk details n0w: sbi-verify.xyz",
"483920 is your OTP for HDFC Bank login. Do not share it with anyone.",
"Bhai kal 7 baje milte hain, paisa kal bhej dunga"];
const $=i=>document.getElementById(i);
S.forEach(s=>{const b=document.createElement("button");b.className="ex";b.textContent=s.slice(0,28)+"…";b.onclick=()=>{$("t").value=s;check()};$("ex").append(b)});
async function check(){const m=$("t").value.trim();if(!m)return;
 const r=await (await fetch("/predict",{method:"POST",body:JSON.stringify({message:m})})).json();
 const bad=r.verdict=="SCAM";$("out").style.setProperty("--c",bad?"var(--bad)":"var(--good)");$("out").style.display="block";
 $("v").textContent=r.verdict;$("cat").textContent=r.category?"Type: "+r.category:"";
 $("b").style.width=r.confidence+"%";$("conf").textContent=r.confidence+"% confident · "+r.ms+" ms · analysed locally";
 $("why").innerHTML="";r.reasons.forEach(x=>{const l=document.createElement("li");l.textContent=x;$("why").append(l)})}
$("go").onclick=check;$("t").onkeydown=e=>{if(e.key=="Enter"&&(e.ctrlKey||e.metaKey))check()};
</script>"""

class H(BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        self.send_response(200); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self): self._send(PAGE.encode(), "text/html; charset=utf-8")
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        msg = json.loads(self.rfile.read(n) or b"{}").get("message", "")[:5000]
        self._send(json.dumps(DET.predict(msg)).encode(), "application/json")
    def log_message(self, *a): pass

if __name__ == "__main__":
    print("ScamGuard running at http://127.0.0.1:8000  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", 8000), H).serve_forever()
