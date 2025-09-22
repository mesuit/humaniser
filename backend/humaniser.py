# backend/humaniser.py
import re
import os
from typing import Optional

# We'll try to use a transformer paraphraser if available.
paraphraser = None

def init_model():
    """
    Lazily load the Hugging Face paraphrase model.
    Set environment PRELOAD_MODEL=true to preload at startup.
    """
    global paraphraser
    if paraphraser is not None:
        return
    try:
        from transformers import pipeline
        # lightweight paraphrase model; can adjust to other models if needed
        paraphraser = pipeline("text2text-generation", model=os.getenv("PARAPHRASE_MODEL", "Vamsi/T5_Paraphrase_Paws"))
    except Exception as e:
        # model load failed — paraphraser stays None and we will fallback to rule-based
        paraphraser = None
        print("Paraphraser model not loaded:", e)


def _clean_text(text: str) -> str:
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Common shorthand replacements
    replacements = {
        r"\bu\b": "you",
        r"\bur\b": "your",
        r"\bidk\b": "I don't know",
        r"\bthx\b": "thanks",
        r"\bpls\b": "please",
        r"\bomg\b": "oh my God",
        r"\blol\b": "laughing out loud",
    }
    for pat, repl in replacements.items():
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)

    # Basic punctuation fixes: ensure space after periods if missing
    text = re.sub(r'\.(?=[A-Za-z])', '. ', text)
    return text


def _rule_based_humanise(text: str) -> str:
    # modest syntactic smoothing and better phrase choices
    text = _clean_text(text)

    # split into lines and sentences, small simple heuristics
    sentences = re.split(r'(?<=[.!?])\s+', text)
    out_sentences = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # capitalize first letter
        s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()
        # add small connecting words randomly? keep deterministic
        out_sentences.append(s)
    return " ".join(out_sentences)


def _paraphrase_text_with_model(text: str) -> Optional[str]:
    global paraphraser
    if paraphraser is None:
        try:
            init_model()
        except Exception:
            pass
    if paraphraser is None:
        return None

    # chunk text if too long: model prefers smaller inputs.
    # we'll split by sentence punctuation into chunks ~ max 200 tokens heuristic
    parts = re.split(r'(?<=[.!?])\s+', text)
    outputs = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        try:
            res = paraphraser(f"paraphrase: {p}", max_length=256, num_return_sequences=1, truncation=True)
            # transformers pipelines sometimes return list of dicts
            if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict):
                gen = res[0].get("generated_text") or res[0].get("summary_text") or ""
            elif isinstance(res, dict):
                gen = res.get("generated_text") or ""
            else:
                gen = str(res)
            outputs.append(gen.strip())
        except Exception:
            # fallback for this chunk
            outputs.append(p)
    return " ".join(outputs)


def humanise_text(text: str) -> str:
    """
    Main function to call. It attempts to use a model; if unavailable, uses rules.
    Always returns humanised text as string.
    """
    if not text:
        return ""

    # Basic clean first
    clean = _clean_text(text)

    # Try model paraphrase
    paraphrased = _paraphrase_text_with_model(clean)
    if paraphrased:
        return paraphrased

    # else fallback to rule-based
    return _rule_based_humanise(clean)
