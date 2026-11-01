# Hoàn thiện đối chứng UTK trên miền NLP hữu hạn

Chốt ngày 02/11/2026 (Asia/Saigon); protocol và hai source freeze được khóa
ngày 01/11/2026. Đây là bổ sung đối chứng hồi cứu, không phát triển novelty,
scorer, corpus, mô hình neural hay kênh lỗi mới. Các số liệu và kiểm định gốc
không bị thay thế.

## Đã khắc phục khoảng trống nào?

Đã thực thi hai bản chuyển thể RSA-FD/JAA-FD trên **toàn bộ 128 truy vấn WANDS,
42.994 sản phẩm và miền gồm đủ 6.684 trạng thái hợp lệ**, với cùng scorer
nguyên, full query, compact channel, B=2/k=10 và tất cả đồng điểm ranh giới.
Không dùng một đoạn nối hai truy vấn thay cho toàn miền nữa.

Đây là mã Python/NumPy viết độc lập theo cơ chế dominance/arrangement trong
Mouratidis và Tang, PVLDB 2018, DOI **10.14778/3204028.3204031**. Chúng được
ghi rõ là bản chuyển thể cho miền hữu hạn, **không phải đo lại nguyên bản C++**.
State cells thay convex cells/LP feasibility; pivot scan thay R-tree; dominance
nghiêm ngặt và equality cells giữ đúng toàn bộ tie. Một thay đổi miền đầu vào
không tự chứng minh thuật toán mới; bảng ánh xạ từng thành phần trong
METHOD_MAPPING.md nêu cả các tối ưu không tái hiện.

## Đợt chính: ba lượt cho mọi truy vấn

Mọi pipeline tự chịu chi phí dựng lattice, screen, materialize và refinement;
chỉ dùng chung immutable warm index. Phương pháp được xoay thứ tự theo hash,
chạy tuần tự, một numerical thread. Các cost bên dưới là median/p95 của
128 median theo truy vấn; giữ cả thời gian tiêu vào unknown.

| Control | Exact cả ba lượt | Median ms | P95 ms | Lượt unknown |
|---|---:|---:|---:|---:|
| Screen + batch | 128/128 | 16.74 | 53.57 | 0 / 384 |
| Parent projection/quotient | 128/128 | 72.87 | 102.14 | 0 / 384 |
| Screen + RSA-FD | 126/128 | 191.22 | 6718.95 | 6 / 384 |
| Screen + JAA-FD | 127/128 | 173.25 | 6026.41 | 3 / 384 |

Cả hai control cũ hoàn tất 384/384 lượt. RSA-FD có 378 exact, 6 unknown;
JAA-FD có 381 exact, 3 unknown. **Mọi lượt được đánh dấu exact đều khớp oracle
toàn corpus**; unknown được kiểm tra containment an toàn và không tính exact.
Không có lỗi thực thi hoặc mismatch của một kết quả được đánh dấu exact.

Truy vấn 170 chạm soft wall guard 120 giây ở cả hai adapter, cả ba lượt.
Ở truy vấn 308, RSA-FD chạm cap một triệu arrangement nodes trước 120 giây,
còn JAA-FD hoàn tất. Vì số nút không cùng đơn vị công việc giữa hai thuật toán,
không lấy riêng tình huống này để kết luận về ưu thế dưới cùng wall budget.

## Kiểm tra bổ sung: bỏ cap số nút

Một profile riêng được khóa trước khi chạy, dùng lại **toàn bộ 128 ID và bốn
control**, bỏ cap số nút cho cả RSA-FD/JAA-FD nhưng giữ wall guard 120 giây
và cap 50 triệu state-score cells. Chạy một first pass cho mỗi method/query;
không trộn với median ba lượt hoặc sửa kết quả ban đầu.

| Control | Exact | Median ms | P95 ms | ID còn unknown |
|---|---:|---:|---:|---|
| Screen + batch | 128/128 | 15.94 | 46.60 | Không |
| Parent projection/quotient | 128/128 | 71.40 | 102.04 | Không |
| Screen + RSA-FD | 127/128 | 208.10 | 6536.34 | 170 |
| Screen + JAA-FD | 127/128 | 167.59 | 5870.13 | 170 |

RSA-FD hoàn tất truy vấn 308 trong 76,89 giây; JAA-FD trong 66,61 giây ở
profile này. Cả hai đạt **127/128 exact**, chỉ còn truy vấn 170 hết wall budget.
Như vậy trường hợp 308 đã được kiểm tra với ngân sách rộng hơn, không bị
bỏ lại như một bất lợi do cap tùy chọn. Mọi kết quả exact ở profile cũng
khớp kiểm chứng toàn corpus. Các trường hợp unknown vẫn nằm trong mẫu số.

## Kiểm chứng độc lập đã làm gì?

Sau khi đo, scorer sparse chấm lại **full text của mọi trạng thái trên toàn
42.994 sản phẩm**, không dùng projected pool hay công thức support để lấy
kết quả chuẩn. Kiểm tra toàn bộ union, witness của RSA và state cells của JAA.
Tất cả 128 union chuẩn mới cũng khớp oracle cũ; không đổi ground truth.

Một lượt kiểm tra nguồn tiếp theo xác nhận **8.298.930 giá trị minimum margin**
cho các phép loại bằng strict dominance, trực tiếp trên điểm toàn corpus của
mọi trạng thái; đồng thời kiểm tra anchor minima và upper envelope của các
phần tử bị loại bởi screen. Hai adapter có chung filter được so receipt
đồng nhất rồi kiểm tra giá trị một lần, không đếm lặp thành hai kết quả độc lập.
Các coefficient/proof giống nhau ở profile bổ sung được nối bằng hash với
receipt đã kiểm chứng; witness/cell đầu ra của profile vẫn được kiểm riêng.

## Cách đọc kết luận

Khoảng trống “chưa có thực nghiệm matched full finite-domain UTK” đã được bổ
sung. Phương pháp finite UTK có thể giải đúng cùng bài toán; khác biệt miền
không được dùng thay cho bằng chứng novelty. Chi phí quan sát áp dụng cho
các bản chuyển thể được mô tả, gồm dựng receipt, không phải mọi bản UTK tối
ưu hay nguyên bản C++. Không gọi timeout là thuật toán sai.

Tỷ lệ 2,35 lần của lượt WANDS gốc giữ đúng hai control và protocol gốc.
Không trộn timing mới vào kiểm định cũ. Ratio trong analysis.json chỉ dùng
các cặp hoàn tất đúng cùng mục tiêu và ghi rõ mẫu số 126/127; không suy ra
ratio toàn 128 từ mẫu hoàn tất. Bảng chính ở trên vẫn giữ đủ mọi truy vấn.
Failed session gate, khác biệt backend và giới hạn neural vẫn giữ trong bài.

Đây là hoàn thiện bằng chứng để chuẩn bị phản biện, không phải cơ chế tự
chứng minh bài chắc chắn được nhận Q1. Không mở rộng thêm novelty trong đợt này.

## Mã, dữ liệu và bản thảo

- Protocol, hai freeze, code, toàn bộ runtime, trạng thái cap và oracle đều có
  trong thư mục này. Execution gzip được chia lossless thành 10 phần 8 MiB,
  giữ hash từng phần và hash toàn file; không đổi số đo nào.
- Archive checker dùng trực tiếp các phần, không cần file gzip riêng trên máy
  tác giả. Raw text, index, nguồn/binary C++ và PDF bên thứ ba không lên Git.
- main.tex/references.bib được cập nhật riêng ngoài repository; Fig1/Fig2 chưa vẽ.
- 48 unit tests, các archive/checksum cũ và kiểm tra toàn bộ hồ sơ mới đều đạt.
