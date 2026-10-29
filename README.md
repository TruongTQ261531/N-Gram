# N-Gram — ba vòng nghiên cứu và một bản công bố thống nhất

Cập nhật 29/10/2026. Vòng 3 đã xây dựng và thực nghiệm **bộ chứng nhận rời rạc cho truy hồi character n-gram**, có lý thuyết, đối chứng LP/MILP, 300 truy vấn xác nhận ban đầu và 970 truy vấn xác nhận độc lập. Mã/kết quả nằm trong [round3](round3/README.md).

**Chưa xác lập đủ novelty hoặc khả năng được nhận Q1.** Kết quả mới hỗ trợ một đóng góp hẹp về khả năng chứng nhận; không làm tăng chất lượng bộ xếp hạng và không biến ba hướng thành một mô hình lai đã được kiểm thử.

| Vòng | Nội dung | Kết luận hiện tại |
|---|---|---|
| 1 — CAPC | Consistency có trọng số nhập nhằng; 156 fit theo giao thức | Chưa vượt rõ đối chứng mạnh; [báo cáo](REPORT_VI.md) |
| 2 — BOLT | Oracle nhiễu và huấn luyện robust; 99 fit theo giao thức | Chưa có lợi thế nhất quán; [báo cáo](round2/REPORT_VI.md) |
| 3 — Chứng nhận truy hồi | Scorer character-BM25 cố định; LP dùng chung truy vấn và cover xung đột rời rạc; không fit thêm | Cải thiện so với LP trên dữ liệu mới, có ý nghĩa sau Holm ở 2/3 corpus; [báo cáo đầy đủ](round3/REPORT_VI.md) |

## Kết quả mới: giữ winner trong top-10, tối đa hai token bị sửa

Đây là tỷ lệ truy vấn **được chứng nhận** trong mô hình nhiễu hữu hạn, không phải accuracy hay recall.

| Corpus | Truy vấn mới | Best LP + enumeration | Phương pháp rời rạc | p exact sau Holm |
|---|---:|---:|---:|---:|
| SciFact | 199 | 115/199 (57,79%) | 123/199 (61,81%) | 0,015625 |
| NFCorpus | 223 | 41/223 (18,39%) | 45/223 (20,18%) | 0,125 |
| FiQA | 548 | 71/548 (12,96%) | 91/548 (16,61%) | 0,00000572 |

NFCorpus chưa đủ bằng chứng thống kê. Mọi truy vấn tăng thêm đều có generic LP chạy thành công, nhưng chỉ 4/2/7 winner tăng thêm có qrel dương. Lượt 300 truy vấn đầu giữ riêng, không gộp để sửa p-value. Các cấu hình không có lợi, MILP thắng, cap/timeout và sai lệch luồng ban đầu đều được báo cáo.

Đọc [bản thảo tiếng Anh](round3/MANUSCRIPT.md), [lý thuyết](round3/THEORY.md), [rà soát tài liệu mới và rủi ro novelty](round3/RELATED_WORK_UPDATE.md), [lịch sử chạy/sửa lỗi](round3/RUN_HISTORY.md). Các thành phần LP, DP, graph cover, pruning và top-K certification đã có prior art, đặc biệt CostCert; không được gọi riêng chúng là phát minh mới.

## Kiểm tra toàn bộ bản công bố

Python 3.12, từ repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-all.txt
python verify_all.py
python -m unittest discover -s round3 -p 'test_*.py'
```

Verifier ngoại tuyến tái tính metric từ dự đoán, CI/exact test/Holm, ID/nguồn đã khóa và checksum cho cả ba vòng, không tải corpus hay huấn luyện. Vòng 3 có 27.000 dự đoán nhiễu từng mẫu; 300/300 cận rank khớp khi replay toàn corpus một luồng; 18 unit test và 12 fixture truy vấn thật. Artifact verification và CI không phải chứng minh mọi compiled library, xác nhận novelty hoặc quyết định tạp chí.

## Tái lập hoặc dùng thuật toán

[Hướng dẫn vòng 3](round3/REPRODUCE.md) có tải dữ liệu được pin, dựng index, chạy truy vấn mới không cần nhãn và chạy lại từng giai đoạn. Cloud hai lõi/8 GiB đã hoàn tất các kết quả; local là tùy chọn cho tái lập độc lập hoặc tăng tốc, không tăng khả năng suy luận của mô hình. Không cần GPU, API trả phí hoặc gán nhãn mới.

[Quy trình CAPC/BOLT](REPRODUCE.md), [tổng quan hợp nhất cũ](docs/CAPC_BOLT_OVERVIEW.md), [hướng dẫn CAPC gốc](docs/CAPC_REPRODUCIBILITY.md), [BOLT](round2/README.md), [metadata trạng thái](PROJECT_STATUS.json). Metric các vòng không so trực tiếp vì khác nhiệm vụ và threat model.

## Dữ liệu và lịch sử

Mã, mô hình và kết quả khoa học CAPC/BOLT giữ nguyên byte. README mới thay trang tổng quan nên hash README trong manifest CAPC được cập nhật; các thay đổi tích hợp có manifest riêng. Vòng 3 có checksum và hai lần công bố khóa trước metric: [8dd7972](https://github.com/TruongTQ261531/N-Gram/commit/8dd7972dc13d85159e908f9b6ea03c394289acd2) và [5fcf816](https://github.com/TruongTQ261531/N-Gram/commit/5fcf816da7d686427f518845c71e682d95626cee).

Dùng nhãn công khai có sẵn; không có đợt gán nhãn mới. Raw corpus, truy vấn nguyên văn, index pickle, tài liệu full text và file Word không thuộc gói công bố. MIT áp dụng cho mã; điều khoản nguồn riêng tại [CAPC](results/DATA_LICENSE.md), [BOLT](round2/DATA_LICENSE.md), [vòng 3](round3/DATA_LICENSE.md). Chưa nộp hoặc tuyên bố paper được nhận.
