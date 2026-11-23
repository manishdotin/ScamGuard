"""Hand-written sanity set (wordings NOT in the generator) + confidence calibration check."""
from scamguard import Detector

SET = [  # (message, expected: SAFE or category)
("Dear SBI user, your YONO account is suspended. Complete KYC today at sbi-yono-kyc.top or it will be closed", "KYC/Bank"),
("Aapka HDFC account kal band ho jayega, PAN verify karne ke liye bit.ly/hd-pan abhi click karein", "KYC/Bank"),
("ALERT: Rs 49,999 debited from ur a/c. If not you, call 9811122233 to block card immediately", "KYC/Bank"),
("Ur Paytm KYC expired. Upd4te n0w or wallet will be fr0zen: tinyurl.com/pt-kyc", "KYC/Bank"),
("H D F C  B a n k: your netbanking is locked. Verify at hdfc-secure-login.xyz", "KYC/Bank"),
("Congratulations!! You've won Rs.25,00,000 in WhatsApp Lucky Draw. Contact claim officer +91 9988776655", "Lottery/Prize"),
("Aapko Amazon se Rs 5000 ka gift card mila hai, collect karein: cutt.ly/amzn-gift", "Lottery/Prize"),
("You are the lucky winner of a brand new Royal Enfield! Pay Rs.999 registration to claim", "Lottery/Prize"),
("W1N a free iPh0ne 15 n0w!! Click here: rb.gy/x9k2", "Lottery/Prize"),
("Pre-approved loan Rs 3,00,000 for you. Zero documents, money in 10 mins. Apply: quickcash-loan.online", "Loan/Credit"),
("Your loan has been sanctioned. Send Rs 2500 processing fee to release the amount to your account", "Loan/Credit"),
("Loan lena hai? 5 minute me paisa account me, sirf Aadhaar chahiye. Call 8877665544", "Loan/Credit"),
("Repay your overdue loan today otherwise we will send your photos to all your contacts", "Loan/Credit"),
("Earn Rs 3000 daily from home just by rating hotels on Google. Message HR on WhatsApp 9090909090", "Job/Investment"),
("Hiring: Amazon part-time workers, salary 20k-40k monthly. Deposit Rs 500 for ID card. t.me/amzjobs", "Job/Investment"),
("Join our crypto signals group, 5x returns in 2 weeks, 100% guaranteed. bit.ly/cryptovip", "Job/Investment"),
("Ghar baithe mobile se kamaye 1000 rupees roz, koi investment nahi. Abhi join karo wa.me/919876501234", "Job/Investment"),
("Your electricity bill is unpaid, power will be cut at 9:30 tonight. Call officer 9123456780 now", "Other"),
("Dear customer your package is held at Mumbai customs, pay Rs 1,850 duty to release: indiapost-track.top", "Other"),
("Cyber Crime Branch: your Aadhaar is used in a money laundering case. Join video call or you will be arrested", "Other"),
("Sir I sent money to your number by mistake, please send it back to my UPI 9871234560 urgently", "Other"),
("Your FASTag wallet is blocked, recharge now at fastag-update.site to avoid penalty", "Other"),
("HDFC Bank: Rs.1,250.00 debited from A/c XX4821 on 21-Nov-26 at Swiggy. Not you? Call 1800-202-6161", "SAFE"),
("483920 is your OTP for Amazon login. Do not share it with anyone.", "SAFE"),
("Your SBI Credit Card ending 4412 payment of Rs.8,400 is received. Thank you.", "SAFE"),
("Your Flipkart order for boAt Airdopes will be delivered tomorrow between 10 AM-2 PM", "SAFE"),
("Dear customer, your KYC has been updated successfully. No further action needed. -ICICI Bank", "SAFE"),
("Your Airtel recharge of Rs.299 is successful. Validity till 20-Dec. Visit airtel.in/app", "SAFE"),
("Your DTDC consignment D12345678 is out for delivery. Contact agent 9812345670 for any query", "SAFE"),
("Rs.2,000 credited to your account by UPI from Rohan. Avl bal Rs.14,820 - Axis Bank", "SAFE"),
("hey are u free tonight? movie plan hai, tickets maine book kar diye", "SAFE"),
("bro send me the pdf asap, submission is in 1 hour", "SAFE"),
("Mummy bol rahi thi ki bijli ka bill aaj bhar dena warna connection kat jayega", "SAFE"),
("Congratulations on winning the hackathon!! Treat chahiye bhai", "SAFE"),
("Urgent: team meeting at 3 PM today, join here meet.google.com/xyz-abcd-efg", "SAFE"),
("Interview scheduled for Data Analyst at TCS on Monday 10 AM. Please carry your resume and ID.", "SAFE"),
("Can you lend me Rs 500? Will pay back tomorrow, my UPI isn't working", "SAFE"),
("Your Uber ride is arriving. Driver Ramesh, KA01AB1234. Share OTP 4821 only with the driver.", "SAFE"),
("Dear student, your exam hall ticket is available on the college portal. Download before 25 Nov.", "SAFE"),
("Your Jio fiber bill of Rs.999 is due on 28-Nov. Pay on MyJio app to avoid late fee.", "SAFE"),
("Aaj office jaldi nikalna hai, doctor appointment hai 5 baje", "SAFE"),
("Reminder: your LIC premium of Rs.5,200 is due on 30-Nov. Pay via licindia.in or nearest branch.", "SAFE"),
]

if __name__ == "__main__":
    d = Detector(); ok = fp = fn = cat_ok = scams = 0; bins = {}
    for msg, exp in SET:
        r = d.predict(msg); pred = r["category"] if r["verdict"] == "SCAM" else "SAFE"
        ok += (r["verdict"] == "SCAM") == (exp != "SAFE")
        if exp != "SAFE":
            scams += 1; cat_ok += pred == exp
        if (pred == "SAFE") != (exp == "SAFE") or (exp != "SAFE" and pred != exp):
            print(f"MISS  exp={exp:14} got={pred:14} {r['confidence']:5}%  {msg[:70]}")
        b = min(int(r["confidence"] // 10 * 10), 90); hit = (r["verdict"] == "SCAM") == (exp != "SAFE")
        bins.setdefault(b, []).append(hit)
    print(f"\nVerdict accuracy {ok}/{len(SET)} | category accuracy on scams {cat_ok}/{scams}")
    print("Calibration (stated confidence bin -> actual accuracy):")
    for b in sorted(bins): print(f"  {b:3}-{b+10:3}%: {sum(bins[b])/len(bins[b]):.0%}  (n={len(bins[b])})")
