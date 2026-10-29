# N-Gram — bản nghiên cứu thống nhất CAPC và BOLT

Bản hợp nhất ngày **29/10/2026**: hai ứng viên phương pháp, kết quả đã công bố và một quy trình kiểm chứng chung.

**Chưa xác lập được novelty hoặc mức đóng góp đủ Q1. Chưa huấn luyện hay đánh giá một thuật toán lai CAPC–BOLT.** Hợp nhất mã và kết quả không thay đổi kết luận khoa học của hai vòng.

| Vòng | Phương pháp | Mã và giao thức | Kết luận |
|---|---|---|---|
| 1 | CAPC: consistency có trọng số nhập nhằng | [study.py](study.py), [PROTOCOL.md](PROTOCOL.md) | Chưa vượt rõ augmentation/uniform/shuffled controls |
| 2 | BOLT: tìm biến thể bất lợi chính xác và huấn luyện robust | [round2/run.py](round2/run.py), [lý thuyết](round2/THEORY.md), [giao thức](round2/PROTOCOL.md) | Tăng RBA trước augmentation; chưa có lợi thế nhất quán trước đối chứng mạnh |

Đọc [tổng quan và khả năng bổ trợ](docs/INTEGRATION_VI.md), [báo cáo CAPC](REPORT_VI.md) và [báo cáo BOLT](round2/REPORT_VI.md). Điểm CAPC và BOLT không so trực tiếp vì hai vòng dùng phép đo và tập biến đổi khác nhau.

## Bắt đầu và kiểm chứng bản công bố

Python 3.12, CPU. Chạy từ repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-all.txt
python verify_all.py
```

Lệnh cuối kiểm tra manifest hợp nhất, cấu hình khóa, checksum và tái tạo độc lập **2.430 dòng metric CAPC**, **270 dòng metric BOLT**, **162 dòng chẩn đoán BOLT**. Không tải corpus hoặc huấn luyện lại. Để chỉ kiểm tra bản công bố, numpy==2.3.5 và pandas==2.2.3 là đủ.

Chạy model BOLT đã xuất:

```bash
python round2/predict.py --model round2/results/UIT-VSFC_bolt_model.npz --text 'bài giảng rất tốt' --budget 3
```

Cờ bất biến chỉ áp dụng cho lattice biến đổi dấu đã định; không khẳng định nhãn dự đoán đúng hay mọi biến thể giữ nghĩa.

## Quy trình từ dữ liệu đến báo cáo

[REPRODUCE.md](REPRODUCE.md) ghi cách tải dữ liệu, kiểm tra, chọn tham số, huấn luyện, phân tích và audit cả hai vòng. Tái lập đầy đủ trên checkout sạch riêng cho từng vòng.

- [Hướng dẫn CAPC gốc](docs/CAPC_REPRODUCIBILITY.md): giữ nguyên README trước hợp nhất; lệnh/đường dẫn bên trong tính từ repository root.
- [Hướng dẫn BOLT](round2/README.md).
- [Novelty CAPC](RELATED_WORK.md), [novelty BOLT](round2/NOVELTY.md).
- [Sửa lỗi CAPC](RUN_CORRECTIONS.md), [BOLT](round2/RUN_HISTORY.md).
- [Metadata hợp nhất](PROJECT_STATUS.json).

## Dữ liệu và tính tái lập

Dùng nhãn công khai có sẵn, không có đợt gán nhãn mới bằng con người. Raw corpus và file Word không nằm trong bản công bố. MIT trong LICENSE áp dụng cho mã nguồn; điều khoản dữ liệu/mô hình phải đọc riêng tại [CAPC](results/DATA_LICENSE.md) và [BOLT](round2/DATA_LICENSE.md).

CAPC có 156 fit, BOLT có 99 fit theo giao thức, bao gồm chọn tham số và chạy lặp. Tổng 255 fit không phải 255 xác nhận khoa học độc lập. Test tiếng Việt đã được xem ở vòng 1 nên kết quả vòng 2 trên đó là thăm dò; tiếng Pháp là xác nhận sau khóa mã/cấu hình.

Mã khoa học, giao thức khóa, mô hình, dự đoán và metric hai vòng được giữ nguyên byte. README mới làm trang tổng quan nên chỉ hash README trong manifest CAPC được cập nhật. README cũ giữ tại docs/CAPC_REPRODUCIBILITY.md và commit CAPC gốc. Manifest hợp nhất kiểm tra các tệp bổ sung. CI thành công không xác lập novelty hay khả năng được nhận Q1.
