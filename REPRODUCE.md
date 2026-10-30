# Tái lập từ đầu đến cuối

Python 3.12, CPU, lệnh chạy từ repository root. Các vòng có mục tiêu và chỉ số khác nhau.

## Kiểm tra bản công bố

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-all.txt
python verify_all.py
```

Không tải corpus/huấn luyện. Kiểm tra bản công bố trước các test/analysis có ghi lại tệp chẩn đoán.

## CAPC

Dùng checkout sạch riêng. Giữ bản results/ gốc và điều khoản dữ liệu ở ngoài checkout trước khi tạo kết quả mới. study.py sẽ tạo results/ khi chạy.

```bash
python download_data.py
python test_integrity.py
python -u study.py select
python -u study.py evaluate
MPLCONFIGDIR=/tmp/ngram-mpl python analyze.py
python profile_inference.py
python audit_solver.py
python make_report.py
python verify_results.py --metrics-only
```

select phải hoàn tất trước evaluate. --metrics-only kiểm tra cấu hình/giao thức và tái tạo metric nhưng bỏ checksum byte của archive cũ vì output/log/timestamp mới khác. Tái lập sau khi đã xem test không phải một xác nhận độc lập mới.

[Hướng dẫn CAPC gốc](docs/CAPC_REPRODUCIBILITY.md), [giao thức](PROTOCOL.md), [sửa lỗi](RUN_CORRECTIONS.md), [điều khoản](results/DATA_LICENSE.md).

## BOLT

Dùng checkout sạch khác. Giữ round2/results/ gốc và điều khoản/metadata ở ngoài checkout trước khi tạo kết quả mới; core.py sẽ tạo thư mục kết quả.

```bash
python download_data.py
python round2/download_fr.py
python round2/test_lattice.py
python round2/test_dual.py
python round2/run.py prepare
python -u round2/run.py select
python -u round2/run.py final
python round2/verify.py
python round2/audit_milp.py
python round2/analyze.py
python round2/audit_optimization.py
python round2/dual_audit.py
python round2/profile.py
python round2/report.py
python round2/verify_recorded.py --skip-checksums
```

select phải khóa cấu hình trước khi xem điểm xác nhận Pháp. Test tiếng Việt là thăm dò. Giữ giới hạn mẫu Allociné/seed/budget theo giao thức; không gọi đây là đánh giá toàn bộ corpus Allociné. --skip-checksums chỉ dùng cho output mới thay byte, không cho archive đã công bố.

Các profiler cần Linux/WSL và /proc; chạy khi không có training song song. Warm latency không gồm cold start/JIT.

[README BOLT](round2/README.md), [giao thức](round2/PROTOCOL.md), [lý thuyết](round2/THEORY.md), [lịch sử](round2/RUN_HISTORY.md), [điều khoản](round2/DATA_LICENSE.md).

Không so trực tiếp Macro-F1 dưới nhiễu lấy mẫu CAPC với RBA theo lattice BOLT. Không có pipeline hybrid được huấn luyện trong bản hợp nhất. Tái lập không tự chứng minh novelty, giữ nghĩa hoặc đóng góp Q1.

## Vòng 3 — chứng nhận truy hồi

Đọc [round3/REPRODUCE.md](round3/REPRODUCE.md) để kiểm chứng ngoại tuyến, chạy 18 unit test, dựng index nguồn được pin, chứng nhận truy vấn mới và tái lập riêng hai lượt 300/970 truy vấn. Không chạy lại trên bản công bố duy nhất hoặc đổi freeze để che các kết quả đã xem.

## Ứng dụng web và audit data v0.1

Chạy `node webapp/test-engine.mjs` và `python application_study/check_archive.py`. Verifier dùng Python chuẩn, tính lại đủ288case/334.815trạng thái; không đổi evidence đã công bố. Xem [hướng dẫn](application_study/README.md), [giao thức](application_study/PROTOCOL.md) và [giới hạn kết quả](application_study/REPORT_VI.md).


## Bộ đệm ứng dụng và oracle trên văn bản mới

[pool_study/README.md](pool_study/README.md) hướng dẫn kiểm tra toàn bộ factor/oracle offline và chạy lại từ nguồn pin. `python verify_all.py` đã gồm audit512 cấu hình mới. Để chỉ kiểm tra phần mới, dùng `python pool_study/check_archive.py` với numpy2.3.5. Không cần GPU hay gán nhãn mới. Bản web500 tài liệu và thí nghiệm lớn Python có scorer/kênh lỗi riêng; xem báo cáo giới hạn.
