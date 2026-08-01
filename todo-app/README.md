# agribank-todo — Ứng dụng quản lý công việc nội bộ

Web app quản lý công việc cho nhóm Kiểm toán nội bộ (KTNB).
Dữ liệu lưu **tạm trong bộ nhớ** — tắt server là mất, chưa dùng database.

## Chức năng

| Chức năng | Cách dùng trên giao diện |
|---|---|
| Thêm công việc | Nhập *Tên công việc* + *Người phụ trách* ở form trên cùng → bấm **Thêm công việc** |
| Sửa công việc | Bấm **Sửa** ở dòng tương ứng → chỉnh → bấm **Lưu** (hoặc **Hủy**) |
| Xóa công việc | Bấm **Xóa** → xác nhận |
| Đánh dấu hoàn thành | Bấm ô vuông bên trái tên công việc (bấm lại để bỏ đánh dấu) |
| Lọc theo trạng thái | Bấm **Tất cả** / **Đang làm** / **Xong** |

Mỗi công việc gồm 3 trường theo spec: `ten`, `nguoi_phu_trach`, `trang_thai`
(`trang_thai` nhận giá trị `dang_lam` hoặc `xong`).

## Yêu cầu

- Python 3.9 trở lên
- Flask 3.x

## Hướng dẫn chạy

### 1. Vào thư mục ứng dụng

```bash
cd todo-app
```

### 2. Cài thư viện

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
python app.py
```

### 4. Mở trình duyệt

http://127.0.0.1:5000

Dừng server: bấm `Ctrl + C` trong cửa sổ terminal.

> **Đổi cổng** nếu cổng 5000 đang bận: sửa `port=5000` ở cuối [app.py](app.py).
>
> **Cho máy khác trong mạng LAN truy cập**: đổi `host="127.0.0.1"` thành
> `host="0.0.0.0"`. Chỉ nên làm trong mạng nội bộ tin cậy — app chưa có
> đăng nhập, ai vào được cũng sửa/xóa được dữ liệu.

## Cấu trúc dự án

```
SPEC.md                      # Đặc tả yêu cầu (nguồn sự thật duy nhất)
prompt_library.md            # Thư viện prompt dùng lại
todo-app/
  app.py                     # ⭐ Toàn bộ logic thêm/sửa/xóa/lọc + dữ liệu trong bộ nhớ
  templates/index.html       # Giao diện (Jinja2), toàn bộ nhãn tiếng Việt
  static/style.css           # CSS
  kiem_thu.py                # Script kiểm thử tự động 10 mục
  requirements.txt           # Thư viện cần cài
```

File chứa logic chính là **`app.py`** — mỗi chức năng là một route:
`them_cong_viec` · `sua_cong_viec` · `xoa_cong_viec` · `doi_trang_thai` ·
lọc nằm trong `trang_chu`.

## Kiểm thử tự động

Khi server đang chạy, mở terminal thứ hai:

```bash
cd todo-app
python kiem_thu.py
```

Script chạy đủ 6 dòng trong bảng review + 4 mục kiểm tra lỗi biên, in
`ĐẠT / KHÔNG ĐẠT` cho từng dòng.

## Ghi chú kỹ thuật

- Kiến trúc **form POST + redirect** (không dùng JavaScript framework), nên
  không bị gửi lại form khi người dùng bấm F5.
- Jinja2 tự escape dữ liệu người dùng nhập → an toàn trước XSS.
- Không có dữ liệu nhạy cảm nào được hardcode trong mã nguồn.
- `debug=True` chỉ dùng khi phát triển; **phải tắt** nếu triển khai thật.

## Hướng phát triển tiếp

- Lưu xuống database (SQLite / PostgreSQL) để không mất dữ liệu
- Thêm đăng nhập và phân quyền theo người dùng
- Bổ sung hạn hoàn thành, mức ưu tiên, ghi chú cho từng công việc
