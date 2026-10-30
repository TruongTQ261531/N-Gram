# Mở rộng ứng dụng và dữ liệu audit — 30/10/2026

Đã triển khai một phòng thực nghiệm web chạy truy hồi/chứng nhận cục bộ trong trình duyệt và bộ audit có nhãn thứ hạng tính được chính xác. Đây là **ứng viên đóng góp ứng dụng/dữ liệu**, chưa xác lập novelty toàn cầu hoặc mức đóng góp đủ Q1. Không thay đổi kết quả khoa học của CAPC, BOLT và vòng3.

**Ứng dụng đang chạy:** https://ngram-research-lab-tq261531.tealrook33.chatgpt.site — quyền truy cập ban đầu chỉ chủ sở hữu.

## Phần ứng dụng đã thực hiện

- Nhập corpus JSON, JSONL hoặc CSV; tìm kiếm EN/VI trên dữ liệu được chọn. Giới hạn live web500 tài liệu,500.000 ký tự,16 token, không cắt truy vấn ngầm.
- Chọn bộ lỗi gõ phím, từ điển, mất dấu hoặc hợp các lựa chọn; ngân sách tối đa2 vị trí token gốc bị đổi.
- Trả cận rank, độ sâu đủ có thể chứng nhận trong cap, witness có thể chạy lại và tài liệu tham chiếu. U>cap khi chưa có witness vi phạm chỉ là chưa kết luận.
- Xuất gói chứng nhận hoặc batch JSONL tự chứa corpus, trọng số, hash, phép sửa, cận/nhóm xung đột và các trạng thái oracle đã liệt kê.
- Xem riêng kết quả float64 của vòng3; không gán các tỷ lệ nghiên cứu cũ cho scorer triển khai mới.
- Không có API nhận corpus/query, không thu thập log truy vấn làm dataset ngầm. Dữ liệu người dùng đưa vào chỉ được xử lý trong trình duyệt; gói họ tải xuống cần kiểm tra trước khi họ chia sẻ.

Scorer web `ngramlab-fixedpoint-v1` làm tròn hệ số BM25 sang trọng số nguyên theo thang10^6. Chứng nhận áp dụng cho những trọng số đã tạo, không phải chứng minh tương đương scorer float64 cũ. Guard giới hạn mọi tổng điểm trong miền số nguyên an toàn; witness, margin, support và DP dùng phép cộng/trừ nguyên. Không có tuyên bố chứng minh compiled browser hoặc tính chính xác tuyệt đối của bước log/làm tròn ban đầu.

## Đóng góp dữ liệu cụ thể

Bản v0.1 gồm48 tài liệu mẫu do project biên soạn,48 query seed,12 nhóm chủ đề, hai ngôn ngữ EN/VI. Tài liệu là tổng hợp, không phải sổ tay công ty thật. Nguồn query, ngôn ngữ, phép sửa, scorer, corpus/model hash và toàn bộ oracle được lưu thay vì chỉ phát hành một điểm số tổng hợp.

codespell revision `4ce1caed2f97a50031225545c9697d9ef885c09b` cung cấp subset250 từ đích/1.276 cặp lỗi. Lọc correction đơn từ, đảo chiều, sort và tối đa8 lỗi/từ; không có diễn giải tần suất. Ghép lỗi từ điển vào query là bán tổng hợp, không phải truy vấn lỗi quan sát từ người dùng thật. Dictionary/data dẫn xuất giữ ghi công CC BY-SA3.0; corpus tự viết CC0. Không sao chép code GPL của codespell.

Có3 channel cho mỗi query ×2 budget =288 trường hợp. Language counterpart, sibling query, channel và budget của một family cùng split. Hash family định trước cho240 development/48 evaluation; chỉ2/12 family thuộc evaluation. Không huấn luyện mô hình trên nhãn oracle; split này không phải bằng chứng tổng quát hóa sang ngôn ngữ/corpus mới. Hai identity lattice vẫn được giữ và đánh dấu.

Nguồn/cấu hình/đầu vào và verifier đã được công bố trước kết quả tại [8055553](https://github.com/TruongTQ261531/N-Gram/commit/8055553afd53d4477988910b1454c8640d075946). Freeze10 file không bị đổi sau metric. Giao thức và kết quả vòng3 giữ nguyên.

## Kiểm tra đầy đủ trong phạm vi bộ hữu hạn này

| Hạng mục | Kết quả thực chạy |
|---|---:|
| Case có oracle liệt kê đủ | 288/288 |
| Trạng thái query đã kiểm tra độc lập | 334.815 |
| Điểm token–tài liệu tính lại độc lập | 998.688 |
| Cạnh xung đột được kiểm chứng độc lập | 23 |
| Case có vi phạm cận chứng nhận | 0 |
| Case cover chặt hơn pairwise | 17/288 |
| Trong split evaluation | 2/48 |
| Case dùng được enumeration trong cap web | 275/288 |

Python tự tính gram và điểm từ trọng số đã lưu, dùng integer độ chính xác tùy ý; liệt kê trạng thái bằng combinations/products theo một thứ tự khác JavaScript; kiểm tra mọi rank, worst-rank witness, cạnh xung đột và phân hoạch. Không dùng thư viện ML, nhãn do người hoặc LLM chấm. Đây là ground truth cho hành vi scorer/lattice, không phải nhãn liên quan hay đúng nghĩa.

## Lợi ích có đo được và giới hạn quan trọng

| Phạm vi | n | Mean depth pairwise | Mean depth cover/deployed | Gold mean depth |
|---|---:|---:|---:|---:|
| Toàn bộ | 288 | 1,8368 | 1,7778 | 1,7778 |
| Evaluation | 48 | 1,1458 | 1,1042 | 1,1042 |

Mỗi case cải thiện chỉ giảm một tài liệu ở cận độ sâu. Trên bộ nhỏ này cover khớp oracle ở cả288 case, pairwise đã khớp271. Điều này cho thấy bộ v0.1 khá dễ; không chứng minh ưu thế ở corpus lớn hoặc phân phối người dùng thật.

**Ở các cap đã khóa1/5/10/20, số case được chấp nhận không tăng so với pairwise:** tương ứng204/282/285/286 trên288. Không chọn thêm ngưỡng hậu kiểm để thay kết luận. Do đó không khẳng định đã giảm abstention hoặc tăng chất lượng RAG trong triển khai. Thời gian concurrent chỉ là diagnostic; chưa có user study, relevance evaluation hoặc đo productivity/latency sản xuất.

Depth=U là mức đủ được cận hiện tại cho phép, không phải mức đủ nhỏ nhất nếu thiếu oracle chính xác. Cận giữ tài liệu tham chiếu khi rerank mỗi biến thể, không bảo đảm mọi tài liệu top‑K gốc hay mọi bằng chứng liên quan đều được giữ.

## Kiểm thử phần mềm

4 nhóm test Node đã qua, gồm128 tổ hợp corpus/budget so với liệt kê độc lập bằng cách encode lại toàn query; kiểm tra factorization, Unicode, ties/OOV và cap không được tạo chứng nhận sai. Kiểm thử trình duyệt Chromium thật đã chạy corpus import CSV/JSON/JSONL, query EN/VI, witness ties, tải certificate, tạo/export batch, điều hướng và mobile. Payload HTML trong corpus hiển thị như văn bản, không chạy script; không có request mang corpus/query lên server. Đã kiểm tra preview desktop/mobile và không có uncaught JavaScript exception trong những luồng này. Xem `browser-qa.json` và log.

Gói xuất của corpus người dùng ghi `user-provided`, license chưa được người tải quy định; ứng dụng không tự cấp CC0/CC BY-SA cho nội dung đó. Bundle kiểm tra hash model/corpus khớp bản kết quả trước khi xuất.

## Novelty ứng dụng/dataset đến đâu

Adaptive K/compact sets, counterfactual ranking demo, robust text transformations, typo dictionaries và JSON export đều có prior art. [RELATED_WORK.md](RELATED_WORK.md) đối chiếu FEVER conformal IR, DiBud, CAS, QE-RAG, CREDENCE, TextFlint và các nguồn dữ liệu. Phần có thể phát triển là dịch vụ chứng nhận finite-lattice có mô hình và giới hạn kiểm tra được, cùng dữ liệu chứa oracle/trace đủ để xác minh cơ chế.

**Web chạy được và bộ288 case chưa khiến đề tài tự đạt Q1.** Mức đóng góp thực tế hiện nhỏ và dữ liệu còn tổng hợp/dễ. Để nâng thành claim ứng dụng mạnh, cần một tác vụ truy hồi thật có dữ liệu được phép dùng, đánh giá giữ bằng chứng/liên quan và chi phí trên biến thể có nguồn thực tế, đối chứng theo cùng ngân sách, cùng phản biện novelty độc lập. Có thể tận dụng nhãn công khai có sẵn và quan sát lỗi có giấy phép; không bắt buộc mở một đợt gán nhãn lớn mới.

## Tái lập

```bash
node webapp/test-engine.mjs
python application_study/check_archive.py
```

Check archive xác minh source freeze, SHA256, đủ288 ID/trace, summary và chạy lại toàn bộ oracle vào thư mục tạm. Không sửa evidence công bố. Node24/Python3.12 đã dùng; `verify_oracle.py` không cần numpy. Xem README và DATA_LICENSE. Website được triển khai qua Sites; quyền truy cập ban đầu chỉ chủ sở hữu, không tự mở public.
