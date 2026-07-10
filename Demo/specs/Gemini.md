# YÊU CẦU XÂY DỰNG WEB DEMO ỨNG DỤNG AI (TARGETED ABSA)

## 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)
* **Mục tiêu:** Xây dựng một trang web Single Page Application (SPA) để demo mô hình Deep Learning (Targeted Aspect-Based Sentiment Analysis - TABSA) cho Đồ án môn Học sâu ứng dụng. 
* **Bài toán:** Nhận diện 3 thành phần từ văn bản: Đối tượng (Target), Khía cạnh (Aspect), và Cảm xúc (Sentiment).
* **Ngôn ngữ xử lý:** Tiếng Việt (Miền dữ liệu: Giải trí, âm nhạc, gameshow).
* **Phong cách UI/UX:** Tối giản (Minimalist), thiết kế tập trung vào dữ liệu, hỗ trợ **Dark Mode** mặc định. 
* **Quy ước màu sắc (Color Code):** * Positive (Tích cực): Xanh lá / Xanh ngọc
  * Negative (Tiêu cực): Đỏ / Cam
  * Neutral (Trung tính): Xám / Xanh dương nhạt

## 2. BỐ CỤC TRANG WEB (SITEMAP & LAYOUT)
Trang web bao gồm 4 phân vùng chính, cuộn từ trên xuống dưới:

### Section 1: Hero Section (Giới thiệu)
* **Tiêu đề:** Targeted ABSA cho Chương trình Gameshow Việt Nam
* **Subtitle:** Trích xuất tự động bộ ba (Target, Aspect, Sentiment) từ bình luận mạng xã hội.
* **Thông tin tác giả:** Nhóm 9 (Nguyễn Minh Phú, Võ Hoàng Minh).
* **Giảng viên hướng dẫn:** TS. Đỗ Trọng Hợp, ThS. Nguyễn Ngọc Quí.

### Section 2: Interactive Playground (Khu vực Demo)
* **Model Selector (Dropdown/Radio):** Cho phép chọn các mô hình sau:
  * XLM-ROBERTa Multi-head (Tag: Đề xuất / Nhanh nhất)
  * PhoBERT Multi-head (Tag: Baseline)
  * Qwen2.5-3B-Instruct (Tag: LLM / Chậm)
* **Input Box:** Khung nhập text (Textarea) rộng rãi.
* **Quick Inputs:** Các nút bấm chứa sẵn câu mẫu phức tạp để test nhanh (ví dụ: *"HIEUTHUHAI rap hay vãi nhưng vũ đạo ALIN hơi cứng, show rất đỉnh"*).
* **Action Button:** Nút "Phân tích" có trạng thái Loading/Spinner.
* **Output Area:** * Không in JSON thô. 
  * Áp dụng **Entity Highlighting** (tương tự spaCy NER): Bôi màu trực tiếp vào từ khóa (Target) trong câu gốc.
  * Khi hover (di chuột) vào từ khóa đã highlight, hiển thị Tooltip/Popup nhỏ chứa thông tin: `Aspect` và `Sentiment`.
  * Có xử lý UI cảnh báo nhẹ (Alert/Badge) cho trường hợp `[IMPLICIT]` (nhận diện tổng quát, không có thực thể cụ thể).

### Section 3: Dataset Showcase (Khám phá dữ liệu)
* **Mô tả ngắn:** Giới thiệu bộ dữ liệu 53.198 bộ tứ ý kiến từ "Anh Trai Say Hi" và "Rap Việt Mùa 3".
* **Bảng dữ liệu (Data Table):** * Hiển thị các cột: `text`, `target`, `aspect`, `sentiment`, `opinion_span`.
  * Có tính năng phân trang (Pagination) để không làm nặng trình duyệt.
  * (Optional) Có thanh tìm kiếm hoặc Dropdown filter theo `Aspect` và `Sentiment`.

### Section 4: Experimental Dashboard (Kết quả thực nghiệm)
* **Bảng so sánh hiệu suất:** Hiển thị tĩnh bảng đối sánh các model (so sánh Joint F1 và Joint Accuracy). Điểm nhấn vào kết quả cao nhất của XLM-ROBERTa.
* **Session History:** Bảng log lưu lại các câu mà người dùng đã nhập và kết quả tương ứng trong phiên sử dụng hiện tại (lưu tạm ở Client-side).

## 3. LƯU Ý KỸ THUẬT (TECHNICAL CONSTRAINTS)
* **Frontend:** Tự động sinh mã nguồn UI rõ ràng, phân chia component (ví dụ: dùng React/Vue hoặc các thư viện chuyên build UI cho AI như Streamlit/Gradio tùy vào logic framework).
* **Backend Integration:** Viết dummy function hoặc mock API cho luồng xử lý AI để frontend có thể chạy độc lập trước khi ghép nối mô hình thực.
* **Tối ưu:** Đảm bảo UI không bị "đóng băng" (freeze) khi đợi kết quả trả về từ mô hình.

---
**YÊU CẦU THỰC THI CHO LLM:** Dựa trên cấu trúc và yêu cầu trên, hãy đề xuất stack công nghệ phù hợp nhất và viết mã nguồn cho toàn bộ ứng dụng này. Cung cấp file cấu trúc dự án và code chi tiết cho từng component.