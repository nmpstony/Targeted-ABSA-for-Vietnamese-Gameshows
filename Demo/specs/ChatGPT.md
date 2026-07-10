# Website Specification - Targeted ABSA Demo System

## 1. Mục tiêu

Xây dựng một website demo trực quan cho đồ án **Targeted Aspect-Based Sentiment Analysis (Targeted ABSA)** trên bình luận YouTube về các chương trình giải trí Việt Nam.

Website **không chỉ là giao diện chạy model**, mà còn đóng vai trò như một **Research Demo Dashboard**, giúp người xem hiểu:

- Bài toán Targeted ABSA
- Bộ dữ liệu do nhóm xây dựng
- Các mô hình được so sánh
- Kết quả thực nghiệm
- Quá trình suy luận của hệ thống

Website cần có giao diện hiện đại, đơn giản, thiên về phong cách AI/NLP Dashboard.

---

# 2. Định hướng thiết kế

## Phong cách

- Modern
- Clean
- AI Dashboard
- Responsive
- Màu trắng + xanh dương + tím
- Ít hiệu ứng
- Dễ trình diễn trước giảng viên

---

# 3. Cấu trúc Website

Navbar gồm:

- Home
- Demo
- Dataset
- Models
- Experiments
- History
- About

---

# 4. HOME PAGE

## Hero Section

Hiển thị:

> Targeted Aspect-Based Sentiment Analysis
>
> for Vietnamese Music Gameshow

Mô tả ngắn:

"Một hệ thống tự động nhận diện Target, Aspect và Sentiment trong bình luận YouTube."

Button

- Try Demo
- View Dataset

---

## Giới thiệu bài toán

Hiển thị pipeline

Input Comment

↓

Model

↓

Prediction

Ví dụ

Input

HIEUTHUHAI rap hay nhưng vũ đạo ALIN hơi cứng.

Output

| Target | Aspect | Sentiment |
|---------|---------|-----------|
| HIEUTHUHAI | PERFORMANCE | Positive |
| ALIN | PERFORMANCE | Negative |

---

## Đóng góp của đề tài

Hiển thị dạng Card

Card 1

Dataset

35,305 Comments

Card 2

53,198 Opinion Quadruples

Card 3

Targeted ABSA

Target + Aspect + Sentiment

Card 4

Multiple Models

- XLM-R
- PhoBERT
- Qwen
- Llama

---

# 5. DEMO PAGE (Quan trọng nhất)

Đây là trang chính của website.

Layout gồm hai phần.

---

## 5.1 Input

Textarea lớn

Placeholder

"Nhập bình luận YouTube..."

Ví dụ

"HIEUTHUHAI rap quá hay nhưng phần visual của Negav hơi chán."

Có nút

Analyze

---

## 5.2 Model Selection

Dropdown

Model

Danh sách

- XLM-RoBERTa
- PhoBERT
- Qwen 2.5
- Llama 3.2

Có thể disable các model chưa hỗ trợ.

---

## 5.3 Ví dụ mẫu

Hiển thị nhiều Sample Input.

Click vào sẽ tự động điền textbox.

Ví dụ

- HIEUTHUHAI rap cực cháy.
- Negav visual đẹp.
- Beat bài này quá hay.
- Phần sân khấu hôm nay rất đỉnh.

---

## 5.4 Loading

Sau khi nhấn Analyze

Hiển thị Loading Pipeline

Step 1

Target Detection

↓

Step 2

Aspect Classification

↓

Step 3

Sentiment Classification

↓

Completed

---

## 5.5 Prediction Result

Không hiển thị JSON mặc định.

Hiển thị trực quan.

### Input

Hiển thị nguyên câu.

---

### Highlight Target

Tô màu các Target trong câu.

Ví dụ

[HIEUTHUHAI] rap rất hay nhưng [Negav] visual hơi yếu.

---

### Prediction Table

| Target | Aspect | Sentiment |
|---------|---------|-----------|
| HIEUTHUHAI | PERFORMANCE | Positive |
| Negav | VISUAL | Negative |

Aspect

Hiển thị Badge.

Sentiment

Positive

🟢

Negative

🔴

Neutral

⚪

---

### Confidence (Optional)

Nếu model hỗ trợ.

Hiển thị

Target

95%

Aspect

91%

Sentiment

97%

---

### Processing Time

Ví dụ

Inference Time

180 ms

---

### Raw JSON

Có nút

Show Raw JSON

Mặc định đóng.

---

### Copy Result

Button

- Copy Table
- Copy JSON

---

### Export

Button

- Export CSV
- Export JSON

---

# 6. DATASET PAGE

Đây là phần giới thiệu bộ dữ liệu.

---

## Tổng quan Dataset

Card

Comments

35,305

Card

Opinion Quadruples

53,198

Card

Nguồn dữ liệu

- Anh Trai Say Hi
- Rap Việt

---

## Dataset Schema

Hiển thị bảng

| Column | Description |
|----------|-------------|

Bao gồm

- comment_id
- text
- target
- aspect
- sentiment
- opinion_span
- intensity

---

## Dataset Sample

Hiển thị Data Table.

Có thể hiển thị

20 dòng

Có thanh cuộn.

Hoặc

Pagination.

---

## Search Dataset

Search theo

- Artist
- Target
- Aspect
- Sentiment

---

## Dataset Statistics

Biểu đồ

- Aspect Distribution
- Sentiment Distribution
- Target Frequency
- Number of Targets per Comment

---

# 7. MODELS PAGE

Giới thiệu các model.

Mỗi model là một Card.

Ví dụ

## XLM-R

- Backbone
- Shared Encoder
- Multi-head Architecture

## PhoBERT

...

## Qwen

...

## Llama

...

---

## Model Comparison

Bảng

| Model | Joint F1 | Joint Accuracy |
|--------|----------|----------------|

Có Highlight Best Model.

---

# 8. EXPERIMENTS PAGE

Hiển thị toàn bộ kết quả thực nghiệm.

---

## Backbone Comparison

So sánh

- XLM-R
- PhoBERT
- Qwen
- Llama

Metric

- Precision
- Recall
- Joint F1
- Joint Accuracy

---

## Ablation Study

Hiển thị

- Data Concatenation
- Feature Fusion
- Focal Loss
- CRF Layer

---

## Visualization

Biểu đồ

- Bar Chart
- Line Chart
- Radar Chart

---

## Best Model

Card

Best Overall

Tên Model

Joint Accuracy

Joint F1

---

# 9. HISTORY PAGE

Lưu toàn bộ kết quả suy luận.

---

## History Table

| Time | Model | Input | Prediction |

Có

- Search
- Filter
- Sort

---

## View Detail

Hiển thị

Input

↓

Prediction

↓

Target

↓

Aspect

↓

Sentiment

---

## Delete

Cho phép xóa.

---

## Export

Cho phép export

CSV

JSON

---

# 10. ABOUT PAGE

Giới thiệu

- Mục tiêu đề tài
- Targeted ABSA
- Dataset
- Pipeline
- Nhóm thực hiện
- Giáo viên hướng dẫn

---

# 11. Chức năng bắt buộc

## Demo

- Nhập một câu
- Chọn model
- Chạy suy luận
- Trả về Target
- Trả về Aspect
- Trả về Sentiment

---

## Dataset

- Giới thiệu dataset
- Hiển thị thống kê
- Hiển thị sample
- Search dataset

---

## Models

- Chọn model
- So sánh model

---

## Experiments

- Hiển thị bảng kết quả
- Hiển thị biểu đồ

---

## History

- Lưu kết quả
- Xem lại
- Xóa
- Export

---

# 12. UI Components

Nên sử dụng

- Navbar
- Sidebar (optional)
- Cards
- Badge
- Table
- Chart
- Dialog
- Toast
- Tooltip
- Accordion
- Tabs

---

# 13. Trải nghiệm người dùng

Luồng sử dụng

Home

↓

Demo

↓

Nhập Comment

↓

Chọn Model

↓

Analyze

↓

Target Detection

↓

Aspect Classification

↓

Sentiment Classification

↓

Prediction

↓

Save History

---

# 14. Yêu cầu UI

Không hiển thị JSON mặc định.

Ưu tiên:

- Highlight Target
- Prediction Table
- Badge
- Icon
- Chart

JSON chỉ dùng cho người muốn xem chi tiết.

---

# 15. Yêu cầu kỹ thuật cho LLM

LLM cần sinh ra toàn bộ frontend theo các nguyên tắc sau:

- Thiết kế hiện đại, tối giản.
- Responsive cho Desktop và Laptop.
- Giao diện ưu tiên trình diễn học thuật.
- Các thành phần phải có thể mở rộng để kết nối backend sau này.
- Không hardcode dữ liệu vào component chính; sử dụng mock data hoặc API abstraction.
- Tách biệt rõ các page, component và service để dễ bảo trì.
- Tất cả bảng dữ liệu phải hỗ trợ tìm kiếm, cuộn hoặc phân trang.
- Biểu đồ và thống kê phải được thiết kế để dễ thay thế bằng dữ liệu thực.
- Kết quả dự đoán phải được trình bày trực quan, tập trung vào ba nhãn cốt lõi:
  - Target
  - Aspect
  - Sentiment
- Lịch sử suy luận phải được lưu trữ và có khả năng xuất dữ liệu.

---

# 16. Mục tiêu cuối cùng

Website cần tạo cảm giác như một **hệ thống nghiên cứu hoàn chỉnh**, không phải chỉ là một trang web nhập văn bản rồi trả kết quả.

Người xem cần thấy được:

- Giá trị của bộ dữ liệu.
- Giá trị của mô hình.
- Quá trình suy luận.
- Khả năng so sánh nhiều mô hình.
- Kết quả thực nghiệm.
- Khả năng mở rộng thành hệ thống Social Listening trong tương lai.