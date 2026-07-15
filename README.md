# Targeted Aspect-Based Sentiment Analysis (Targeted ABSA) - Web Demo Dashboard

**GitHub Repository:** [https://github.com/nmpstony/Targeted-ABSA-for-Vietnamese-Gameshows](https://github.com/nmpstony/Targeted-ABSA-for-Vietnamese-Gameshows)

Dự án chuyên biệt phục vụ phân tích cảm xúc dựa trên khía cạnh đối tượng (Targeted ABSA) cho bình luận tiếng Việt về hai gameshow âm nhạc lớn: **Anh Trai Say Hi** và **Rap Việt Mùa 3**.

Thư mục chính chứa mã nguồn Web Demo Dashboard, dữ liệu mẫu, và khung mô hình.

---

## 1. Cấu trúc thư mục kho lưu trữ
Kho lưu trữ chứa 3 thư mục chính:
- **`Data/`:** Chứa dữ liệu CSV đã chuẩn hóa phục vụ phân tích phân phối thống kê và đối chiếu Cohen's Kappa score.
- **`Demo/`:** Chứa mã nguồn chạy Web Dashboard (giao diện SPA `index.html` và server tĩnh `server.py`).
- **`Model/`:** Thư mục lưu trữ các local checkpoints cho các mô hình (weights được tự động bỏ qua qua `.gitignore`).

---

## 2. Hướng dẫn khởi chạy Web Demo

### Yêu cầu hệ thống
- Python 3.10+ hỗ trợ chạy học sâu (PyTorch, Transformers, CUDA).

### Các bước cài đặt và khởi chạy

1. **Clone repository này về máy:**
   ```bash
   git clone https://github.com/nmpstony/Targeted-ABSA-for-Vietnamese-Gameshows.git
   cd Targeted-ABSA-for-Vietnamese-Gameshows
   ```
2. **Kích hoạt môi trường chạy và cài đặt thư viện phụ thuộc:**
   Kích hoạt môi trường Conda (nếu có) và chạy lệnh cài đặt qua tệp `requirements.txt`:
   ```bash
   conda activate se365
   pip install -r requirements.txt
   ```
3. **Di chuyển vào thư mục Demo và chạy server:**
   ```bash
   cd Demo
   python server.py
   ```
4. **Mở trình duyệt và truy cập:**
   Truy cập đường dẫn sau trên trình duyệt web:
   ```
   http://localhost:8080
   ```
