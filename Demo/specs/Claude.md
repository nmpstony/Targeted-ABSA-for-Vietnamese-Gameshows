# Đặc tả xây dựng Website Demo — Targeted ABSA cho Gameshow Việt Nam

> Tài liệu này mô tả yêu cầu chức năng và giao diện cho một website demo học thuật, minh họa hệ thống Targeted Aspect-Based Sentiment Analysis (Target – Aspect – Sentiment) được xây dựng trong đồ án. Dùng tài liệu này làm brief để một LLM/agent lập trình triển khai (frontend + backend giả lập dữ liệu nếu cần).

## 0. Bối cảnh dữ liệu & mô hình (để LLM hiểu domain)

- Bài toán: trích xuất bộ tứ `(target, aspect, sentiment, opinion_span)` từ bình luận YouTube tiếng Việt về 2 chương trình: **Anh Trai Say Hi** và **Rap Việt Mùa 3**.
- 9 nhãn aspect cố định: `VOCAL, PERFORMANCE, VISUAL, SONG, STAGE_PRODUCTION, PERSONALITY, TEAMWORK, SHOW_FORMAT, GENERAL`.
- 3 nhãn sentiment: `positive, negative, neutral`.
- 3 nhãn intensity (phụ): `strong, moderate, mild`.
- Các model cần cho phép chọn để gán nhãn:
  1. `XLM-RoBERTa-Base` (fine-tuned, đề xuất chính) — Joint F1 0.270 / Joint Acc 0.3909
  2. `PhoBERT-Base` (fine-tuned) — Joint F1 0.240 / Joint Acc 0.3606
  3. `Qwen2.5-3B-Instruct` (zero-shot) — Joint F1 0.124 / Joint Acc 0.0533
  4. `Llama-3.2-3B-Instruct` (zero-shot) — Joint F1 0.156 / Joint Acc 0.0800
- Thống kê dataset: 48.152 bình luận thô → 53.198 bộ tứ sạch / 35.305 bình luận; Gold Standard: 150 bình luận / 334 bộ tứ.

---

## 1. Sitemap tổng thể

Xây dựng dạng SPA (1 trang, có sidebar/tab điều hướng) với các section sau:

```
Trang chủ (Overview)
├── Demo trực tiếp (Live Inference)      -- CORE FEATURE
├── Bộ dữ liệu (Dataset Explorer)         -- CORE FEATURE
├── Kết quả thực nghiệm (Experiment Results)
└── Giới thiệu phương pháp (Model & Method) -- phụ, có thể làm sau
```

---

## 2. Section: Demo trực tiếp (ưu tiên cao nhất)

### Input
- Textarea nhập câu bình luận tiếng Việt.
- Nút "Dùng câu mẫu ngẫu nhiên" — lấy random 1 câu từ tập Gold Standard/dataset có sẵn.
- Dropdown chọn model (4 lựa chọn liệt kê ở mục 0).
- Nút "Phân tích".
- Nút "So sánh các model" — chạy đồng thời nhiều model trên cùng 1 câu, hiển thị kết quả side-by-side (bảng hoặc cột song song).

### Output
- **Highlight trực quan trên câu gốc**: bôi màu đúng vị trí `opinion_span`/target ngay trong câu (giống Hình 3.1 trong report — 1 câu có thể ra nhiều bộ tứ).
- Với mỗi target tách thành 1 card/dòng riêng gồm:
  - `target` (text)
  - `aspect` (badge, màu cố định theo 9 loại — xem bảng màu ở mục 6)
  - `sentiment` (badge màu: xanh lá = positive, đỏ = negative, xám = neutral)
  - `intensity` (nhỏ, phụ)
  - `opinion_span` (in nghiêng hoặc highlight)
- Trường hợp không tìm thấy span rõ ràng → hiển thị nhãn `[IMPLICIT]` kèm ghi chú giải thích ngắn (không để trống gây hiểu lầm là lỗi).
- Hiển thị **thời gian suy luận (ms)** cho mỗi lần chạy.
- Validate input: chặn submit khi rỗng, giới hạn độ dài tối đa (ví dụ 256 ký tự), thông báo lỗi rõ ràng.

### Lưu ý kỹ thuật quan trọng
- Model nhẹ (XLM-R fine-tuned) nên gọi API thật/real-time nếu có thể host.
- Model LLM zero-shot (Qwen/Llama 3B) nếu không host được real-time: dùng **kết quả cache sẵn** cho một tập câu mẫu cố định, và hiển thị rõ nhãn "Kết quả minh họa (cached)" trên UI để tránh gây hiểu lầm là suy luận trực tiếp.
- Cần trạng thái loading rõ ràng khi gọi model, và fallback UI thân thiện nếu API lỗi/timeout (không được crash trắng trang).

---

## 3. Section: Giới thiệu Dataset

### Khối thống kê tổng quan (dạng số liệu lớn / infographic)
- Tổng bình luận thô: 48.152 (ATSH: 28.000 / RV3: 20.152)
- Tổng bộ tứ sau làm sạch: 53.198 (từ 35.305 bình luận)
- Gold Standard: 150 bình luận / 334 bộ tứ

### Biểu đồ (tái dựng từ report, dùng dữ liệu mẫu/giả lập nếu không có số liệu thật)
- Stacked bar chart: phân bố Sentiment theo từng Aspect
- Bar chart: số lượng bình luận theo số lượng target/câu (1–6 target)
- Thêm: pie chart tỉ lệ dữ liệu theo 2 nguồn (ATSH vs RV3); bar chart phân bố 9 nhãn aspect

### Bảng xem mẫu dữ liệu (data viewer) — bắt buộc
- Cột hiển thị: `comment_id, text, target, aspect, sentiment, intensity, opinion_span`
- **Không load hết toàn bộ dữ liệu cùng lúc** — dùng phân trang hoặc virtualized scroll (lazy-load), vì tập dữ liệu lớn (53k dòng).
- Bộ lọc: theo `aspect`, `sentiment`, nguồn dữ liệu (ATSH/RV3), có/không có `opinion_span`.
- Ô tìm kiếm theo từ khóa trong `text` hoặc `target`.
- Highlight `opinion_span` ngay trong cột `text` (đồng bộ style với phần Demo).
- Toggle chuyển giữa 2 tập: "Dữ liệu Silver (gán nhãn tự động bằng LLM)" và "Gold Standard (gán nhãn thủ công)".
- Lọc trước nội dung nhạy cảm/xúc phạm nếu dataset thật chứa (không hiển thị công khai nếu chưa kiểm duyệt).

---

## 4. Section: Kết quả thực nghiệm

### Bảng so sánh kiến trúc (tương ứng Bảng 6.1 trong report)
| Model | Joint F1 | Joint Accuracy |
|---|---|---|
| XLM-RoBERTa-Base (đề xuất) | 0.270 | 0.3909 |
| PhoBERT-Base | 0.240 | 0.3606 |
| Qwen2.5-3B-Instruct (zero-shot) | 0.124 | 0.0533 |
| Llama-3.2-3B-Instruct (zero-shot) | 0.156 | 0.0800 |

- Bảng có thể sort theo cột, highlight hàng có kết quả tốt nhất.

### Bảng Ablation Study (tương ứng Bảng 6.2)
| Cấu hình tinh chỉnh | Joint F1 | Joint Accuracy |
|---|---|---|
| Merge Dataset (gộp 3 câu) | 0.248 | 0.3758 |
| Feature Fusion (Local+Global) | 0.255 | 0.3818 |
| Fusion + Focal Loss | 0.262 | 0.3697 |
| Fusion + Focal Loss + CRF | 0.218 | 0.3182 |

- Có thể thêm biểu đồ cột minh họa trade-off giữa các cấu hình.

### Bảng phân tích module Sentiment độc lập (tương ứng Bảng 6.3)
- 3 Attention Mode (`cls`, `attention_pooling`, `gated_fusion`) × 3 Loss Function (`CrossEntropy`, `WeightedCrossEntropy`, `FocalLoss`).
- Gợi ý hiển thị dạng **heatmap** (thay vì bảng số thuần) để thấy rõ pattern hiệu năng.

### Tính năng "Lưu kết quả" (bắt buộc theo yêu cầu người dùng)
- Mỗi lần chạy inference ở Section 2 (Demo trực tiếp), tự động lưu vào **bảng lịch sử** gồm: input text, model đã chọn, output (bộ tứ), thời gian chạy, timestamp.
- Cho phép xem lại lịch sử demo dạng bảng, xóa từng dòng hoặc xóa toàn bộ.
- Nút **Export** lịch sử demo và bảng thực nghiệm chính thức ra file CSV/JSON.
- Mục đích: dùng làm minh chứng khi báo cáo, tránh phải chạy lại demo trực tiếp khi trình bày nếu mạng/model gặp sự cố.

### Phần Case study lỗi điển hình (tương ứng mục 6.3 report)
Hiển thị 3 ví dụ lỗi thực tế (kèm câu gốc, gold label, model prediction, giải thích nguyên nhân):
1. **Sentiment Confusion** — 1 target có 2 sắc thái cảm xúc trái chiều trong cùng câu.
2. **Boundary/Implicit Target Failure** — mô hình không nhận diện được tên riêng, fallback về `[IMPLICIT]`.
3. **Aspect Misclassification** — nhầm lẫn giữa các aspect gần nghĩa (VD: PERSONALITY vs PERFORMANCE).

---

## 5. Section: Giới thiệu phương pháp (phụ, làm sau nếu còn thời gian)

- Sơ đồ kiến trúc Unified Multi-Head TABSA: `Comment → Tokenizer → Transformer Backbone → NER Head → Mean Pooling → (Aspect Head, Sentiment Head) → Extracted Triples`.
- Bảng chú giải: 9 nhãn aspect + 3 nhãn sentiment + ý nghĩa ngắn gọn từng nhãn.

---

## 6. Yêu cầu UI/UX chung

- **Bảng màu cố định, dùng xuyên suốt toàn site** (Demo, Dataset Viewer, Charts):
  - Sentiment: `positive` = xanh lá, `negative` = đỏ, `neutral` = xám.
  - Aspect: chọn 9 màu phân biệt rõ, giữ nguyên mapping ở mọi nơi hiển thị badge/chart.
- Ngôn ngữ giao diện: **tiếng Việt** là chính (vì dữ liệu và người dùng mục tiêu là tiếng Việt).
- Responsive: bảng dữ liệu lớn cần scroll ngang mượt trên mobile.
- Loading state rõ ràng cho mọi tác vụ gọi model/API.
- Có trang/thông báo fallback thân thiện khi API lỗi, không để trắng trang hoặc crash.

---

## 7. Gợi ý kiến trúc kỹ thuật (không bắt buộc theo đúng công nghệ này, chỉ là gợi ý)

- **Frontend**: SPA (React hoặc tương đương), quản lý state cho lịch sử demo ở client hoặc gọi API lưu về backend.
- **Backend/API**:
  - `POST /predict` — nhận `{text, model_name}` → trả về danh sách bộ tứ `{target, aspect, sentiment, intensity, opinion_span}`.
  - `GET /dataset` — trả dữ liệu phân trang, hỗ trợ filter/search theo query params.
  - `GET/POST/DELETE /history` — lưu, lấy, xóa lịch sử demo.
- **Model serving**: model nhẹ (XLM-R) nên host thật; model LLM 3B nếu không host real-time thì dùng cache cho tập câu mẫu cố định, ghi rõ trên UI đây là kết quả minh họa.
- Nếu chưa có dữ liệu/model thật, có thể dùng **dữ liệu giả lập (mock)** đúng theo schema mô tả ở mục 0 và 3 để dựng UI trước, sau đó thay bằng API thật.

---

## 8. Checklist hoàn thành (dùng để tự kiểm tra khi build xong)

- [ ] Nhập câu → chọn model → ra đúng 3 nhãn target/aspect/sentiment, có highlight span
- [ ] Chọn được ít nhất 2 model khác nhau, có chế độ so sánh song song
- [ ] Giới thiệu dataset có số liệu tổng quan + ít nhất 2 biểu đồ
- [ ] Bảng dữ liệu mẫu có phân trang/scroll, filter, search
- [ ] Bảng kết quả thực nghiệm (3 bảng chính) hiển thị đầy đủ, đúng số liệu
- [ ] Tính năng lưu lịch sử demo + export CSV/JSON hoạt động
- [ ] Bảng màu nhất quán toàn site, giao diện tiếng Việt, responsive cơ bản
- [ ] Xử lý lỗi/loading không làm crash trang
