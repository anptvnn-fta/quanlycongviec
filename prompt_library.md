# Prompt Template Library — KTNB Agribank

Thư viện prompt dùng lại xuyên suốt khóa học. Mỗi mẫu viết theo cấu trúc
5 thành phần: **Role → Context → Goal → Constraints → Output Format**.

Chỉ ghi vào đây những prompt đã dùng thật và cho kết quả dùng được.

---

## Mẫu 1 — Sinh ứng dụng CRUD đơn giản

*Dùng ở Buổi 3, Phần 3 — sinh toàn bộ ứng dụng quản lý công việc.*

```
[ROLE] Bạn là full-stack developer.

[CONTEXT] Đây là dự án agribank-rag của một nhóm KTNB. Sản phẩm đầu
tiên là ứng dụng quản lý công việc nội bộ nhóm.

[GOAL] Tạo web app quản lý công việc: danh sách task, thêm/sửa/xóa,
đánh dấu hoàn thành, lọc theo trạng thái (tất cả / đang làm / xong).

[CONSTRAINTS] Giao diện tiếng Việt, lưu dữ liệu tạm trong bộ nhớ,
code gọn, dễ đọc, có chú thích. Mỗi công việc gồm: ten,
nguoi_phu_trach, trang_thai.

[OUTPUT] Ứng dụng chạy được + hướng dẫn chạy.
```

**Kết quả thực tế:** sinh ra Flask + Jinja2 gồm `app.py`, `templates/index.html`,
`static/style.css`, `requirements.txt`, `README.md`. Chạy được ngay, 6/6 dòng
trong bảng review Phần 4 đều Đạt ở lần chạy đầu.

**Rút kinh nghiệm:** phần `[CONSTRAINTS]` là phần quyết định. Nếu bỏ đi thì:
- Giao diện nhiều khả năng ra tiếng Anh (mặc định của mô hình).
- AI dễ tự thêm database (SQLite) — sai với yêu cầu "lưu tạm trong bộ nhớ" của buổi này.
- Tên trường có thể thành `name`/`assignee`/`status` thay vì `ten`/`nguoi_phu_trach`/`trang_thai`,
  gây lệch với SPEC.md và khó nối vào các buổi sau.
- Code có thể dùng framework nặng (React + build tool) thay vì "gọn, dễ đọc".

**Cần bổ sung khi dùng lại:** nói rõ ngôn ngữ/framework mong muốn nếu có ràng buộc
môi trường (ví dụ "dùng Python + Flask, không dùng JavaScript framework").

---

## Mẫu 2 — Self-review edge case

*Dùng ở Buổi 3, Phần 5 — bắt AI tự rà lỗi biên sau khi sinh code.*

```
[ROLE] Bạn là kiểm toán viên nội bộ đang review code, không phải người viết code.

[CONTEXT] Ứng dụng quản lý công việc trong thư mục todo-app/ vừa được sinh ra
và đã qua bảng kiểm tra chức năng cơ bản (6/6 đạt). Đặc tả gốc ở SPEC.md.

[GOAL] Tự rà soát lại code vừa sinh, tìm các trường hợp biên chưa xử lý:
danh sách rỗng, sửa/xóa công việc không tồn tại, nhập tên công việc trống,
dữ liệu vượt quá độ dài cho phép, tham số lạ trên URL.

[CONSTRAINTS] Chỉ sửa phần code liên quan tới lỗi tìm được, không đổi các chức
năng đang chạy đúng. Giữ nguyên giao diện tiếng Việt và cấu trúc dữ liệu
ten / nguoi_phu_trach / trang_thai theo SPEC.md.

[OUTPUT] Danh sách lỗi đã phát hiện kèm cách tái hiện, code đã sửa, và bằng
chứng chạy lại cho thấy lỗi không còn.
```

**Kết quả thực tế:** tìm ra 3 lỗi mà bảng kiểm tra chức năng không bắt được —

| # | Lỗi | Cách sửa |
|---|---|---|
| 1 | Thêm công việc trong lúc đang lọc "Xong" → việc mới không hiện, tưởng thêm hỏng | Sau khi thêm, tự chuyển bộ lọc về "Tất cả" |
| 2 | `maxlength` chỉ chặn ở trình duyệt, gửi 5000 ký tự vẫn lưu đủ 5000 | Cắt bớt ở phía server (200 ký tự tên, 100 ký tự người phụ trách) |
| 3 | Nội dung thông báo lỗi lấy thẳng từ URL → gửi link kèm thông báo giả mạo được | Chỉ nhận **mã** lỗi rồi tra ra câu tiếng Việt trong code |

**Rút kinh nghiệm:** ràng buộc *"chỉ sửa phần liên quan"* rất quan trọng — nếu
không, AI hay nhân tiện viết lại cả file và làm hỏng chức năng đang chạy đúng.
Yêu cầu *"bằng chứng chạy lại"* buộc AI phải thật sự chạy chứ không chỉ tuyên bố
"đã sửa xong".

---

## Mẫu 3 — Few-shot chuẩn hóa định dạng hiển thị

*Dùng ở Buổi 3, Phần 5 — thống nhất cách hiển thị một dòng công việc.*

```
[ROLE] Bạn là full-stack developer.

[CONTEXT] Ứng dụng quản lý công việc trong todo-app/ đang hiển thị tên công việc,
người phụ trách và trạng thái ở ba vị trí rời rạc, đọc không thống nhất.

[GOAL] Chuẩn hóa để mỗi công việc hiển thị theo đúng định dạng ví dụ sau:
"[Đang làm] Rà soát Thông tư 41/2016 — phụ trách: Nguyễn Văn A"
Áp dụng cho toàn bộ danh sách, ở cả 3 bộ lọc.

[CONSTRAINTS] Chỉ đổi phần hiển thị, không đụng tới logic thêm/sửa/xóa/lọc.
Giữ nguyên các class CSS mà script kiểm thử đang dùng.

[OUTPUT] Code đã sửa + kết quả chạy lại bảng kiểm tra cho thấy 6 dòng vẫn Đạt.
```

**Kết quả thực tế:** đúng định dạng ngay lần đầu. Đưa **một ví dụ cụ thể** hiệu quả
hơn nhiều so với mô tả bằng lời ("hiển thị trạng thái trước, rồi tên, rồi người phụ trách").

**Rút kinh nghiệm:** khi đổi giao diện, phải nói rõ *"giữ nguyên các class CSS mà
script kiểm thử đang dùng"* — lần đầu quên câu này thì script kiểm thử gãy dù ứng
dụng vẫn chạy đúng.

---

*(Còn tiếp — bổ sung ở Buổi 4, mục tiêu tối thiểu 10 mẫu khi hết cụm buổi 1–4.)*
