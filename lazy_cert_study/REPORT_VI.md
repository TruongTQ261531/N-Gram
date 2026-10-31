# Kết quả xác nhận index-first và tình trạng claim

**Đã xác nhận một cải tiến tạo chứng nhận offline; chưa xác nhận đủ novelty
cho Q1. Claim tăng tốc phiên truy vấn ngắn bị bác bỏ.** Không đổi một kết
quả tốc độ thành kết luận mới toàn cầu hoặc SOTA NLP.

## Giao thức và dữ liệu thực sự đã chạy

Nguồn WANDS chính thức, commit `3b74dcf4ba29ab8ff3e6a50b5b09fc627cb882b5`,
42.994 sản phẩm; index product_name + product_class + product_description
không cắt văn bản. 480 query IDs và nội dung chuẩn hóa không trùng nhau.
Chia theo SHA256 cố định:64 phát triển,128 xác nhận,288 dự trữ chưa tính
retrieval outcome. Không dùng nhãn relevance để chọn query hoặc fit index.

Sau development, mã/giao thức/analysis và lựa chọn screen_batch được khóa
tại [d5aa30f](https://github.com/TruongTQ261531/N-Gram/commit/d5aa30f7e7b1544d71bb3c653107e21fb7f8ba3e),
đã push trước khi chạy confirmation. Lượt xác nhận bắt đầu
30/10/2026 18:10:03 UTC, kết thúc18:16:08 UTC. Không sửa source đã khóa
trong/sau lượt này; không chọn lại metric sau khi xem kết quả.

B=2 token gốc được đổi, k=10, mọi ties ở biên đều giữ. Compact channel
chỉ có các alternative xóa/đổi chỗ/phím lân cận đã định trước; không phải
toàn bộ edit-distance ball. 128 query nguyên câu có1–10token. Ba timing
repeat, hai scenario, sáu phương pháp; rotate thứ tự, index warm chung.
89/128 query có đủ20 chuỗi request khác nhau; các lattice nhỏ hơn được
lặp vòng, nên “distinct” là tên scenario chứ không phải mọi query có20
request phân biệt. Median unique count20. Session là tổng hợp, không phải
log người dùng.

Các đối chứng: full sparse scoring+memo; incremental token-count delta
scoring+memo; full-query batched enumeration; parent compiled projection+
rank quotient; screen+parent; screen+batch. Tối ưu trích sparse feature rows,
memo và all-zero/tie closure được chia sẻ khi phù hợp. Hai primary tests
và gate được định trước ở PROTOCOL.md. Mỗi query là một mẫu; repeat không
được coi là mẫu độc lập. Đối chứng primary chọn phương pháp nhanh hơn
**cho từng query**, là một đối chứng oracle còn mạnh hơn chọn cố định.

## Correctness và tái lập

- 128/128 original-state full-query oracles hoàn tất, tổng6.684 trạng thái,
  luôn chấm điểm toàn bộ42.994 sản phẩm bằng index gốc.
- 128/128 exact union khớp hoàn toàn;0 resource_unknown trong cấu hình này.
- 4.608 method-session executions có kết quả giống nhau, không bỏ query
  khó, OOV hoặc ties. Bảy nhóm differential/edge-case tests đạt.
- Dựng lại index từ source bytes đã kiểm hash: cả26.954.436 trọng số nguyên,
  vocabulary, thứ tự document IDs và model hash khớp tuyệt đối với cache.
- Model hash:
  `3640aa299076386d0bb5c8e95b1b43979f4d1a36337fd435bfb327dc3ae5d244`.

Các kiểm tra trên không phải formal verification mọi compiled library và
không phải reproduction do nhóm bên ngoài thực hiện.

## Tốc độ và giá trị ứng dụng

Median theo query, đã lấy median timing repeat; đơn vịms:

| Phương pháp | Tạo certificate | Phiên20 request | Phiên20 có lặp |
|---|---:|---:|---:|
| Full sparse scoring + memo | — |35,59|19,18|
| Incremental delta + memo | — |34,93|16,37|
| Full-query batched enumeration |70,14|84,93|80,23|
| Parent projection + rank quotient |120,23|132,86|131,04|
| Screen + parent |33,73|47,63|41,92|
| **Screen + batch, ứng viên đã khóa** |**24,39**|38,38|30,94|

**Primary certificate:** nhanh hơn đối chứng min(parent,batch) trên107/128
query; geometric speedup **2,3474×**, paired-bootstrap95%CI
**[2,0824;2,6293]**, Holm-adjusted one-sided sign-testp=
**4,4757×10^-15**. Qua gate kỹ thuật định trước. Đây không phải tỉ số hai
median trong bảng, không phải benchmark thắng mọi thuật toán công bố.

**Primary online:** so min(memo,incremental), chỉ thắng38/128 query;
geometric speedup **0,7472×**,95%CI **[0,6949;0,8016]**, Holm p≈1.
Tức chậm hơn khoảng1,34× theo trung bình nhân. Không qua gate.
Scenario lặp chỉ thắng1/128, speedup0,4595×. Không được quảng bá tăng tốc
phiên ngắn bằng cách chỉ báo thời gian mỗi request sau khi đã bỏ startup.

Pool sơ bộ median2.613 tài liệu; exact union median45 tài liệu. Giảm kích
thước không đồng nghĩa tiết kiệm toàn phiên. Warm-index loading1,397s;
max-weight statistic0,035s, dùng chung ngoài query timer. Dựng index đầu
30,25s; dựng lại kiểm chứng39,37s là phép audit riêng. Process peak892,84MiB,
không phải peak RAM riêng của từng method. Môi trường Python3.12.14,
NumPy2.3.5, SciPy1.17.0, sklearn1.8.0; numerical threads1; quota4CPU/32GiB.
Chưa đo production concurrency, network, scope checks, fallback/rebuild.

## Relevance và dataset

Clean nDCG@10=**0,63160**, judged-top10 fraction=**76,875%**,127/128 query
có qrel dương. Dùng Exact=2/Partial=1/Irrelevant=0, gain2^grade-1,
unjudged0; tie-break document ID cố định cho metric này, trong khi oracle
pool vẫn giữ mọi ties. Các certifier dùng cùng ranker nên không có
relevance gain do phương pháp.

Source có233.448 judgment rows,231.873 pair riêng,1.467 pair lặp,14 pair
khác grade. Policy lấy maximum existing grade đã khóa trước mọi quality
metric; không thay source bytes. WANDS kế thừa nhãn người có sẵn; lượt
này0 human/LLM annotations mới. Oracle là nhãn tính toán, không xác nhận
typo giữ nghĩa. Đóng góp là audit dẫn xuất có nguồn/oracle, **chưa phải
novelty dataset đã được xác lập**.

## Điều gì thực sự mạnh hơn, điều gì còn thiếu cho Q1

Đã xử lý nút thắt materialize factors toàn corpus, thêm đối chứng batch
và incremental mạnh, mở domain sản phẩm, xác nhận prospective, định lượng
chính xác cả kết quả âm, và dựng lại index. Có thể dùng làm bằng chứng phụ
cho ứng dụng audit offline trong bài shared-query certification.

Tuy nhiên feature envelopes/anchor bounds, sparse extraction và batching
có nguyên lý đã biết. Tốc độ2,35× chưa tự chứng minh khác biệt thuật toán
đủ lớn. Luận đề trung tâm ở round3 vẫn có bằng chứng tích cực2/3 corpus
so LP+enum, nhưng overlap CostCert/UTK/discrete verification chưa giải
quyết. CLOSEST_METHODS.md cho reduction rõ sang uncertain linear top-k
và giới hạn của convex-hull replacement; không giả định UTK không chuyển
được sang miền này. Chưa chạy RSA/JAA gốc hoặc thiết lập non-equivalence
với toàn thuật toán CostCert.

Ưu tiên tiếp theo là một mở rộng **cận số đối thủ đồng thời** của bài toán
trung tâm, thay vì thêm caching: thử higher-order valid cuts/nhóm đối thủ
chỉ sau khi đối chiếu với disjunctive/cover-cut verification và baseline
genericMILP cùng tài nguyên. Đây là giả thuyết nghiên cứu, **chưa triển khai,
chưa có kết quả và chưa được coi mới**. Chọn cơ chế trên development rồi
khóa trước phần dự trữ; không dùng lại128 confirmation để cứu claim.
Song song cần closest-method full-text review, lỗi tự nhiên có nguồn và
proof/code review độc lập. Các truy cập scholarly/GitHubAPI mới trong lượt
này vẫn HTTP403; bản mạng dự thảo lưu sẵn chưa được Publish. Không có căn
cứ xác nhận quartile hiện hành hay bảo đảm nhận Q1.

Xem CLAIM_DEFENSE_VI.md để biết câu claim nên dùng và điều kiện bác bỏ.
LaTeX/BibTeX/figures không nằm trong branch này; bản thảo giữ cục bộ theo
yêu cầu. Không vẽ Fig1/Fig2. Không thay dữ liệu, source hoặc báo cáo cũ.
