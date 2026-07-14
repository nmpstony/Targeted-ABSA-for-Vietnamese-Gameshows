# Đóng góp và Vai trò của Hệ thống Web Demo Dashboard trong Đề tài Nghiên cứu

Hệ thống Web Demo Dashboard không chỉ đơn thuần là một công cụ trực quan hóa kết quả dự án, mà đóng vai trò là một **nền tảng tích hợp (Unified Evaluation Platform)** quan trọng đóng góp trực tiếp vào sự thành công và tính thực tiễn của đề tài nghiên cứu **Targeted Aspect-Based Sentiment Analysis (Targeted ABSA) cho Gameshow âm nhạc Việt Nam**. 

Dưới đây là các đóng góp cốt lõi của hệ thống Demo đối với đề tài:

---

## 1. Hiện thực hóa Lý thuyết & Tối ưu hóa Triển khai Thực tế (Practical Deployment & Resource Optimization)
*   **Giải pháp tối ưu hóa bộ nhớ cục bộ (Lazy Loading & VRAM Cleanup)**: Đồ án nghiên cứu sử dụng nhiều mô hình có kích thước tham số lớn (từ mô hình Encoder 110M-370M như ViBERT/XLM-R cho đến các LLMs sinh văn bản 3B như Llama-3.2/Qwen-2.5). Demo đã hiện thực hóa cơ chế nạp lười (Lazy Load) và giải phóng bộ nhớ tự động (`gc.collect` và giải phóng cache CUDA) sau mỗi request. Nhờ đó, cả 4 mô hình lớn có thể chạy đồng thời tuần tự trên một máy chủ cá nhân có tài nguyên VRAM hạn chế (chỉ từ 6-8GB) mà không gây tràn bộ nhớ.
*   **Kiến trúc đa luồng chống nghẽn (Concurrency)**: Bằng cách chuyển đổi sang máy chủ đa luồng (`ThreadingTCPServer`), hệ thống duy trì tính sẵn sàng cao. Người dùng có thể duyệt dữ liệu, xem biểu đồ phân tích thống kê một cách mượt mà ngay cả khi mô hình học sâu ở Live Playground đang chiếm dụng CPU/GPU để chạy suy luận.

## 2. Công cụ Đánh giá Định tính trực quan và Đối sánh mô hình (Qualitative Evaluation & Comparative Playground)
*   **Live Playground - Chế độ so sánh song song (Comparative Mode)**: Thay vì chỉ đánh giá mô hình thông qua các chỉ số F1 và Accuracy tĩnh trên tập test, Demo cung cấp giao diện đối chiếu trực quan kết quả suy luận của cả 4 mô hình cùng lúc trên cùng một văn bản đầu vào. Điều này giúp các nhà nghiên cứu:
    *   So sánh trực tiếp khả năng nhận dạng thực thể (NER) giữa các mô hình Encoder-based và Generative LLMs.
    *   Đánh giá định tính năng lực chịu lỗi đối với ngôn ngữ mạng (teencode, viết tắt, từ mượn tiếng Anh) đặc trưng của bình luận gameshow Việt Nam.
*   **Highlight kết quả trực quan**: Tự động bôi màu làm nổi bật đối tượng được nhắc đến (Target) cùng với phân cực cảm xúc tương ứng (Xanh lá cho Tích cực, Đỏ cho Tiêu cực, Vàng cho Trung lập), hỗ trợ người dùng cuối nhanh chóng nắm bắt cấu trúc ý kiến phức tạp trong câu mà không cần đọc hiểu các nhãn BIO/NER thô.

## 3. Cầu nối kiểm định dữ liệu và Phân tích lỗi (Data Exploration & Error Analysis Platform)
*   **Khám phá dữ liệu tập trung (Dataset Explorer)**: Tích hợp bộ lọc đa chiều (lọc theo Aspect, Sentiment, Nguồn gameshow) cùng tính năng tìm kiếm văn bản nhanh. Điều này giúp các thành viên phát triển đề tài dễ dàng kiểm tra chéo độ chính xác của tập dữ liệu vàng (Gold standard), đồng thời đối chiếu dữ liệu huấn luyện thực tế với đầu ra của mô hình.
*   **Trưng bày các lỗi điển hình (Case Studies)**: Dashboard lưu trữ trực tiếp các trường hợp lỗi kinh điển gặp phải trong thực tế (Lỗi xung đột cảm xúc - Sentiment Confusion, Lỗi trượt ranh giới từ - Boundary Failure, Lỗi nhầm lẫn Aspect gần nghĩa). Việc trực quan hóa các lỗi này giúp định hướng cải tiến mô hình trong tương lai (ví dụ: chuyển từ cơ chế Mean Pooling sang Attention Pooling hoặc chuyển sang Generative ABSA).

## 4. Tăng cường Giá trị Khoa học và Khả năng Ứng dụng Thực tiễn (Value and Application Potential)
*   **Tiền đề cho các hệ thống Social Listening thực tế**: Demo chứng minh rằng kiến trúc học đa nhiệm đề xuất (Unified Multi-Task Head) dựa trên XLM-RoBERTa không chỉ đạt hiệu năng cao về mặt học thuật mà còn có **tốc độ suy luận lý tưởng (~10ms/câu)**. Điều này chứng minh mô hình hoàn toàn khả thi để tích hợp vào các hệ thống lắng nghe mạng xã hội quy mô lớn thời gian thực.
*   **Tính tương tác cao phục vụ báo cáo**: Hệ thống đóng vai trò là phương tiện trực quan sinh động nhất giúp hội đồng đánh giá và độc giả dễ dàng tương tác, trải nghiệm thực tế năng lực của các mô hình học sâu thay vì chỉ đọc các báo cáo văn bản thông thường.
