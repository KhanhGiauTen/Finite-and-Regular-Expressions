# Finite and Regular Expressions

Dự án này là sản phẩm thuộc học phần **Ngôn ngữ hình thức**, tập trung nghiên cứu và cài đặt các thuật toán chuyển đổi từ **Biểu thức chính quy (Regular Expression)** sang **NFA** và **DFA**, đồng thời mô phỏng quá trình đoán nhận chuỗi. Hệ thống được xây dựng hoàn toàn bằng **Python** với giao diện đồ họa **Tkinter** trực quan.

---

## Thành Viên Nhóm

| STT | Họ và Tên | MSSV |
|-----|-----------|------|
| 1 | Nguyễn Quốc Khánh | [MSSV] |
| 2 | Tô Xuân Đông | [MSSV] |
| 3 | Ngô Chánh Phong | [MSSV] |
| 4 | Phùng Chí Tâm | [MSSV] |
| 5 | Bùi Trọng Nguyên | [MSSV] |

**Giảng viên hướng dẫn:** ThS. Hồ Thanh Tuyến

---

## Tính Năng Chính

- **Chuyển đổi Regex sang NFA:** Sử dụng giải thuật Thompson's Construction kết hợp với Shunting Yard để xử lý độ ưu tiên toán tử.
- **Chuyển đổi NFA sang DFA:** Cài đặt thuật toán Subset Construction (Mô phỏng tập hợp con) để loại bỏ tính không đơn định.
- **Mô phỏng (Simulation):** Kiểm tra tính hợp lệ của chuỗi input thông qua DFA đã sinh ra (trả về kết quả ACCEPT/REJECT).
- **Trực quan hóa:** Tích hợp thư viện Graphviz để vẽ và hiển thị sơ đồ trạng thái (State Diagram) ngay trên giao diện.
- **Nhập liệu đa dạng:** Hỗ trợ nhập Regex tự động hoặc nhập cấu trúc DFA thủ công.

---

## Yêu Cầu Hệ Thống (Prerequisites)

Để chạy được dự án, máy tính cần đáp ứng các yêu cầu sau:

- **Python 3.8+:** Môi trường thực thi chính.
- **Graphviz (Software):** Phần mềm lõi để vẽ đồ thị.
  - Tải bản cài đặt cho Windows tại: [Graphviz Download](https://graphviz.org/download/)
  - **LƯU Ý QUAN TRỌNG:** Khi cài đặt, bắt buộc tích chọn **"Add Graphviz to the system PATH for all users"** để Python có thể gọi lệnh vẽ hình.

---

## Cài Đặt Môi Trường

### Bước 1: Cài đặt thư viện Python

Mở Terminal (CMD hoặc PowerShell) tại thư mục gốc của dự án và chạy lệnh sau để cài đặt các gói phụ thuộc:

```bash
pip install graphviz pillow
```

*(Lưu ý: Thư viện `tkinter` thường đã được tích hợp sẵn trong bộ cài Python chuẩn)*

---

## Hướng Dẫn Sử Dụng

Sau khi cài đặt xong, chạy lệnh sau để khởi động ứng dụng:

```bash
python app.py
```

Giao diện **Mini-JFLAP** sẽ hiện ra. Bạn thực hiện theo quy trình sau:

### 1. Chế độ Regex (Mặc định)

1. **Nhập Regex:** Điền biểu thức vào ô nhập liệu (Ví dụ: `(a+b)*abb`).
2. **Chuyển đổi:** Nhấn nút **"Chuyển đổi: Regex -> NFA -> DFA"**. Hệ thống sẽ xử lý và hiển thị sơ đồ DFA ở khung bên trái.
