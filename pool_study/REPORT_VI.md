# Mở rộng ứng dụng và audit dataset: kết quả ngày30/10/2026

Project đã có một chức năng ứng dụng bổ sung được kiểm thử: **tạo tập tài liệu dự phòng bao phủ mọi kết quả top-k dưới bộ lỗi hữu hạn, rồi dùng lại tập đó cho truy vấn sửa lỗi**. Bộ audit cũng được mở rộng sang văn bản từ hai corpus công khai chưa dùng ở các vòng trước, với nhãn tập kết quả do oracle tính chính xác, không cần gán nhãn thủ công. Đây là bằng chứng về chức năng, tính đúng trong phạm vi đã khai báo và một artifact tái lập. **Chưa đủ căn cứ khẳng định novelty toàn cầu hoặc đủ đóng góp cho paper Q1.**

## Thay đổi so với phiên trước

Trước đây, chứng nhận trả lời “tài liệu tham chiếu ban đầu có còn nằm trong top-K khi truy vấn bị sửa hay không”. Điều đó chưa bảo đảm danh sách lấy sẵn chứa tất cả tài liệu có thể xuất hiện trong top-K mới. Chức năng mới xét chính hợp các tập kết quả có thể xuất hiện; một pool an toàn cho phép truy hồi lại trong pool với cùng trọng số mà vẫn giữ đủ kết quả của scorer toàn corpus. Không phải mô hình tăng chất lượng liên quan hay chứng minh câu trả lời RAG đúng.

Mã Python nghiên cứu và mã web có định danh scorer riêng. Bản web giữ giới hạn500 tài liệu và kênh lỗi hiện có; thí nghiệm lớn dưới đây chạy Python trên toàn corpus và dùng một kênh lỗi compact để oracle duyệt hết. Không gán số liệu offline cho tốc độ hoặc quy mô vận hành của bản web.

## Giao thức đã công bố trước kết quả

[Snapshot596435b](https://github.com/TruongTQ261531/N-Gram/commit/596435bef3ab039b8abfbf672399c761e0c6e7ae) khóa10 file mã/giao thức/nguồn/ID trước khi chạy retrieval trên hai corpus. Dùng64 truy vấn mỗi corpus, chọn theo hash ID không dựa điểm số. Giữ nguyên mọi truy vấn và cấu hình, không loại case khó hoặc kết quả âm. Các analyzer/tài liệu viết sau được ghi rõ; không gọi chúng là mã phân tích khóa trước.

- ArguAna:8.674 tài liệu,64 truy vấn; SciDocs:25.657 tài liệu,64 truy vấn.
- Cắt về16 token đầu theo giao thức:64/64 truy vấn ArguAna và3/64 SciDocs bị cắt. Vì vậy đây chưa phải đánh giá toàn bộ nội dung truy vấn dài hay chất lượng BEIR.
- Character ngram3/4/5, BM25 cố định, hệ số làm tròn thành số nguyên. Kênh compact gồm tối đa một biến thể được chọn bằng hash cho mỗi loại xóa/đảo/thay phím kề ở từng token. Không dùng đầy đủ mọi lỗi gõ và không mô tả tần suất lỗi tự nhiên.
- Ngân sách1/2 token, k5/10:512 cấu hình phụ thuộc từ128 truy vấn gốc. Không coi512 cấu hình là512 mẫu độc lập.
- Không tải qrels và không tạo nhãn liên quan bằng người/LLM. Nhãn oracle chỉ mô tả kết quả của scorer dưới đúng phép sửa đã định.

## Kết quả chính

Số tài liệu trung bình trong pool tại **B=2, k=10**, giữ mọi tài liệu bằng điểm tại ngưỡng:

| Corpus | Cận độc lập | Cận dùng chung truy vấn | Chia2 token đầu | Chia2 token theo độ biến thiên | Hợp chính xác |
|---|---:|---:|---:|---:|---:|
| ArguAna |285,91|139,16|108,69|72,97|27,77|
| SciDocs |632,73|305,75|212,41|135,08|37,16|

So với đối chứng cận dùng chung truy vấn, phương án chia thích nghi giảm số tài liệu trung bình **47,56% trên ArguAna và55,82% trên SciDocs**. Có cải thiện ở42/64 và58/64 truy vấn tương ứng. Đây là giảm kích thước một tập bảo thủ, không phải tăng recall, độ chính xác ngữ nghĩa hay điểm nDCG.

Đối chứng chia cùng số token/ngân sách cũng hữu ích: phương án thích nghi tốt hơn cách chọn2 vị trí đầu trên39/64 ArguAna và45/64 SciDocs, nhưng **tệ hơn trên1/64 và8/64**. Giữ nguyên các trường hợp này trong báo cáo từng truy vấn. Pool thích nghi vẫn lớn hơn hợp chính xác; không gọi nó là pool nhỏ nhất. Các cấu hình khác cùng kết quả từng truy vấn có trong [summary.csv](results/summary.csv), [per-query.csv](results/per-query.csv) và [analysis.json](results/analysis.json).

## Lợi ích thời gian và kết quả âm

Ở B=2,k=10, trung vị thời gian khởi tạo pool khoảng62,30ms trên ArguAna và105,64ms trên SciDocs. Trung vị truy hồi mỗi lần trong microbenchmark sparse lần lượt là1,78/3,29ms cho toàn corpus và0,25/0,22ms cho pool. Các số này là phép đo tại máy cloud, không phải latency web thực tế.

**Trung vị điểm hòa vốn dự phóng là45 lần sửa trên ArguAna và35 trên SciDocs. Không có truy vấn nào ở cấu hình này dự phóng hòa vốn trong chuỗi20 lần sửa đã đo.** Không được bỏ chi phí ban đầu để tuyên bố đã tăng tốc toàn phiên sử dụng. Ở B=1,k=10, có10/64 ArguAna và39/64 SciDocs có dự phóng hòa vốn trong20 lần; đó vẫn là dự phóng từ các thành phần đo riêng, chưa phải phiên người dùng quan sát được.

Mỗi pipeline được chạy3 lần để đo thời gian; full/cached dùng thứ tự cân bằng. Chúng là lặp đo cho thuật toán tất định, không phải ba lần xác nhận độc lập. Môi trường2CPU/8GiB,1 thread số học; hai lượt benchmark lớn chạy tuần tự. Browser QA nhỏ có chạy ngắn trong giai đoạn đo nên timing chưa cách ly hoàn toàn. Không tuyên bố hơn hệ thống retrieval production hoặc RSA/JAA gốc chưa được triển khai. Xem [EXECUTION_NOTES.md](EXECUTION_NOTES.md).

## Xác minh minh bạch

Oracle gồm98.023 cấu hình biến thể token tại B=2, tính theo truy vấn gốc; nếu tính riêng các bài toán B=1 và B=2, có103.013 lượt kiểm tra trạng thái–ngân sách. Không cộng thêm k5/k10 thành các truy vấn độc lập. Oracle lưu đầy đủ tập top-k từng trạng thái và mọi tie.

Bộ kiểm tra độc lập dùng cách duyệt trạng thái khác và sort toàn bộ điểm thay cho cách partition của oracle. Đã đối chiếu512 cấu hình,1.548.211 quan hệ thành viên top-k và11.686 nhánh điều kiện; **không thiếu tài liệu oracle nào và tập kết quả cache/full khớp trong mọi trạng thái đã lưu**. Các factor số nguyên, trace, ID cột, nguồn pin/hash và báo cáo kiểm tra đều công bố trong results. Một bước khác đối chiếu97.964.788 điểm token–tài liệu từ index corpus nguồn bằng bộ trích gram riêng và cộng Python integer; báo cáo nguồn nằm ở results/*/source-replay.json. Không coi kiểm tra này là chứng minh formal toàn bộ machine code hoặc công thức log được làm tròn.

Web có kiểm thử600 tổ hợp factor/ngân sách/k ngẫu nhiên, xử lý tie/OOV, fallback khi hết tài nguyên, query có token bị xóa rỗng, và đối chiếu cache với truy hồi toàn corpus. Chromium thực tế kiểm tra replay hợp lệ, từ chối ngoài lattice, hủy hiệu lực khi đổi cấu hình, từ chối model hash cũ/corpus mới, xuất chứng nhận và giao diện mobile. Các kiểm thử browser cũ về nhập file, xuất dữ liệu và nội dung HTML không thực thi vẫn đạt.

## Dataset đóng góp gì và còn thiếu gì

Artifact mới cung cấp truy vấn kế thừa, phép sửa, matrix điểm nguyên cho mọi token–form–document, oracle set-valued đầy đủ, pool của mọi đối chứng, trace chia miền và các trường hợp heuristic kém hơn đối chứng. Dữ liệu có thể dùng kiểm tra độ chặt cận hoặc tìm phản ví dụ mà không phải gán nhãn mới. Giữ nguồn/giấy phép CC BY-SA4.0; không nhận ArguAna/SciDocs là dữ liệu tự thu thập.

Quy mô và văn bản đã đa dạng hơn bộ48 tài liệu tổng hợp cũ, nhưng vẫn là **bộ audit dẫn xuất với lỗi tổng hợp**, chỉ hai corpus tiếng Anh và truy vấn bị giới hạn độ dài. Chưa có bằng chứng nó đại diện hành vi lỗi tự nhiên, là dataset đầu tiên của loại này, hay đủ đóng góp cho một bài dataset Q1. Không có dữ liệu của người dùng web được thu gom.

## Novelty và quyết định nghiên cứu

[Rà soát nguồn gần nhất](RELATED_WORK.md) cho thấy UTK2018 đã có possible-top-k union, regional dominance và chia miền; TASTIER đã có fuzzy interactive caching. Vì vậy không gọi việc ghép các thành phần này thành thuật toán mới chưa từng có. Điểm đã bổ sung là bài toán ứng dụng sát hơn, triển khai có điều kiện dùng lại rõ ràng và bằng chứng oracle tái lập trên văn bản mới.

**Chưa đạt điều kiện để tuyên bố hoàn thành mục tiêu Q1.** Nút thắt còn lại là khác biệt phương pháp đủ rõ so với UTK và các phương pháp chứng nhận gần, cùng lợi ích toàn phiên khi chỉ có ít lần sửa. Hướng đáng thử tiếp là khai thác trạng thái token có cùng hiệu ứng điểm để nén lattice và tìm hợp chính xác với chứng nhận chi phí thấp hơn; đó mới là giả thuyết chưa triển khai/kiểm chứng novelty trong đợt này. Không đổi tên phương pháp cũ hoặc tăng số benchmark để coi như đã giải quyết nút thắt.

Bạn chưa cần chạy local để hoàn tất các phép đo trên. Cloud hiện tại đủ chạy toàn bộ. Local giúp tái lập độc lập hoặc tăng quy mô/tốc độ thí nghiệm khi có thêm CPU/RAM; nó không tự tăng khả năng suy luận của phiên chat hoặc bảo đảm novelty. Web dùng để thử corpus nhỏ, replay và tải chứng nhận; Python dùng cho thí nghiệm lớn và xác minh nguồn. Không cần GPU cho phạm vi hiện tại.
