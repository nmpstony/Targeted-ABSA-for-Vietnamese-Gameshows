# Targeted Aspect-Based Sentiment Analysis (Targeted ABSA) - Web Demo Dashboard

Dự án chuyên biệt phục vụ phân tích cảm xúc dựa trên khía cạnh đối tượng (Targeted ABSA) cho bình luận tiếng Việt về hai gameshow âm nhạc lớn: **Anh Trai Say Hi** và **Rap Việt Mùa 3**.

Thư mục chính chứa mã nguồn Web Demo Dashboard, dữ liệu mẫu, và khung mô hình.

---

## 1. Cấu trúc thư mục kho lưu trữ
Kho lưu trữ chứa 3 thư mục chính:
- **`Data/`:** Chứa 4 tệp tin dữ liệu CSV đã chuẩn hóa phục vụ phân tích phân phối thống kê và đối chiếu Cohen's Kappa score:
  - `absa_GT_RV_1000.csv` (Silver Rap Việt)
  - `absa_GT_ATSH_2000.csv` (Silver Anh Trai Say Hi)
  - `gold_targeted_absa.csv` (Gold Standard thủ công)
  - `val_gold.csv` (LLMs gán nhãn)
- **`Demo/`:** Chứa mã nguồn chạy Web Dashboard (giao diện SPA `index.html` và server tĩnh `server.py`).
- **`Model/`:** Thư mục trống dùng để lưu trữ các local checkpoints cho Qwen và Llama (weights được tự động bỏ qua qua `.gitignore`).

---

## 2. Hướng dẫn khởi chạy Web Demo

### Yêu cầu hệ thống
- Python 3.10+ hỗ trợ chạy học sâu (PyTorch, Transformers, CUDA).

### Các bước cài đặt và khởi chạy

1. **Clone repository này về máy:**
   ```bash
   git clone <github-repo-url>
   cd Targeted-ABSA-for-Vietnamese-Gameshows
   ```
2. **Kích hoạt môi trường chạy (Ví dụ bằng Conda):**
   ```bash
   conda activate se365
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
