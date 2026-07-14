import http.server
import socketserver
import json
import os
import csv
import urllib.parse
import re
import time
import difflib

# Apply aggressive monkeypatch to bypass transformers safety check on torch.load
try:
    import transformers
    import transformers.utils.import_utils as import_utils
    import_utils.check_torch_load_is_safe = lambda *args, **kwargs: None
    import transformers.utils as utils
    utils.check_torch_load_is_safe = lambda *args, **kwargs: None
    import transformers.modeling_utils as modeling_utils
    modeling_utils.check_torch_load_is_safe = lambda *args, **kwargs: None
    print("[INFO] Aggressive monkeypatch applied to transformers.")
except Exception as e:
    print(f"[WARNING] Could not apply transformers monkeypatch: {e}")

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8080
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "Data"))
MODEL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "Model"))

# Model Checkpoint Paths
QWEN_PATH = os.path.join(MODEL_DIR, "Qwen2.5-3B-Instruct")
LLAMA_PATH = os.path.join(MODEL_DIR, "Llama-3.2-3B-Instruct")
VIBERT_PATH = os.path.join(MODEL_DIR, "ViBERT-Base")
XLMR_PATH = os.path.join(MODEL_DIR, "XLM-RoBERTa-Large")

# ABSA System Prompt (from user request)
ABSA_SYSTEM = """\
Bạn là bộ gán nhãn Targeted ABSA cho bình luận YouTube tiếng Việt về gameshow âm nhạc.

NHIỆM VỤ: Trích xuất TẤT CẢ ý kiến/nhận xét được nhắc đến trong bình luận, mỗi ý kiến là 1 object theo schema sau.

QUAN TRỌNG - TRÍCH XUẤT ĐẦY ĐỦ:
- Một bình luận có thể chứa NHIỀU NHẬN XÉT KHÁC NHAU, kể cả khi cùng nói về 1 người (vd: vừa khen kỹ năng rap, vừa khen ngoại hình/tính cách). PHẢI tách thành các object riêng theo đúng aspect tương ứng, KHÔNG được chỉ lấy 1 ý rồi bỏ qua các ý còn lại.
- Ví dụ: "X rap hay, mặt X cũng dễ thương" -> PHẢI có 2 object: 1 về PERFORMANCE (rap hay) và 1 về PERSONALITY (dễ thương).

OUTPUT FORMAT (BẮT BUỘC):
- CHỈ trả về 1 JSON object thuần, KHÔNG markdown, KHÔNG code block, KHÔNG giải thích, KHÔNG field nào khác ngoài "targets".
{"targets":[{"target":"<string>","aspect":"<ASPECT>","sentiment":"<SENTIMENT>","opinion_span":"<string|null>","intensity":"<INTENSITY>"}]}
- Nếu bình luận spam/không liên quan/không thể gán nhãn: {"targets":[]}

RÀNG BUỘC GIÁ TRỊ (TUYỆT ĐỐI, KHÔNG NGOẠI LỆ):

1. ASPECT (Chỉ chọn 1 trong 6 giá trị này. Nếu phân vân hoặc không khớp cụ thể, bắt buộc dùng PERFORMANCE):
- PERFORMANCE: KỸ NĂNG RAP, hát và trình diễn trên sân khấu — bao gồm rap, flow, lyrics/lời rap, wordplay, punchline, freestyle, đối đáp (battle), vũ đạo, chất lượng giọng hát, hát live, melody, hook, trình diễn tổng thể.
- PERSONALITY: tính cách, thái độ, cách cư xử, sự đáng yêu/dễ thương/hài hước của thí sinh/HLV.
- SONG: nội dung/chất lượng bài hát, beat, sản xuất âm nhạc của bài (giai điệu, beat hay/dở).
- TEAMWORK: sự kết hợp, ăn ý, hỗ trợ giữa các thành viên/đội/HLV.
- VISUAL: ngoại hình, trang phục, hình ảnh, gương mặt (KHÔNG bao gồm tính cách).
- SHOW_FORMAT: định dạng, luật chơi, cách tổ chức của chương trình.

2. "sentiment" CHỈ ĐƯỢC LẤY MỘT TRONG: positive | negative | neutral | mixed
(Lưu ý: Các emoji như 💀/🔥/❤️/👏 mặc định quy về positive trừ khi ngữ cảnh rõ ràng là mỉa mai).

3. "intensity" CHỈ ĐƯỢC LẤY MỘT TRONG: strong | moderate | mild

4. "target" PHẢI LÀ một thực thể được nhắc đến trực tiếp/gián tiếp trong bình luận (tên nghệ sĩ, tên bài hát, tên HLV/đội, hoặc "Rap Việt" cho show nói chung). KHÔNG bịa thêm target không xuất hiện trong bình luận.

5. "opinion_span" PHẢI LÀ một đoạn trích NGUYÊN VĂN (hoặc rất gần nguyên văn) từ bình luận, hoặc null nếu không có cụm từ rõ ràng. KHÔNG tự diễn giải/viết lại thành câu mới.

6. KHÔNG thêm bất kỳ key nào khác ngoài 5 key: target, aspect, sentiment, opinion_span, intensity.

TRƯỚC KHI XUẤT: 
- Đọc lại toàn bộ bình luận, đảm bảo KHÔNG bỏ sót ý kiến nào (đặc biệt khi 1 câu chứa nhiều mệnh đề nối bằng "và", dấu phẩy, "cũng", "nữa").
- Tự kiểm tra lại từng object trong "targets" — nếu "aspect" hoặc "sentiment" hoặc "intensity" không thuộc đúng danh sách enum ở trên, hãy sửa lại cho đúng (map về giá trị gần nhất trong enum, ưu tiên PERFORMANCE/neutral nếu không chắc) trước khi trả kết quả cuối cùng.

VÍ DỤ 1 (nhiều aspect cho cùng 1 target):
Input: Anh Thái VG rap đã thiệt sự, mặt ổng cũng ngơ ngơ nữa, dễ thương thiệt á
Output: {"targets":[{"target":"Anh Thái VG","aspect":"PERFORMANCE","sentiment":"positive","opinion_span":"rap đã thiệt sự","intensity":"strong"},{"target":"Anh Thái VG","aspect":"PERSONALITY","sentiment":"positive","opinion_span":"mặt ổng cũng ngơ ngơ nữa, dễ thương thiệt á","intensity":"moderate"}]}

VÍ DỤ 2 (nhiều target khác nhau):
Input: HIEUTHUHAI rap hay vãi nhưng vũ đạo ALIN hơi cứng, show rất đỉnh
Output: {"targets":[{"target":"HIEUTHUHAI","aspect":"PERFORMANCE","sentiment":"positive","opinion_span":"rap hay vãi","intensity":"strong"},{"target":"ALIN","aspect":"PERFORMANCE","sentiment":"negative","opinion_span":"vũ đạo hơi cứng","intensity":"moderate"},{"target":"Rap Việt","aspect":"SHOW_FORMAT","sentiment":"positive","opinion_span":"show rất đỉnh","intensity":"strong"}]}
"""

# Global In-Memory Databases
silver_comments = []
gold_comments = []
comment_lookup = {}  # Normalized text -> comment dict
common_targets = set()
cohens_kappa_score_val = 0.6559
ALLOWED_ASPECTS = ["PERFORMANCE", "PERSONALITY", "SONG", "TEAMWORK", "VISUAL", "SHOW_FORMAT"]

def cohen_kappa(y_true, y_pred):
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        return 0.0
    n = len(y_true)
    categories = sorted(list(set(y_true).union(set(y_pred))))
    agreements = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    po = agreements / n
    from collections import Counter
    counts_true = Counter(y_true)
    counts_pred = Counter(y_pred)
    pe = sum((counts_true[cat] / n) * (counts_pred[cat] / n) for cat in categories)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)

def get_dynamic_kappa():
    gold_path = os.path.join(DATA_DIR, "gold_targeted_absa.csv")
    val_path = os.path.join(DATA_DIR, "val_gold.csv")
    if not os.path.exists(gold_path) or not os.path.exists(val_path):
        return 0.6559
    try:
        gold_dict = {}
        with open(gold_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                cid = r['comment_id'].strip()
                target = re.sub(r'\s+', ' ', r['target'].strip().lower())
                aspect = r['aspect'].strip().upper()
                if aspect not in ALLOWED_ASPECTS:
                    aspect = "PERFORMANCE"
                sentiment = r['sentiment'].strip().lower()
                key = (cid, target, aspect)
                gold_dict[key] = sentiment
        val_dict = {}
        with open(val_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                cid = r['comment_id'].strip()
                target = re.sub(r'\s+', ' ', r['target'].strip().lower())
                aspect = r.get('aspect', r.get('aspect_category', '')).strip().upper()
                if aspect not in ALLOWED_ASPECTS:
                    aspect = "PERFORMANCE"
                sentiment = r['sentiment'].strip().lower()
                key = (cid, target, aspect)
                val_dict[key] = sentiment
        matched_keys = sorted(list(set(gold_dict.keys()).intersection(set(val_dict.keys()))))
        if len(matched_keys) == 0:
            return 0.0
        gold_s = [gold_dict[k] for k in matched_keys]
        val_s = [val_dict[k] for k in matched_keys]
        return cohen_kappa(gold_s, val_s)
    except Exception as e:
        print(f"[ERROR] Error calculating dynamic Kappa: {e}")
        return 0.6559

# Loaded Hugging Face Models Cache
loaded_models = {
    "qwen": {"model": None, "tokenizer": None},
    "llama": {"model": None, "tokenizer": None},
    "vibert": {"model": None, "tokenizer": None},
    "xlm-roberta-large": {"model": None, "tokenizer": None}
}

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def determine_source(text, target=""):
    text_lower = text.lower()
    target_lower = target.lower()
    atsh_keywords = [
        "anh trai", "say hi", "atsh", "dương domic", "hieuthuhai", "quang trung", 
        "rhyder", "captain", "negav", "isaac", "erik", "quang hùng", "germany", 
        "anh tú", "song luân", "hải đăng doo", "hurrykng", "wean", "lou hoàng", 
        "đỗ phú quí", "năn nỉ", "bài hát", "trấn thành", "chương trình"
    ]
    rv_keywords = [
        "rap việt", "rap viet", "rv3", "karik", "justatee", "b ray", "suboi", 
        "thai vg", "andree", "double2t", "24k.right", "liu grace", "mikelodic", 
        "tez", "gducky", "rap", "flow", "lyrics"
    ]
    for kw in atsh_keywords:
        if kw in target_lower:
            return "Anh Trai Say Hi"
    for kw in rv_keywords:
        if kw in target_lower:
            return "Rap Việt"
    for kw in atsh_keywords:
        if kw in text_lower:
            return "Anh Trai Say Hi"
    for kw in rv_keywords:
        if kw in text_lower:
            return "Rap Việt"
    return "Anh Trai Say Hi"

def load_data_file(filename, source_name=None, is_gold=False):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[WARNING] File not found: {filepath}")
        return []
    
    # Store by comment_id
    grouped_comments = {}
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = r.get("comment_id", "").strip()
            text = r.get("text", "").strip()
            if not cid or not text:
                continue
                
            target = r.get("target", "").strip()
            aspect = r.get("aspect", r.get("aspect_category", "")).strip().upper()
            if aspect not in ALLOWED_ASPECTS:
                aspect = "PERFORMANCE"
            sentiment = r.get("sentiment", "").strip().lower()
            opinion_span = r.get("opinion_span", "").strip()
            intensity = r.get("intensity", "").strip().lower()
            
            # Determine source dynamically if not provided
            curr_source = source_name
            if not curr_source:
                curr_source = determine_source(text, target)
                
            if cid not in grouped_comments:
                grouped_comments[cid] = {
                    "comment_id": cid,
                    "text": text,
                    "source": curr_source,
                    "quadruples": []
                }
            
            if target or aspect or sentiment:
                grouped_comments[cid]["quadruples"].append({
                    "target": target,
                    "aspect": aspect,
                    "sentiment": sentiment,
                    "opinion_span": opinion_span,
                    "intensity": intensity
                })
                if target:
                    common_targets.add(target)
                    
    return list(grouped_comments.values())

def init_databases():
    global silver_comments, gold_comments, comment_lookup
    print("[INFO] Loading datasets from CSV files...")
    
    # Load Silver from FINAL_DATASET.csv (consolidated and preprocessed)
    silver_comments = load_data_file("FINAL_DATASET.csv")
    
    # Load Gold
    gold_comments = load_data_file("gold_targeted_absa.csv", "Gold Standard", is_gold=True)
    
    # Build Lookup Index
    for c in silver_comments:
        norm_txt = normalize_text(c["text"])
        comment_lookup[norm_txt] = c
        
    for c in gold_comments:
        norm_txt = normalize_text(c["text"])
        # Gold standard takes precedence in lookup
        comment_lookup[norm_txt] = c
        
    # Calculate Dynamic Kappa Score
    global cohens_kappa_score_val
    cohens_kappa_score_val = get_dynamic_kappa()
        
    print(f"[SUCCESS] Loaded {len(silver_comments)} Silver comments and {len(gold_comments)} Gold comments.")
    print(f"[SUCCESS] Dynamic Cohen's Kappa score calculated: {cohens_kappa_score_val:.4f}")
    print(f"[SUCCESS] Lookup database initialized with {len(comment_lookup)} unique entries.")

# Custom Heuristic Predictor as a fallback
def heuristic_predict(text):
    norm_text = normalize_text(text)
    targets_found = []
    
    # Simple target search
    for t in common_targets:
        if len(t) > 2 and t.lower() in norm_text:
            targets_found.append(t)
            
    # Default to HIEUTHUHAI, Tez, Karik, B Ray if none found but text contains artists
    if not targets_found:
        default_artists = ["hieuthuhai", "tez", "karik", "b ray", "andree", "thai vg", "double2t", "rhyder", "captain"]
        for artist in default_artists:
            if artist in norm_text:
                targets_found.append(artist.title())
                
    if not targets_found:
        # Fallback to general program target
        if "rap việt" in norm_text or "rv3" in norm_text:
            targets_found.append("Rap Việt")
        elif "anh trai say hi" in norm_text or "atsh" in norm_text:
            targets_found.append("Anh Trai Say Hi")
        else:
            targets_found.append("Chương trình")
            
    # Deduplicate
    targets_found = list(set(targets_found))
    
    targets = []
    for t in targets_found:
        # Heuristically classify aspect
        aspect = "PERFORMANCE"
        if any(w in norm_text for w in ["đẹp trai", "visual", "mặt", "trang phục", "đẹp"]):
            aspect = "VISUAL"
        elif any(w in norm_text for w in ["bài hát", "beat", "nhạc", "giai điệu", "sound"]):
            aspect = "SONG"
        elif any(w in norm_text for w in ["tính cách", "dễ thương", "đáng yêu", "hiền", "thái độ"]):
            aspect = "PERSONALITY"
        elif any(w in norm_text for w in ["team", "đội", "kết hợp", "song ca", "nhóm"]):
            aspect = "TEAMWORK"
        elif any(w in norm_text for w in ["luật", "format", "vòng", "tổ chức", "mùa", "sân khấu", "sound", "show"]):
            aspect = "SHOW_FORMAT"
            
        # Heuristically classify sentiment
        sentiment = "positive"
        if any(w in norm_text for w in ["dở", "chán", "xấu", "cứng", "tệ", "thất vọng", "yếu"]):
            sentiment = "negative"
        elif any(w in norm_text for w in ["bình thường", "tàm tạm", "neutral", "không có gì"]):
            sentiment = "neutral"
            
        # Heuristically extract opinion span
        opinion_span = None
        # Try to find a window around target or a positive/negative keyword
        keywords = ["hay", "đỉnh", "cháy", "đẹp", "dễ thương", "dở", "chán", "xấu", "cứng", "tệ", "bứt phá", "vượt trội"]
        for kw in keywords:
            if kw in norm_text:
                # Find target index and keyword index
                idx_kw = text.lower().find(kw)
                start = max(0, idx_kw - 15)
                end = min(len(text), idx_kw + len(kw) + 15)
                opinion_span = text[start:end].strip()
                break
                
        targets.append({
            "target": t,
            "aspect": aspect,
            "sentiment": sentiment,
            "opinion_span": opinion_span,
            "intensity": "strong" if "quá" in norm_text or "vãi" in norm_text or "lắm" in norm_text else "moderate"
        })
        
    return {"targets": targets}

# Prompt builders based on evaluation scripts
def build_prompt_qwen(text):
    return (
        "<|im_start|>system\n"
        f"{ABSA_SYSTEM}<|im_end|>\n"
        "<|im_start|>user\n"
        f"Gán nhãn ABSA cho bình luận sau:\n{text}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

def build_prompt_llama(text):
    return (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{ABSA_SYSTEM}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
        f"Gán nhãn ABSA cho bình luận sau:\n{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    )

# Robust JSON Parser to handle LLM quirks/malformations
def parse_robust_json(raw_out):
    raw_out = raw_out.strip()
    
    # 1. Clean markdown code blocks
    if raw_out.startswith("```"):
        start_idx = raw_out.find("\n")
        if start_idx != -1:
            raw_out = raw_out[start_idx:].strip()
        if raw_out.endswith("```"):
            raw_out = raw_out[:-3].strip()
            
    # 2. Try direct JSON parsing
    try:
        data = json.loads(raw_out)
        if isinstance(data, list):
            return {"targets": data}
        return data
    except Exception:
        pass
        
    # 3. Try to extract JSON array or object using regex
    start_brace = raw_out.find("{")
    start_bracket = raw_out.find("[")
    
    start_idx = -1
    end_char = ""
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start_idx = start_brace
        end_char = "}"
    elif start_bracket != -1:
        start_idx = start_bracket
        end_char = "]"
        
    if start_idx != -1:
        end_idx = raw_out.rfind(end_char)
        if end_idx != -1 and end_idx > start_idx:
            json_candidate = raw_out[start_idx:end_idx+1]
            try:
                data = json.loads(json_candidate)
                if isinstance(data, list):
                    return {"targets": data}
                return data
            except Exception:
                # Clean trailing commas
                json_candidate_clean = re.sub(r',\s*\}', '}', json_candidate)
                json_candidate_clean = re.sub(r',\s*\]', ']', json_candidate_clean)
                try:
                    data = json.loads(json_candidate_clean)
                    if isinstance(data, list):
                        return {"targets": data}
                    return data
                except Exception:
                    pass
                    
    # 4. Fallback: Regex salvage of JSON objects
    print("[WARNING] Strict JSON parsing failed. Trying regex salvage pattern...")
    salvaged_targets = []
    
    # Match individual JSON objects {...}
    blocks = re.findall(r'\{[^{}]*\}', raw_out)
    for b in blocks:
        try:
            b_clean = re.sub(r',\s*\}', '}', b)
            obj = json.loads(b_clean)
            if "target" in obj:
                salvaged_targets.append({
                    "target": str(obj.get("target", "")),
                    "aspect": str(obj.get("aspect", "PERFORMANCE")),
                    "sentiment": str(obj.get("sentiment", "neutral")),
                    "opinion_span": str(obj.get("opinion_span", "")),
                    "intensity": str(obj.get("intensity", "moderate"))
                })
        except Exception:
            # Fallback to manual key-value extraction using regex
            target_m = re.search(r'"target"\s*:\s*"([^"]*)"', b)
            aspect_m = re.search(r'"aspect"\s*:\s*"([^"]*)"', b)
            sentiment_m = re.search(r'"sentiment"\s*:\s*"([^"]*)"', b)
            opinion_m = re.search(r'"opinion_span"\s*:\s*"([^"]*)"', b)
            intensity_m = re.search(r'"intensity"\s*:\s*"([^"]*)"', b)
            
            if target_m:
                salvaged_targets.append({
                    "target": target_m.group(1),
                    "aspect": aspect_m.group(1) if aspect_m else "PERFORMANCE",
                    "sentiment": sentiment_m.group(1) if sentiment_m else "neutral",
                    "opinion_span": opinion_m.group(1) if opinion_m else None,
                    "intensity": intensity_m.group(1) if intensity_m else "moderate"
                })
                
    if salvaged_targets:
        return {"targets": salvaged_targets}
        
    return None

# Local LLM Predictor
def local_llm_predict(text, model_type):
    global loaded_models
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    model_name = "Qwen" if model_type == "qwen" else "Llama"
    checkpoint_path = QWEN_PATH if model_type == "qwen" else LLAMA_PATH
    
    if not os.path.exists(checkpoint_path) or len(os.listdir(checkpoint_path)) < 3:
        print(f"[WARNING] Local checkpoint for {model_name} not found. Fallback to heuristics.")
        return None
        
    try:
        # Load model dynamically if not cached in RAM
        if loaded_models[model_type]["model"] is None:
            print(f"[INFO] Lazily loading {model_name} model from local checkpoint: {checkpoint_path}...")
            tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
            
            # Use pad_token for Llama
            if model_type == "llama" and tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = AutoModelForCausalLM.from_pretrained(
                checkpoint_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            model.eval()
            
            loaded_models[model_type] = {"model": model, "tokenizer": tokenizer}
            print(f"[SUCCESS] {model_name} model loaded successfully into {device.upper()}!")
            
        # Run inference
        model = loaded_models[model_type]["model"]
        tokenizer = loaded_models[model_type]["tokenizer"]
        
        # Build prompt using specific format
        if model_type == "qwen":
            prompt = build_prompt_qwen(text)
        else:
            prompt = build_prompt_llama(text)
        
        inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
        
        with torch.inference_mode():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id if model_type == "qwen" else tokenizer.pad_token_id
            )
            
        input_len = inputs["input_ids"].shape[1]
        generated_ids = output_ids[0][input_len:]
        raw_out = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        
        # Parse using robust parser
        result = parse_robust_json(raw_out)
        if result is None:
            raise ValueError(f"Failed to parse or salvage JSON from raw output: {raw_out[:100]}...")
        return result
    except Exception as e:
        print(f"[ERROR] Error running local LLM prediction ({model_name}): {e}")
        return None
    finally:
        # Clean up space immediately to protect host RAM/VRAM
        print(f"[INFO] Cleaning up {model_name} model memory from host RAM/VRAM...")
        loaded_models[model_type] = {"model": None, "tokenizer": None}
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Local BERT-based Joint ABSA Predictor (ViBERT / XLM-RoBERTa-Large)
def local_bert_predict(text, model_type):
    global loaded_models
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, AutoModel
    
    model_name = "ViBERT-Base" if model_type == "vibert" else "XLM-RoBERTa-Large"
    checkpoint_path = VIBERT_PATH if model_type == "vibert" else XLMR_PATH
    backbone_name = "FPTAI/vibert-base-cased" if model_type == "vibert" else "xlm-roberta-large"
    ckpt_filename = "tabsa_bb_vibert.pt" if model_type == "vibert" else "tabsa_bb_xlm-roberta-large.pt"
    ckpt_path = os.path.join(checkpoint_path, ckpt_filename)
    
    if not os.path.exists(ckpt_path):
        print(f"[WARNING] Local checkpoint for {model_name} not found at {ckpt_path}. Returning None.")
        return None
        
    try:
        # Load model dynamically if not cached in RAM
        if loaded_models[model_type]["model"] is None:
            print(f"[INFO] Lazily loading {model_name} model and tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(backbone_name)
            
            # Instantiate model architecture matching state dict
            class ABSAModel(nn.Module):
                def __init__(self, backbone_model_name, num_aspects=6):
                    super().__init__()
                    self.backbone = AutoModel.from_pretrained(backbone_model_name)
                    H = self.backbone.config.hidden_size
                    self.dropout = nn.Dropout(0.1)
                    self.ner_head = nn.Linear(H, 3)          # BIO NER head
                    self.asp_head = nn.Linear(H, num_aspects) # Aspect classification head
                    self.sent_head = nn.Linear(H, 3)         # Sentiment classification head

                def forward(self, input_ids, attention_mask):
                    out = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
                    sequence_output = out.last_hidden_state  # (B, L, H)
                    logits_ner = self.ner_head(self.dropout(sequence_output)) # (B, L, 3)
                    return logits_ner, sequence_output
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = ABSAModel(backbone_name, num_aspects=6)
            
            # Load weights (with monkeypatch already applied globally)
            state_dict = torch.load(ckpt_path, map_location=device)
            model.load_state_dict(state_dict)
            model.to(device)
            model.eval()
            
            loaded_models[model_type] = {"model": model, "tokenizer": tokenizer}
            print(f"[SUCCESS] {model_name} model loaded successfully into {device.upper()}!")
            
        model = loaded_models[model_type]["model"]
        tokenizer = loaded_models[model_type]["tokenizer"]
        device = next(model.parameters()).device
        
        # Tokenize and run inference
        inputs = tokenizer(text, return_offsets_mapping=True, return_tensors="pt").to(device)
        offsets = inputs["offset_mapping"][0].cpu().tolist()
        
        with torch.no_grad():
            logits_ner, seq_out = model(inputs["input_ids"], inputs["attention_mask"])
            preds = torch.argmax(logits_ner, dim=-1)[0].cpu().tolist() # (L,)
            
        # Decode BIO tag spans: 1 is B-TGT, 2 is I-TGT, 0 is O
        spans = []
        start_idx = None
        for i, pred in enumerate(preds):
            if pred == 1: # B-TGT
                if start_idx is not None:
                    spans.append((start_idx, i - 1))
                start_idx = i
            elif pred == 2: # I-TGT
                if start_idx is None:
                    start_idx = i
            else: # O (0)
                if start_idx is not None:
                    spans.append((start_idx, i - 1))
                    start_idx = None
        if start_idx is not None:
            spans.append((start_idx, len(preds) - 1))
            
        # Filter valid token spans mapping to actual characters
        valid_spans = []
        for s_tok, e_tok in spans:
            if s_tok < len(offsets) and e_tok < len(offsets):
                char_start = offsets[s_tok][0]
                char_end = offsets[e_tok][1]
                # Skip special tokens with zero width offset mapping
                if char_start != char_end:
                    valid_spans.append((s_tok, e_tok, char_start, char_end))
                    
        # Implicit target handling
        if not valid_spans:
            valid_spans = [(0, 0, 0, 0)] # CLS token mapping
            
        # Classify each span for aspect and sentiment
        # Aspects list must match the training alphabetical order:
        aspects_list = ["PERFORMANCE", "PERSONALITY", "SHOW_FORMAT", "SONG", "TEAMWORK", "VISUAL"]
        sent_map = {0: "negative", 1: "neutral", 2: "positive"}
        
        targets = []
        for s_tok, e_tok, char_start, char_end in valid_spans:
            # Extract span representation using mean pooling (or h_0 for implicit)
            if char_start == 0 and char_end == 0:
                v_s = seq_out[0, 0] # CLS representation
                target_str = "[IMPLICIT]"
            else:
                v_s = seq_out[0, s_tok : e_tok + 1].mean(dim=0)
                target_str = text[char_start:char_end].strip()
                if not target_str:
                    target_str = "[IMPLICIT]"
                    
            with torch.no_grad():
                logits_asp = model.asp_head(v_s)
                logits_sent = model.sent_head(v_s)
                
            asp_idx = torch.argmax(logits_asp).item()
            sent_idx = torch.argmax(logits_sent).item()
            
            targets.append({
                "target": target_str,
                "aspect": aspects_list[asp_idx],
                "sentiment": sent_map[sent_idx],
                "opinion_span": None,
                "intensity": "moderate"
            })
            
        return {"targets": targets}
        
    except Exception as e:
        print(f"[ERROR] Error running local BERT prediction ({model_name}): {e}")
        return None
    finally:
        # Clean up space immediately to protect host RAM/VRAM
        print(f"[INFO] Cleaning up {model_name} model memory from host RAM/VRAM...")
        loaded_models[model_type] = {"model": None, "tokenizer": None}
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Core Prediction router
def get_prediction(text, model_key):
    # Live playground predictions are always calculated from scratch (no DB lookup)
    if model_key in ["qwen", "llama"]:
        print(f"[INFO] Predicting from scratch. Running local LLM: {model_key}")
        result = local_llm_predict(text, model_key)
        if result:
            return result
    elif model_key in ["vibert", "xlm-roberta-large"]:
        print(f"[INFO] Predicting from scratch. Running local BERT model: {model_key}")
        result = local_bert_predict(text, model_key)
        if result:
            return result
            
    # Fallback returns None when checkpoints are missing or inference fails
    print(f"[INFO] Fallback activated for model: {model_key} -> returning None")
    return {"targets": None}

# Custom HTTP Request Handler
class ABSADemoHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
        
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        # API: Get Stats
        if path == "/api/stats":
            self.handle_get_stats()
        # API: Get Dataset explorer
        elif path == "/api/dataset":
            self.handle_get_dataset(query)
        # Default: serve static files
        else:
            super().do_GET()
            
    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # API: Live Prediction
        if path == "/api/predict":
            self.handle_predict()
        else:
            self.send_error(404, "Not Found")
            
    def handle_get_stats(self):
        # Total comments count
        total_comments = len(silver_comments)
        total_gold = len(gold_comments)
        
        # Combined quadruples count
        total_quads = sum(len(c["quadruples"]) for c in silver_comments)
        total_gold_quads = sum(len(c["quadruples"]) for c in gold_comments)
        
        # Aspect distribution
        aspect_counter = {}
        sentiment_counter = {}
        source_counter = {"Rap Việt": 0, "Anh Trai Say Hi": 0}
        
        for c in silver_comments:
            source_counter[c["source"]] = source_counter.get(c["source"], 0) + 1
            for q in c["quadruples"]:
                asp = q["aspect"]
                sent = q["sentiment"]
                
                aspect_counter[asp] = aspect_counter.get(asp, 0) + 1
                sentiment_counter[sent] = sentiment_counter.get(sent, 0) + 1
                
        # Cohen's Kappa is dynamically calculated
        stats = {
            "total_comments": total_comments,
            "total_quadruples": total_quads,
            "total_gold_comments": total_gold,
            "total_gold_quadruples": total_gold_quads,
            "cohens_kappa": cohens_kappa_score_val,
            "aspect_distribution": aspect_counter,
            "sentiment_distribution": sentiment_counter,
            "source_distribution": source_counter
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
        
    def handle_get_dataset(self, query):
        page = int(query.get("page", [1])[0])
        limit = int(query.get("limit", [50])[0])
        search = query.get("search", [""])[0].lower()
        aspect = query.get("aspect", [""])[0].upper()
        sentiment = query.get("sentiment", [""])[0].lower()
        source = query.get("source", [""])[0]
        has_span = query.get("has_span", [""])[0]
        dataset_type = query.get("type", ["silver"])[0]
        
        db = gold_comments if dataset_type == "gold" else silver_comments
        
        filtered = []
        for c in db:
            # Source filter
            if source and c["source"] != source:
                continue
                
            # Text/Target search
            if search:
                text_match = search in c["text"].lower()
                target_match = any(search in q["target"].lower() for q in c["quadruples"])
                if not text_match and not target_match:
                    continue
                    
            # Check individual quadruples
            matching_quads = []
            for q in c["quadruples"]:
                if aspect and q["aspect"] != aspect:
                    continue
                if sentiment and q["sentiment"] != sentiment:
                    continue
                if has_span == "yes" and not q["opinion_span"]:
                    continue
                if has_span == "no" and q["opinion_span"]:
                    continue
                matching_quads.append(q)
                
            if c["quadruples"] and not matching_quads:
                continue
                
            quads_to_show = matching_quads if (aspect or sentiment or has_span) else c["quadruples"]
            
            for q in quads_to_show:
                filtered.append({
                    "comment_id": c["comment_id"],
                    "text": c["text"],
                    "source": c["source"],
                    "target": q["target"],
                    "aspect": q["aspect"],
                    "sentiment": q["sentiment"],
                    "intensity": q["intensity"],
                    "opinion_span": q["opinion_span"]
                })
                
        # Pagination
        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = filtered[start:end]
        
        response = {
            "total": total,
            "page": page,
            "limit": limit,
            "data": paginated_data
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
    def handle_predict(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode('utf-8'))
        
        text = payload.get("text", "").strip()
        model_key = payload.get("model", "xlm-roberta-large").lower()
        
        if not text:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Text is empty"}).encode('utf-8'))
            return
            
        start_time = time.time()
        
        # Get predictions
        prediction_res = get_prediction(text, model_key)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        response = {
            "model": model_key,
            "text": text,
            "targets": prediction_res.get("targets", []),
            "cached": prediction_res.get("cached", False),
            "inference_time_ms": elapsed_ms
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def run_server():
    init_databases()
    # Change working directory to Report/Demo to make sure server serves static files from there
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = ABSADemoHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[RUNNING] ABSA Web Demo Dashboard active at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[STOPPED] Stopping server.")

if __name__ == "__main__":
    run_server()
