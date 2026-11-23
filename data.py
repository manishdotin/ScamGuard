"""Template-based synthetic corpus (English + Hinglish + obfuscation). Templates, not messages, are split
into train/test so evaluation is on *unseen* wordings. Drop extra real data in extra.csv (text,label)."""
import random, string

BANKS = ["SBI", "HDFC Bank", "ICICI", "Axis Bank", "PNB", "Kotak", "Bank of Baroda", "Paytm", "PhonePe", "Canara Bank"]
NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Neha", "Arjun", "Pooja", "Suresh", "Anita"]
MERCH = ["Amazon", "Flipkart", "Swiggy", "Zomato", "BigBasket", "Myntra", "Uber", "IRCTC"]
COURIER = ["BlueDart", "Delhivery", "India Post", "DTDC", "Ecom Express"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

T = {
"KYC": [
 "Dear customer, your {b} account will be blocked today. Update your KYC immediately: {u}",
 "URGENT: {b} KYC expired. Complete verification within 24 hrs or account will be suspended. Click {u}",
 "Dear user your {b} net banking is deactivated. Update PAN card now {u}",
 "Your {b} debit card is blocked. Call {p} to reactivate immediately",
 "Aapka {b} account band ho jayega. Turant KYC update karein: {u}",
 "{b} Alert: Aapka PAN update nahi hai, account freeze hoga. Abhi link par click karein {u}",
 "Your Aadhaar is not linked with {b}. Link now to avoid account suspension {u}",
 "Dear customer, ur {b} a/c is on hold. Share OTP {n} with our executive to verify KYC",
 "{b}: Your credit card reward points of {a} will expire today. Redeem now {u}",
 "Your UPI id will be disabled. Verify your bank details here {u}",
 "Dear customer your SIM KYC is incomplete, number will be blocked in 2 hours. Call {p}",
 "{b} account suspicious login detected. Verify your identity or card will be locked {u}",
 "Dear sir/madam, aapka bank khata block ho gaya hai. Apna card number aur CVV bhejein"],
"LOTTERY": [
 "Congratulations! You have won {a} in the {b} lucky draw. Claim your prize now {u}",
 "You are selected as lucky winner of KBC lottery {a}. Contact {p} on WhatsApp to claim",
 "Badhai ho! Aapne {a} ka inaam jeeta hai. Claim karne ke liye {u} par click karein",
 "WINNER! Your mobile number won iPhone 15 in Jio anniversary offer. Pay {f} delivery fee {u}",
 "Dear user, you got a gift voucher worth {a} from Amazon. Claim before it expires {u}",
 "Lucky draw result: number {p} won {a}. Send your bank details to receive the money",
 "Free recharge of {a} for all Jio users! Click {u} to get it now",
 "Aapka number lucky draw me select hua hai, {a} jeetne ke liye jaldi register karo {u}",
 "You have been chosen for a free gift hamper! Pay only {f} shipping to receive {u}"],
"LOAN": [
 "Pre-approved personal loan of {a} at 0% interest. No documents needed. Apply now {u}",
 "Instant loan {a} in 5 minutes! Only Aadhaar needed. Apply {u}",
 "Aapka loan {a} approved ho gaya hai. Processing fee {f} bhejein aur paisa turant paayein {u}",
 "Congratulations your credit limit increased to {a}. Activate by paying small fee {u}",
 "Need urgent cash? Get {a} loan without CIBIL check. Call {p}",
 "Loan approved! Pay insurance charge of {f} to release {a} to your account {u}",
 "Final reminder: pay your pending loan today or we will inform your contacts and family. {u}",
 "Aapka loan pending hai, abhi repay karo warna aapke contacts ko message jayega {u}",
 "Get {a} credit card limit instantly, zero paperwork, guaranteed approval. Click {u}"],
"JOB": [
 "Work from home! Earn {a} daily by liking videos. Join our Telegram {u}",
 "Part time job offer: earn {d} per day. No experience required. WhatsApp {p}",
 "Hiring data entry executives. Salary {a} per month. Pay {f} registration fee {u}",
 "Ghar baithe kamaye {d} roz. Sirf mobile chahiye. Abhi join karein {u}",
 "Invest Rs.5000 and get {a} in 7 days guaranteed returns. Join our VIP trading group {u}",
 "Dear candidate, you are shortlisted by Amazon for work from home. Message HR on WhatsApp {p}",
 "Crypto trading tips: double your money in 10 days, 100% profit guaranteed. {u}",
 "Aapko job mil gayi hai, joining fee {f} jama karein {u}",
 "Task based job: complete simple tasks and earn commission. Deposit {f} to start {u}",
 "Stock market expert tips, 300% returns assured. Join premium group {u}"],
"OTHER": [
 "Your electricity will be disconnected tonight 9:30 PM due to unpaid bill. Call {p} immediately",
 "Your parcel is held at customs. Pay {f} clearance fee to release {u}",
 "This is CBI. A parcel in your name has illegal items. You are under digital arrest. Call {p}",
 "Hi, I accidentally sent {a} to your UPI. Please return it to {p}",
 "Dear customer, your FASTag is blocked. Recharge now via {u}",
 "I have your private videos. Pay {f} or I will send them to all your contacts",
 "Microsoft alert: your computer is infected. Call tech support {p} now",
 "Income tax refund of {a} is pending. Submit bank details {u} to receive",
 "Aapka bijli ka bill pending hai, connection aaj raat kat jayega. Call {p}",
 "Courier delivery failed. Reschedule and pay {f} redelivery fee {u}",
 "Hello dear, new number here. Remember me? Click {u} to see my photos"],
"SAFE": [
 "{b}: Rs.{x} debited from A/c XX{n4} on {dt} to {nm}. UPI Ref {n}. Not you? Call 1800-123-4567",
 "Rs.{x} credited to your A/c XX{n4} on {dt}. Avl Bal Rs.{x}. -{b}",
 "{n} is your OTP for login to {b}. Do not share it with anyone. Valid for 10 minutes.",
 "OTP {n} for transaction of Rs.{x} at {m}. Never share OTP with anyone, including bank staff.",
 "Your {b} credit card statement for {mon} is generated. Total due Rs.{x}, due date {dt}. Pay via official app.",
 "{b}: KYC verification completed for your account. No action is required.",
 "Your KYC details were updated on {dt}. Thank you for choosing {b}.",
 "Your KYC has been successfully updated. Thank you for banking with {b}.",
 "Dear customer, your EMI of Rs.{x} has been debited successfully from {b}. Thank you.",
 "Reminder: KYC re-verification is due. Please visit your nearest {b} branch with ID proof. We never ask for OTP or card details.",
 "Your {m} order #{n} has been shipped and will arrive by {dt}. Track in the app.",
 "Delivered: your {m} package was delivered today. Rate your experience.",
 "Your {m} order is on the way. Rider {nm} will reach in 10 mins. Delivery OTP is {n4}.",
 "Your {c} shipment AWB {n} is out for delivery today.",
 "Dear customer, your Jio plan of Rs.{x} is recharged successfully. Validity 28 days.",
 "Your Airtel bill of Rs.{x} is due on {dt}. Pay through the Airtel Thanks app.",
 "Your electricity bill of Rs.{x} for {mon} has been paid. Thank you.",
 "Appointment reminder: Dr. {nm} tomorrow at 5 PM at Apollo Clinic.",
 "Your IRCTC ticket PNR {n} is confirmed. Train departs {dt}.",
 "{m}: Your sale starts tomorrow. Shop top deals at {su}",
 "Hey are you coming for dinner tonight?",
 "Can you send me the notes from yesterday's class?",
 "Happy birthday {nm}! Have a great year ahead",
 "Meeting moved to 4 PM, please join the call {su}",
 "Urgent: please submit the report by 5 PM today, client is waiting.",
 "Call me asap, it's about dad's tests",
 "I'll transfer Rs.{x} for rent tonight, sending now",
 "Did you see the match yesterday? What a finish",
 "Bhai kal milte hain, 7 baje cafe me",
 "Kya kar raha hai? Aaj raat movie chalein?",
 "Mummy ka call aaya tha, ghar jaldi aana",
 "Paisa kal bhej dunga yaar, abhi tight hai",
 "Office se nikal gaya, 20 min me pahunch jaunga",
 "Assignment submit kar diya? Deadline kal hai",
 "Bhaiya, parcel gate pe chhod dena",
 "Aaj ka lunch bahar karenge kya? Jaldi bata",
 "{b}: Your cheque no {n} for Rs.{x} has been cleared.",
 "Your {m} refund of Rs.{x} has been processed to your original payment method in 3-5 days.",
 "Loan EMI reminder: Rs.{x} due on {dt}. Ignore if already paid. -{b}",
 "Hi {nm}, your table for 4 is booked at 8 PM tonight. See you!",
 "Your Ola ride is arriving in 3 mins. Driver {nm}, OTP {n4}.",
 "Your Netflix subscription renewed for Rs.{x}. Thanks for watching!",
 "Class cancelled tomorrow due to heavy rain",
 "Reached home safely. Thanks for the lift!",
 "Congratulations {nm}! So proud of you for the promotion",
 "Congratulations on the new job! Party kab de raha hai?",
 "Won 50 rupees in the lottery lol, treat on me",
 "Please update the KYC form on your side and send me the scanned copy",
 "Your OTP for {m} is {n}. Valid for 5 mins.",
 "Verification code {n}. Do not share this code with anyone.",
 "Bhai job ke liye apply kar diya, interview Monday hai",
 "Work from home today, joining the 11 AM standup {su}",
 "Naya loan nahi lena yaar, EMI ka tension hai",
 "Your Zerodha contract note for {dt} is ready. Login to Console to view.",
 "Kal bijli ka bill bhar dena, last date 25 hai",
 "Reminder: electricity bill due {dt}. Pay only via the official app or website.",
 "Loan ke papers bank me jama kar diye, approval ka wait hai",
 "Mujhe {x} rupees chahiye urgent, kal subah return kar dunga",
 "Your {b} account statement for {mon} is ready. Open the PDF with your date of birth."],
}

# Composable fragments: hook (class-specific) + urgency + call-to-action (shared) -> far more varied scams
H = {
"KYC": ["Your {b} account is not verified", "Aapka {b} account verify nahi hua hai", "Dear {b} customer, your PAN is not updated",
        "{b} KYC pending", "Your {b} net banking access has been restricted", "Your {b} debit card has expired",
        "Your Aadhaar is not linked to your bank account", "{b} Alert: unauthorized transaction of {a} detected",
        "Aapka SIM aur bank KYC adhoora hai", "Your {b} mobile banking will be discontinued"],
"LOTTERY": ["Congratulations, you are today's lucky winner of {a}", "Aapko {a} ka inaam mila hai",
        "You have won a free iPhone in our festival lucky draw", "Your number was selected for a cash reward of {a}",
        "Aapne cashback jeeta hai {a}", "Mega prize alert: {a} waiting for you", "You are our 1,000,000th visitor, claim your gift",
        "Scratch card reward of {a} unlocked", "Aapka gift voucher {a} ka ready hai"],
"LOAN": ["Your loan of {a} is pre-approved", "Aapka {a} ka personal loan sanction ho gaya hai",
        "Get an instant loan up to {a} with low interest", "Your credit limit has been upgraded to {a}",
        "Loan chahiye? {a} tak turant paisa", "Dear borrower, your loan repayment is overdue",
        "Need money urgently? Easy loan, no CIBIL score check", "Aapka overdue loan abhi tak nahi bhara gaya hai"],
"JOB": ["Earn {d} per day working from home", "Part time job: just like and share posts",
        "We are hiring for online typing job, salary {a} monthly", "Ghar se kaam karke roz {d} kamayein",
        "Invest small and earn big profits every week", "Bitcoin trading made easy, earn {d} daily",
        "You are selected for a task-based job at Flipkart", "Naukri ka mauka: bina experience ke salary {a}",
        "Join our stock tips group for guaranteed profit", "Amazon is hiring, no interview needed"],
"OTHER": ["Your electricity connection will be cut", "Your gas connection will be stopped for unpaid bill",
        "Your parcel from abroad is stuck at customs", "Aapka courier address galat hai, delivery ruk gayi hai",
        "This is Delhi Police cyber cell. Your number is linked to a crime", "We have recorded your video, you will be exposed",
        "Your Netflix payment failed, account will be cancelled", "Your Windows license has expired, virus detected",
        "You have a pending traffic challan of {a}", "Dear customer, your gas subsidy of {a} is pending",
        "Your WhatsApp will be deactivated"]}
URG = ["Act now.", "Do it immediately.", "Offer expires today.", "Last chance!", "Within 24 hours or action will be taken.",
       "Turant action lein.", "Jaldi karein, time kam hai.", "Don't ignore this message.", "Urgent!", "Limited slots left.",
       "Only today.", "Abhi respond karein warna nuksan hoga."]
CTA = ["Click {u}", "Visit {u}", "Call {p} now", "WhatsApp {p}", "Reply with your details", "Tap here: {u}",
       "Link par click karein {u}", "Contact {p}", "Apply: {u}", "Share your OTP to proceed",
       "Send your Aadhaar and PAN photo to {p}", "Pay processing fee {f} at {u}", "Pay {f} via UPI to {p}"]

def _rand(r, n, chars=string.ascii_letters + string.digits):
    return "".join(r.choice(chars) for _ in range(n))

def _slots(r, label):
    b = r.choice(BANKS)
    word = r.choice(["kyc", "update", "verify", "secure", "login", "claim", "offer"])
    bank_slug = b.lower().replace(" ", "")
    tld = r.choice(["in", "xyz", "top", "online", "com", "co.in", "site", "club"])
    scam_links = [f"bit.ly/{_rand(r,6)}", f"https://tinyurl.com/{_rand(r,7)}", f"cutt.ly/{_rand(r,5)}",
                  f"{bank_slug}-{word}.{tld}", f"www.{bank_slug}{r.randint(10,99)}-{word}.{tld}",
                  f"https://{bank_slug}.{word}-{_rand(r,4,string.ascii_lowercase)}.{tld}/login"]
    safe_links = ["hdfcbank.com/app", "amazon.in/orders", "flipkart.com", "paytm.com", "sbi.co.in", "meet.google.com/abc-defg"]
    amt = r.choice([f"Rs.{r.randint(1,50)*1000:,}", f"Rs {r.randint(10,99)*1000}", f"₹{r.randint(1,25)} lakh", f"{r.randint(1,9)*10000} rupees"])
    return dict(b=b, a=amt, f=f"Rs.{r.choice([99,199,499,999,1500,2999])}", d=f"Rs.{r.choice([500,800,1500,3000,5000])}",
                u=r.choice(scam_links) if label != "SAFE" else r.choice(safe_links) if r.random() < .6 else r.choice(scam_links[:1]),
                su=r.choice(safe_links), p=r.choice(["", "+91 "]) + str(r.randint(6, 9)) + _rand(r, 9, string.digits),
                n="".join(r.choice(string.digits) for _ in range(6)), n4=_rand(r, 4, string.digits),
                x=f"{r.randint(1,99999):,}", nm=r.choice(NAMES), m=r.choice(MERCH), c=r.choice(COURIER),
                mon=r.choice(MONTHS), dt=f"{r.randint(1,28)}-{r.choice(MONTHS)}-26")

KEYWORDS = ["kyc", "otp", "blocked", "update", "loan", "lottery", "winner", "claim", "verify", "account", "click", "bank", "urgent", "prize"]
LEET = str.maketrans("aeiosAEIOS", "4310$4310$")
HOMO = str.maketrans("aeopc", "аеорс")

def obfuscate(s, r):
    mode = r.choice(["leet", "space", "dots", "caps", "homo", "emoji", "plain"])
    if mode == "leet":
        return "".join(c.translate(LEET) if r.random() < .5 else c for c in s)
    if mode in ("space", "dots"):
        for k in r.sample(KEYWORDS, 3):
            i = s.lower().find(k)
            if i >= 0:
                s = s[:i] + ("." if mode == "dots" else " ").join(s[i:i + len(k)]) + s[i + len(k):]
        return s
    if mode == "caps": return "".join(c.upper() if r.random() < .5 else c.lower() for c in s)
    if mode == "homo": return "".join(c.translate(HOMO) if r.random() < .5 else c for c in s)
    if mode == "emoji": return r.choice(["🚨 ", "⚠️ ", "✅ ", "💰 "]) + s
    return "".join(c for c in s.lower() if c not in ".,!:")

def _compose(hook, r):
    parts = [hook] + ([r.choice(URG)] if r.random() < .5 else []) + ([r.choice(CTA)] if r.random() < .9 else [])
    return ". ".join(p.rstrip(".") for p in parts)

def generate(per_template=60, seed=0, holdout=0.25):
    """Returns train, test lists of (text, label). Whole templates/hooks are held out for the test set."""
    r = random.Random(seed)
    train, test = [], []
    for label, temps in T.items():
        units = [(t, False) for t in temps] + [(h, True) for h in H.get(label, [])]
        r.shuffle(units)
        cut = max(int(len(units) * holdout), 1) if holdout else 0
        for part, chunk, n in ((test, units[:cut], per_template // 2), (train, units[cut:], per_template)):
            for t, composed in chunk:
                for _ in range(n):
                    s = (_compose(t, r) if composed else t).format(**_slots(r, label))
                    if r.random() < (.35 if label != "SAFE" else .06): s = obfuscate(s, r)
                    part.append((s, label))
    return train, test

def generate_all(per_template=60, seed=1):
    """Final model: every template (including the ones held out for evaluation) is used for training."""
    tr, te = generate(per_template, seed, holdout=0.0)
    return tr + te
