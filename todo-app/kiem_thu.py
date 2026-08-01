"""
Script kiểm thử tự động — bảng review Phần 4 (Buổi 3).

Chạy khi server đang bật:  python kiem_thu.py
Kiểm tra đủ 6 dòng trong bảng SPEC và in kết quả Đạt / KHÔNG ĐẠT.
"""

import io
import re
import sys
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

GOC = "http://127.0.0.1:5000"
ket_qua = []  # [(ten_dong, dat?, ghi_chu)]


# --- Tiện ích gọi HTTP ----------------------------------------------------

def get(duong_dan=""):
    with urllib.request.urlopen(GOC + duong_dan) as r:
        return r.read().decode("utf-8")


def post(duong_dan, du_lieu=None):
    body = urllib.parse.urlencode(du_lieu or {}).encode("utf-8")
    req = urllib.request.Request(GOC + duong_dan, data=body)
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8"), r.url


def lay_ten(html):
    """Trích danh sách tên công việc đang hiển thị."""
    return re.findall(r'class="ten">([^<]*)<', html)


def lay_nguoi(html):
    return re.findall(r'class="ten-nguoi">([^<]*)<', html)


def lay_ids(html):
    """Trích id các công việc từ action của form xóa."""
    return [int(x) for x in re.findall(r'/xoa/(\d+)', html)]


def lay_so_bo_loc(html):
    """Trả về (tong, dang_lam, xong) đọc từ nhãn trên 3 nút lọc."""
    so = re.findall(r'\((\d+)\)', html)
    return tuple(int(x) for x in so[:3])


def ghi(ten_dong, dat, ghi_chu=""):
    ket_qua.append((ten_dong, dat, ghi_chu))
    print(f"  {'✅ ĐẠT     ' if dat else '❌ KHÔNG ĐẠT'} | {ten_dong}" + (f"  → {ghi_chu}" if ghi_chu else ""))


def don_sach():
    """Xóa hết công việc để bắt đầu từ trạng thái trắng."""
    for i in lay_ids(get("/?loc=tat_ca")):
        post(f"/xoa/{i}")


# --- Chạy bảng kiểm tra ---------------------------------------------------

print("=" * 74)
print("BẢNG REVIEW PHẦN 4 — đối chiếu với SPEC.md")
print("=" * 74)
don_sach()

MAU = [
    ("Rà soát Thông tư 41/2016", "Nguyễn Văn A"),
    ("Kiểm tra hồ sơ tín dụng chi nhánh Láng Hạ", "Trần Thị B"),
    ("Lập báo cáo kiểm toán quý III", "Lê Văn C"),
]

# --- Dòng 1: Thêm 3 công việc mẫu, kiểm tra hiển thị đúng ---
for ten, nguoi in MAU:
    post("/them", {"ten": ten, "nguoi_phu_trach": nguoi})
html = get("/")
ten_ht, nguoi_ht = lay_ten(html), lay_nguoi(html)
dat = ten_ht == [t for t, _ in MAU] and nguoi_ht == [n for _, n in MAU]
ghi("Thêm công việc", dat, f"hiển thị {len(ten_ht)}/3 mục, tên và người phụ trách khớp" if dat
    else f"nhận được {ten_ht} / {nguoi_ht}")

# --- Dòng 2: Sửa tên 1 công việc, kiểm tra cập nhật đúng ---
ids = lay_ids(get("/"))
TEN_MOI = "Rà soát Thông tư 41/2016 (bản cập nhật)"
post(f"/sua/{ids[0]}", {"ten": TEN_MOI, "nguoi_phu_trach": "Nguyễn Văn A"})
ten_ht = lay_ten(get("/"))
dat = TEN_MOI in ten_ht and MAU[0][0] not in ten_ht
ghi("Sửa công việc", dat, "tên mới thay đúng chỗ, tên cũ biến mất" if dat else f"nhận được {ten_ht}")

# --- Dòng 3: Xóa 1 công việc, kiểm tra biến mất khỏi danh sách ---
truoc = len(lay_ten(get("/")))
post(f"/xoa/{ids[1]}")
sau_html = get("/")
dat = len(lay_ten(sau_html)) == truoc - 1 and MAU[1][0] not in lay_ten(sau_html)
ghi("Xóa công việc", dat, f"{truoc} → {len(lay_ten(sau_html))} mục, đúng mục bị xóa" if dat else "xóa không đúng")

# --- Dòng 4: Đánh dấu xong 1 công việc, kiểm tra trạng thái đổi ---
ids = lay_ids(get("/"))
post(f"/doi-trang-thai/{ids[0]}")
html = get("/")
dat_xong = 'nhan-xong' in html
post(f"/doi-trang-thai/{ids[0]}")          # bấm lại để kiểm tra đảo ngược
dat_lai = 'nhan-xong' not in get("/")
post(f"/doi-trang-thai/{ids[0]}")          # đặt lại là xong để dùng cho dòng 5
ghi("Đánh dấu hoàn thành", dat_xong and dat_lai,
    "đánh dấu xong được và bỏ đánh dấu được" if dat_xong and dat_lai else "trạng thái không đổi đúng")

# --- Dòng 5: Thử cả 3 bộ lọc, đối chiếu số lượng hiển thị ---
tong, dang_lam, xong = lay_so_bo_loc(get("/"))
n_tat_ca = len(lay_ten(get("/?loc=tat_ca")))
n_dang_lam = len(lay_ten(get("/?loc=dang_lam")))
n_xong = len(lay_ten(get("/?loc=xong")))
dat = (tong, dang_lam, xong) == (n_tat_ca, n_dang_lam, n_xong) and tong == dang_lam + xong
ghi("Lọc theo trạng thái", dat,
    f"nhãn ({tong}/{dang_lam}/{xong}) khớp số mục thực tế ({n_tat_ca}/{n_dang_lam}/{n_xong})")

# --- Dòng 6: Rà toàn bộ nhãn, nút bấm, thông báo là tiếng Việt ---
NHAN_CAN_CO = ["Quản lý công việc", "Thêm công việc", "Tất cả", "Đang làm",
               "Xong", "Sửa", "Xóa", "Người phụ trách", "Tên công việc"]
thieu = [n for n in NHAN_CAN_CO if n not in html]
# Bắt các từ tiếng Anh còn sót trong phần nội dung hiển thị (bỏ qua thẻ HTML)
noi_dung = re.sub(r"<[^>]+>", " ", html)
TU_ANH = ["Add", "Edit", "Delete", "Task", "Status", "All", "Done", "Submit", "Filter"]
sot_anh = [t for t in TU_ANH if re.search(rf"\b{t}\b", noi_dung)]
# Kiểm tra cả thông báo lỗi
loi_html = get("/?ma_loi=ten_trong")
co_thong_bao_viet = "Vui lòng nhập tên công việc." in loi_html
dat = not thieu and not sot_anh and co_thong_bao_viet
ghi("Giao diện tiếng Việt", dat,
    "đủ nhãn/nút/thông báo tiếng Việt, không sót từ tiếng Anh" if dat
    else f"thiếu {thieu}; sót tiếng Anh {sot_anh}")

# --- Kiểm tra bổ sung: các lỗi biên đã sửa ở Phần 5 ---
print("-" * 74)
print("KIỂM TRA BỔ SUNG — các lỗi biên đã sửa ở Phần 5")

# (a) Định dạng hiển thị theo mẫu few-shot
html = get("/")
noi_dung = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))
dat = re.search(r"\[(Đang làm|Xong)\] .+ — phụ trách: .+", noi_dung) is not None
ghi("Định dạng hiển thị theo mẫu", dat,
    "khớp mẫu “[Đang làm] Tên công việc — phụ trách: Người”" if dat else "chưa đúng mẫu")

# (b) Thêm công việc trong lúc đang lọc "Xong" phải thấy được kết quả
post("/them", {"ten": "Việc thêm khi đang lọc Xong", "nguoi_phu_trach": "Phạm D", "loc": "xong"})
dat = "Việc thêm khi đang lọc Xong" in get("/?loc=tat_ca")
ghi("Thêm khi đang lọc “Xong”", dat,
    "tự chuyển về “Tất cả” nên thấy ngay việc vừa thêm" if dat else "việc vừa thêm bị ẩn")

# (c) Server tự cắt tên quá dài (maxlength của HTML có thể bị vượt qua)
post("/them", {"ten": "Z" * 5000, "nguoi_phu_trach": "W" * 5000})
dai_nhat = max(len(t) for t in lay_ten(get("/")))
dat = dai_nhat <= 200
ghi("Giới hạn độ dài phía server", dat, f"gửi 5000 ký tự → lưu {dai_nhat} ký tự")

# (d) Không cho nhét thông báo tùy ý qua URL
h = get("/?ma_loi=" + urllib.parse.quote("Phiên đăng nhập hết hạn, nhập lại mật khẩu"))
dat = "mật khẩu" not in h
ghi("Chặn thông báo giả mạo qua URL", dat,
    "mã lỗi lạ bị bỏ qua, không hiện thông báo" if dat else "vẫn hiện thông báo bịa từ URL")

# (e) Chuỗi dài không được làm tràn ngang trang (cần playwright; không có thì bỏ qua)
try:
    from playwright.sync_api import sync_playwright
    post("/them", {"ten": "Z" * 300, "nguoi_phu_trach": "W" * 300})
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1050, "height": 700})
        pg.goto(GOC)
        tran = pg.evaluate(
            "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
        )
        b.close()
    ghi("Không tràn ngang khi tên quá dài", not tran,
        "chữ tự xuống dòng, không sinh thanh cuộn ngang" if not tran else "trang bị cuộn ngang")
except ImportError:
    print("  ⏭️  BỎ QUA    | Không tràn ngang khi tên quá dài (chưa cài playwright)")

# --- Dọn dẹp ---
# Bắt buộc: script tạo ra dữ liệu rác (chuỗi ZZZ..., WWW... để thử giới hạn
# độ dài). Không dọn thì chúng nằm lại trong bộ nhớ server và hiện ra trên
# giao diện, người dùng tưởng là lỗi ứng dụng.
don_sach()
con_lai = len(lay_ten(get("/?loc=tat_ca")))
print("-" * 74)
print(f"Đã dọn dữ liệu kiểm thử — còn lại {con_lai} công việc trong danh sách.")

# --- Tổng kết ---
print("-" * 74)
so_dat = sum(1 for _, d, _ in ket_qua if d)
print(f"KẾT QUẢ: {so_dat}/{len(ket_qua)} dòng ĐẠT")
if so_dat < len(ket_qua):
    print("Các dòng KHÔNG ĐẠT cần ghi chú và sửa ở Phần 5:")
    for t, d, g in ket_qua:
        if not d:
            print(f"  - {t}: {g}")
print("=" * 74)
