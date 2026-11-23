"""Train: (1) evaluate on held-out *templates*, (2) refit on everything and save model.joblib."""
import csv, os, joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import FeatureUnion, Pipeline
from data import generate, generate_all
from scamguard import normalize, MODEL_PATH

def build():
    return Pipeline([
        ("tfidf", FeatureUnion([
            ("word", TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
            ("char", TfidfVectorizer(preprocessor=normalize, analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True))])),
        ("clf", LogisticRegression(C=8, max_iter=2000, class_weight="balanced"))])

def extra():  # optional real-world data: extra.csv with columns text,label (SAFE/KYC/LOTTERY/LOAN/JOB/OTHER)
    if not os.path.exists("extra.csv"): return []
    with open("extra.csv", encoding="utf-8") as f:
        return [(r["text"], r["label"].upper()) for r in csv.DictReader(f)]

if __name__ == "__main__":
    train, test = generate()
    m = build().fit(*zip(*(train + extra())))
    X, y = zip(*test)
    pred = m.predict(X)
    print("Held-out templates (6 classes):\n", classification_report(y, pred, digits=3))
    bin_true = np.array([l != "SAFE" for l in y]); bin_pred = np.array([p != "SAFE" for p in pred])
    print(f"Binary scam/safe: acc={np.mean(bin_true == bin_pred):.3f}  false-positive rate on SAFE={np.mean(bin_pred[~bin_true]):.3f}")
    final = build().fit(*zip(*(generate_all() + extra())))
    joblib.dump(final, MODEL_PATH, compress=3)
    print(f"Saved {MODEL_PATH} ({os.path.getsize(MODEL_PATH)/1024:.0f} KB)")
