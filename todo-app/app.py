"""
Ứng dụng quản lý công việc nội bộ - nhóm KTNB (agribank-todo).

Đặc điểm:
- Dữ liệu lưu TẠM trong bộ nhớ (list Python), mất khi tắt server.
- Mỗi công việc gồm: ten, nguoi_phu_trach, trang_thai.
- Không chứa dữ liệu nhạy cảm, không kết nối database.
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- Hằng số trạng thái ---------------------------------------------------
# Dùng hằng số thay vì gõ chuỗi rải rác để tránh sai chính tả.
DANG_LAM = "dang_lam"
XONG = "xong"

# Nhãn tiếng Việt hiển thị ra giao diện, tương ứng từng trạng thái.
NHAN_TRANG_THAI = {
    DANG_LAM: "Đang làm",
    XONG: "Xong",
}

# --- Thông báo lỗi --------------------------------------------------------
# Chỉ nhận MÃ lỗi trên URL rồi tra ra câu tiếng Việt ở đây, không nhận thẳng
# nội dung thông báo từ URL. Nếu nhận thẳng, người khác có thể gửi cho đồng
# nghiệp một đường link kèm thông báo giả mạo (ví dụ đòi nhập lại mật khẩu).
MA_LOI = {
    "ten_trong": "Vui lòng nhập tên công việc.",
    "khong_tim_thay": "Không tìm thấy công việc.",
    "ten_trong_khi_sua": "Tên công việc không được để trống.",
}

# --- Giới hạn độ dài ------------------------------------------------------
# Thuộc tính maxlength trong HTML chỉ chặn ở trình duyệt, người dùng vẫn có
# thể gửi dữ liệu dài tùy ý. Vì vậy phải cắt bớt ở phía server.
GIOI_HAN_TEN = 200
GIOI_HAN_NGUOI = 100

# --- Kho dữ liệu tạm trong bộ nhớ ----------------------------------------
# danh_sach_cong_viec: list các dict {id, ten, nguoi_phu_trach, trang_thai}
danh_sach_cong_viec = []
_id_tiep_theo = 1  # bộ đếm để cấp id duy nhất cho mỗi công việc


def _cap_id_moi():
    """Cấp một id mới, tăng dần. Đơn giản vì app chỉ chạy 1 tiến trình."""
    global _id_tiep_theo
    id_moi = _id_tiep_theo
    _id_tiep_theo += 1
    return id_moi


def _tim_cong_viec(cong_viec_id):
    """Trả về công việc theo id, hoặc None nếu không tìm thấy."""
    for cv in danh_sach_cong_viec:
        if cv["id"] == cong_viec_id:
            return cv
    return None


def _lam_sach(gia_tri, gioi_han):
    """Bỏ khoảng trắng thừa hai đầu và cắt bớt nếu vượt quá giới hạn."""
    return gia_tri.strip()[:gioi_han]


def _bo_loc_hop_le(gia_tri):
    """Chỉ chấp nhận 3 giá trị bộ lọc; giá trị lạ thì quay về mặc định."""
    return gia_tri if gia_tri in ("tat_ca", DANG_LAM, XONG) else "tat_ca"


# --- Các route ------------------------------------------------------------

@app.route("/")
def trang_chu():
    """
    Hiển thị danh sách công việc.

    Tham số trên URL:
    - loc: 'tat_ca' (mặc định) | 'dang_lam' | 'xong'  -> lọc theo trạng thái
    - sua: id công việc đang được mở form sửa (nếu có)
    - ma_loi: mã thông báo lỗi cần hiển thị (tra trong MA_LOI)
    """
    bo_loc = _bo_loc_hop_le(request.args.get("loc", "tat_ca"))

    # Lọc danh sách theo trạng thái được chọn.
    if bo_loc == "tat_ca":
        danh_sach_hien_thi = danh_sach_cong_viec
    else:
        danh_sach_hien_thi = [
            cv for cv in danh_sach_cong_viec if cv["trang_thai"] == bo_loc
        ]

    # id của công việc đang sửa (nếu người dùng bấm nút "Sửa").
    id_dang_sua = request.args.get("sua", type=int)

    return render_template(
        "index.html",
        cong_viecs=danh_sach_hien_thi,
        bo_loc=bo_loc,
        id_dang_sua=id_dang_sua,
        nhan_trang_thai=NHAN_TRANG_THAI,
        tong_so=len(danh_sach_cong_viec),
        so_dang_lam=sum(1 for cv in danh_sach_cong_viec if cv["trang_thai"] == DANG_LAM),
        so_xong=sum(1 for cv in danh_sach_cong_viec if cv["trang_thai"] == XONG),
        loi=MA_LOI.get(request.args.get("ma_loi")),
    )


@app.route("/them", methods=["POST"])
def them_cong_viec():
    """Thêm công việc mới từ form ở đầu trang."""
    ten = _lam_sach(request.form.get("ten", ""), GIOI_HAN_TEN)
    nguoi_phu_trach = _lam_sach(request.form.get("nguoi_phu_trach", ""), GIOI_HAN_NGUOI)
    bo_loc = _bo_loc_hop_le(request.form.get("loc", "tat_ca"))

    # Tên công việc là bắt buộc; thiếu thì báo lỗi và không thêm.
    if not ten:
        return redirect(url_for("trang_chu", loc=bo_loc, ma_loi="ten_trong"))

    danh_sach_cong_viec.append({
        "id": _cap_id_moi(),
        "ten": ten,
        "nguoi_phu_trach": nguoi_phu_trach or "Chưa phân công",
        "trang_thai": DANG_LAM,  # công việc mới luôn ở trạng thái đang làm
    })

    # Công việc mới luôn ở trạng thái "đang làm". Nếu đang xem bộ lọc "Xong"
    # thì nó sẽ không hiện ra, người dùng dễ tưởng là thêm hỏng -> chuyển về
    # bộ lọc "Tất cả" để thấy ngay kết quả vừa thêm.
    if bo_loc == XONG:
        bo_loc = "tat_ca"

    return redirect(url_for("trang_chu", loc=bo_loc))


@app.route("/sua/<int:cong_viec_id>", methods=["POST"])
def sua_cong_viec(cong_viec_id):
    """Lưu thay đổi tên / người phụ trách của một công việc."""
    cong_viec = _tim_cong_viec(cong_viec_id)
    bo_loc = _bo_loc_hop_le(request.form.get("loc", "tat_ca"))

    if cong_viec is None:
        return redirect(url_for("trang_chu", loc=bo_loc, ma_loi="khong_tim_thay"))

    ten = _lam_sach(request.form.get("ten", ""), GIOI_HAN_TEN)
    if not ten:
        # Giữ nguyên form sửa để người dùng nhập lại.
        return redirect(url_for(
            "trang_chu", loc=bo_loc, sua=cong_viec_id, ma_loi="ten_trong_khi_sua"
        ))

    cong_viec["ten"] = ten
    cong_viec["nguoi_phu_trach"] = _lam_sach(
        request.form.get("nguoi_phu_trach", ""), GIOI_HAN_NGUOI
    ) or "Chưa phân công"
    return redirect(url_for("trang_chu", loc=bo_loc))


@app.route("/xoa/<int:cong_viec_id>", methods=["POST"])
def xoa_cong_viec(cong_viec_id):
    """Xóa một công việc khỏi danh sách."""
    global danh_sach_cong_viec
    bo_loc = _bo_loc_hop_le(request.form.get("loc", "tat_ca"))
    danh_sach_cong_viec = [cv for cv in danh_sach_cong_viec if cv["id"] != cong_viec_id]
    return redirect(url_for("trang_chu", loc=bo_loc))


@app.route("/doi-trang-thai/<int:cong_viec_id>", methods=["POST"])
def doi_trang_thai(cong_viec_id):
    """Đánh dấu hoàn thành / bỏ đánh dấu (đảo trạng thái)."""
    cong_viec = _tim_cong_viec(cong_viec_id)
    bo_loc = _bo_loc_hop_le(request.form.get("loc", "tat_ca"))

    if cong_viec is not None:
        cong_viec["trang_thai"] = XONG if cong_viec["trang_thai"] == DANG_LAM else DANG_LAM

    return redirect(url_for("trang_chu", loc=bo_loc))


if __name__ == "__main__":
    # Chạy ở localhost cho nhóm dùng nội bộ khi phát triển.
    app.run(host="127.0.0.1", port=5000, debug=True)
