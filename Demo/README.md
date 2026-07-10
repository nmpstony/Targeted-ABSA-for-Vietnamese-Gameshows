# Targeted Aspect-Based Sentiment Analysis (Targeted ABSA) - Web Demo Dashboard

Hệ thống Web Demo Dashboard gán nhãn và phân tích cảm xúc dựa trên đối tượng khía cạnh (Targeted ABSA) cho bình luận YouTube tiếng Việt về các chương trình gameshow âm nhạc (**Anh Trai Say Hi** và **Rap Việt Mùa 3**).

Dự án hỗ trợ chạy suy luận thực tế bằng các mô hình học sâu lớn cục bộ (Local LLM) và bộ phân tích tối ưu.

---

## 1. Các chức năng chính của Dashboard

1. **Tổng quan (Overview):** Biểu đồ phân phối tự động vẽ bằng Chart.js cho các khía cạnh Aspect (VOCAL, PERFORMANCE, SONG,...), cực tính cảm xúc (positive, negative, neutral), và nguồn dữ liệu (Rap Việt, Anh Trai Say Hi). Hiển thị chỉ số Cohen's Kappa score được tính động.
2. **Live Playground:**
   - **Chạy đơn lẻ (Single Model):** Chạy suy luận trực tiếp trên câu nhập tự do hoặc chọn câu mẫu có sẵn.
   - **Chạy so sánh (Comparative Mode):** So sánh side-by-side kết quả của cả 4 mô hình (`xlm-r`, `phobert`, `qwen`, `llama`) cùng lúc.
   - **Tối ưu hóa tài nguyên:** Các mô hình LLM (Qwen và Llama) được chạy tuần tự và **tự động giải phóng VRAM ngay sau khi chạy xong** để tránh quá tải bộ nhớ máy tính.
   - **Highlight trực quan:** Bôi màu riêng biệt giữa **Đối tượng (Target)** và **Đoạn ý kiến (Opinion Span)** để dễ dàng quan sát.
3. **Dataset Explorer:** Trình duyệt tập dữ liệu mẫu, phân trang mượt mà, lọc theo Aspect/Sentiment/Source và tìm kiếm nhanh.
4. **Báo cáo học thuật:** Trưng bày các bảng kết quả benchmark của đồ án và phân tích chi tiết các case study lỗi thực tế.

---

## 2. Hướng dẫn khởi chạy Web Demo

### Yêu cầu hệ thống
- Hệ điều hành: Windows / Linux / macOS.
- Python 3.10+ có hỗ trợ môi trường chạy học sâu (PyTorch, Transformers, CUDA).

### Các bước cài đặt và khởi chạy

1. **Clone repository này về máy:**
   ```bash
   git clone <github-repo-url>
   cd Targeted-ABSA-for-Vietnamese-Gameshows
   ```
2. **Kích hoạt môi trường (Ví dụ bằng Conda):**
   ```bash
   conda activate se365
   ```
3. **Khởi chạy Web Server:**
   ```bash
   python server.py
   ```
4. **Mở trình duyệt và truy cập:**
   Truy cập đường dẫn sau trên trình duyệt web:
   ```
   http://localhost:8080
   ```

*Lưu ý: Các checkpoint mô hình lớn (như Qwen2.5-3B-Instruct và Llama-3.2-3B-Instruct) cần được đặt tương ứng trong thư mục `Model/Qwen2.5-3B-Instruct/` và `Model/Llama-3.2-3B-Instruct/` để server nạp và chạy suy luận.*
