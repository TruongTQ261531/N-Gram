# Lượt nghiên cứu riêng: exact pool, nguyên truy vấn và chi phí toàn phiên

Ngày30/10/2026, Asia/Bangkok. Branch `research/rank-equivalence-2026-10-30`, nền main94a9f0c16ab2bd312621682cb842fb9b439deabe. **Đã hoàn tất triển khai và thực nghiệm; chưa xác lập novelty đủ Q1. Main và live Site không thay đổi.** Tổng kiểm kê từ đầu project ở [PROJECT_REVIEW_2026-10-30.md](../PROJECT_REVIEW_2026-10-30.md).

## 1. Kết luận và phần đã cải thiện

Đã khắc phục một số thiếu hụt cụ thể: xử lý nguyên truy vấn dài thay vì16token đầu; giữ nguyên cận cũ với cách tính lại ít hơn; tính hợp top10 chính xác sau sàng lọc có chứng nhận; gộp phép sửa/vị trí có cùng hiệu ứng thứ hạng với budget và multiplicity được kiểm tra; đo cả chi phí khởi tạo và đối chứng memoization thông thường. Không tạo nhãn người/LLM mới.

**Kết quả tích cực:**32/32query mới có exact union được kiểm tra độc lập; pool nhỏ hơn hoặc bằng cận cũ; compiler giúp rõ trên ArguAna; computational audit có đủ source/factor/proof/witness để tái lập. **Kết quả âm quyết định:** phương án exact nhanh nhất vẫn không thắng ordinary query memoization ở bất kỳ query nào trong mỗi điều kiện5/20request, distinct/repeated đã đo. Vì vậy **NO-GO cho claim tăng tốc truy hồi online ngắn và chưa nên gộp vào main như một cải tiến hiệu năng**. Đây vẫn là ứng viên cho công cụ kiểm toán/verification offline, chưa là một phương pháp mới đã đủ Q1.

## 2. Thiết kế và lịch công bố

- [7062944](https://github.com/TruongTQ261531/N-Gram/commit/70629444f90c1841f1562aba4e1a2121f59455a8) khóa14file mã/giao thức/ID/nguồn trước kết quả mới. [freeze.json](freeze.json) và [PROTOCOL.md](PROTOCOL.md) giữ nguyên byte.
-16query ArguAna và16query SciDocs mới theo hashID; loại ID và full-query string đã dùng, thêm loại topicfamily ArguAna đã dùng. Cùng corpus/index đã nghiên cứu trước; đây không phải xác nhận trên domain/corpus mới. Không suy diễn topic-independence ở SciDocs khi thiếu metadata tương ứng.
-Toàn corpus8674/25657tài liệu, nguyên query83–351token ở ArguAna và4–16token ở SciDocs;32/32không bị cắt. Scorer integer, compact hash-chosen deletion/swap/QWERTY alternatives, B2,k10,ties được giữ. Không phải mọi lỗi bàn phím hay typo tự nhiên.
-Ba lượt timing có thứ tự cân bằng; không chạy đồng thời các benchmark. Index corpus chung đã warm được loại khỏi chi phí cho mọi phương pháp; factor/certificate/subset-index và request đều nằm trong actual session timer.
-Khi thấy source primary có thể chọn request lặp sau early saturation, đã giữ kết quả gốc và thêm [2a05551](https://github.com/TruongTQ261531/N-Gram/commit/2a05551) trước timing supplemental:20query khác nhau, raw+5single+14doubleedits; thêm10query lặp2lần; ordinary memoization control; đo prefix5 và20. Đây là audit ghép cặp trên cùng32query, không phải tập xác nhận độc lập thứ hai. Xem [SESSION_ADDENDUM.md](SESSION_ADDENDUM.md).
-Sau khi primary đã chạy và trong giai đoạn session audit, static code inspection thấy tính lại dạng từ giống nhau. [afdc60a](https://github.com/TruongTQ261531/N-Gram/commit/afdc60ac6a039e6211dd1e8d2697a992a54e793a) khóa tối ưu unique-form scoring trước timing của nó. Đây là audit tối ưu kỹ thuật trên cùng dữ liệu; xem [FACTOR_ADDENDUM.md](FACTOR_ADDENDUM.md). Không chỉnh lại các giao thức trước hoặc chọn bỏ case bất lợi.

## 3. Thuật toán đã thực hiện

**Compiled bounds:** tính một lần các gain/loss lớn nhất theo budget và tokenID, rồi tái sử dụng tại mọi nhánh. Hai token bị fix chỉ cần loại ID tương ứng khỏi top4. Kết quả pool phải giống hoàn toàn scalar implementation cũ; đã kiểm tra32/32.

**Exact projected union:** trước tiên chứng minh toàn corpus rằng mọi top10 có thể xuất hiện nằm trong P. Sau đó chỉ tính trên P với trọng số gốc. Mọi phương pháp exact đều có standard witness-saturation closure: nếu đã thấy đủ mọi thành viên P thì U=P, không cần duyệt hết. Phải ghi theoretical/visited/complete/termination riêng.

**Các quotient/control:** enumerate vị trí gốc; gộp exact-score effects trong mỗi vị trí; gộp repeated-text token types với multiplicity; ứng viên gộp delta modulo một constant chung cho tất cả tài liệu trong P rồi gộp các vị trí có cùng effect set. Raw-equivalent class dùng minimum cost0; các class khác cost1; hai edits trong một group phải có hai vị trí gốc thực sự. Mỗi union member có witness hợp lệ. [THEORY.md](THEORY.md) giải thích hai chiều coverage và giới hạn.

**Unique-form scoring:** sinh/score mỗi dạng từ khác nhau một lần và ánh xạ về đủ mọi vị trí token. Đây là caching/vectorization thông thường, không thay scorer/budget/IDF và không được gọi riêng là novelty. Tất cả factor trả về được so với scalar archive trên mọi document.

## 4. Exactness và kích thước pool

Các so sánh dưới dùng CÙNG query mới, nguyên câu và lattice, không so mean của cohort này trực tiếp với cohort128query/16token của lượt trước.

| Corpus | Query mới | Pool cũ trung bình | Hợp chính xác trung bình | Giảm mean pool |
|---|---:|---:|---:|---:|
| ArguAna |16|16,4375|13,9375|15,21%|
| SciDocs |16|145,0625|39,6250|72,68%|

Quotient combinations lý thuyết trước khi đóng bằng witness:

| Corpus | Vị trí gốc | Exact-score classes | Repeated-text control | Rank-effect candidate |
|---|---:|---:|---:|---:|
| ArguAna |3272741|2900764|1318112|1208008|
| SciDocs |7583|7274|7259|6994|

Phần lớn giảm ở ArguAna đến từ repeated-token symmetry đã biết. Candidate giảm thêm khoảng8,35%so với text grouping ở ArguAna và3,65%ở SciDocs; không quy toàn bộ giảm cho common-shift quotient. Số visited quotient thực tế719845/6994; closure áp dụng cho mọi exact control. Chỉ có một primary Argquery dùng một visited descriptor cho chuỗi request, là lý do thêm workload audit độc lập với visitation.

Full-corpus brute-force oracle đạt cap100millioncells ở cả16Argquery nên giữ `resource_unknown`;16Sciquery có exact full-corpus comparator. Không coi cap là baseline sai/thua. Tính đúng toàn corpus ở Arg được kiểm tra qua full-corpus exclusion proof, original-state exhaustive oracle TRÊN P và full-corpus witnesses; không gọi đó là đã brute-force mọi điểm tài liệu ở mọi rawstate.

## 5. Hiệu suất thành phần, có cả các trường hợp không có lợi

Median speedup theo từng query của compiled bound so với legacy là3,61×ở ArguAna, nhưng0,978×ở SciDocs: **không có lợi thế nhất quán ở corpus thứ hai**. Ratio của hai median tổng thể có thể khác median của paired ratios; report/CSV giữ cả hai giá trị để không chọn cách tóm tắt có lợi.

Median factor construction ArguAna215,21ms→140,39ms; paired median speedup1,49×. SciDocs31,96ms→31,67ms, paired1,004×gần như không đổi. Kết quả này hỗ trợ tối ưu lặp lại từ ở câu dài, chưa phải một cơ chế cải thiện tổng quát.

## 6. Actual session5/20request: kết quả âm cần giữ

Millisec, median giữa các query sau khi lấy median3repeat mỗi query. Bảng sử dụng audit cuối có factor optimization. Bao gồm initialization; mỗi cột nhận cùng sequence và trả đúng cùng tập kết quả.

| Corpus / workload | Request | Full sparse | Ordinary memo | Fast exact pool |
|---|---:|---:|---:|---:|
| ArguAna / khác nhau |5|46,66|45,49|407,82|
| ArguAna / khác nhau |20|180,94|182,40|432,78|
| ArguAna /10query lặp2 |20|186,97|95,54|515,20|
| SciDocs / khác nhau |5|20,64|20,30|135,19|
| SciDocs / khác nhau |20|75,61|79,35|140,23|
| SciDocs /10query lặp2 |20|82,72|40,05|143,76|

Ở mỗi trong4điều kiện distinct/repeated×5/20, fast-exact thắng memo ở0/16Arg và0/16Sci. Tại Sci distinct20 có2/16query nhanh hơn full nhưng0/16nhanh hơn memo; thời gian/nguồn biến thiên nhỏ cần được đọc cùng raw repeats. Không dùng hai case này để tuyên bố online speedup.

Compiler/unique-factor giảm thành phần công việc và exact pool giảm tài liệu, nhưng initialization vẫn lớn. Đây là đo actual session, mạnh hơn break-even dự phóng35–45lượt của báo cáo cũ. Các cohort và workload khác nhau nên không suy ngược một ngưỡng hòa vốn chung. [session-summary.csv](results/session-summary.csv), [factor-summary.csv](results/factor-summary.csv), [factor-session-summary.csv](results/factor-session-summary.csv) chứa đầy đủ phương pháp, mọi điều kiện và win counts. Tổng cộng384primary+960supplemental+1152factor-audit=2496timed session executions; đây là các lặp/đối chứng phụ thuộc trên cùng32query, không phải2496người dùng độc lập. Sequence là synthetic controlled edits, không phải hành vi người dùng quan sát.

## 7. Kiểm tra độc lập và công bố

-32/32query được giữ, không truncation/không chọn bỏ case; hai bộ verifier đều không có mismatch.
-3280324original projected states được enumerate độc lập theo thứ tự khác; không dùng quotient làm đáp án chuẩn.
-726839visited quotient states và14653862scorecells được kiểm tra từ representative ORIGINAL factor; kiểm tra coverage mọi original form, minimum cost, group multiplicity, ties và saturation/complete flag.
-512conditional leaves được đối chiếu bằng full-corpus bounds không dùng compiled cache;857attaining witnesses đối chiếu trên toàn corpus.
-86836463điểm integer token-form/document được dựng lại bằng gram extractor riêng và Python integer accumulation từ stored source index;0sai khác. Kiểm tra này nhắm scorer integer đã định, không formal-proof compiled libraries hoặc floating log builder.
-Dựng lại cả hai index từ corpus byte gốc có hash pin, cho canonical integer-weight hash trùng bản đã khóa. Helper `prepare_index.py` tải/dựng cache ngoài repo và giữ nguyên mọi parent environment/result file, để đường tái lập không ghi đè bằng chứng cũ. Đây là audit sau kết quả, không phải tập test xác nhận mới.
-Primary20request sets và toàn bộ supplemental/factor-audit answer hashes được dựng lại từ F; dữ liệu lưu đầy đủ request text/edits, method/order/timings, expected sets/hash và mọi source/freeze hash.
-3nhóm test compiled/quotient và1nhóm unique-factor differential test đạt; runtime chỉ2CPU/8GiB, không GPU/paidAPI/nhãn mới. Các thời gian source/verifier chỉ là log kiểm tra, không dùng để so ranker production.

Mọi factor NPZ dùng unique form rows và mapping về từng vị trí; không bỏ bớt document. File proof lưu descriptor/bitset cho MỌI state thực sự đã thăm; không bịa trace cho các trạng thái không cần duyệt sau closure. [results/](results/) và [hướng dẫn tái lập](README.md) kèm toàn bộ logs, checksums và query source provenance.

## 8. Novelty, dataset và quyết định paper

Khoản bổ sung có thể bảo vệ là khả năng tính/kiểm tra exact finite-edit union trên nguyên truy vấn, phép tách đối chứng cơ chế, và artifact oracle có thể kiểm chứng mà không nhãn người mới. Dataset kế thừa hai corpus thật, còn edits/requests là synthetic; không phải collection mới hoặc natural typo logs. Quyền/credit giữ CC BY-SA4.0 như nguồn; không thu dữ liệu web của người dùng.

[Rà soát novelty](RELATED_WORK.md) cho thấy UTK đã có possible top-k/dominance/partition, và weighted-transducer pushing/minimization đã có chuẩn hóa trọng số/equivalence reduction. Repeated-token symmetry, common shifts, caching và witness closure đều là nguyên lý tiêu chuẩn. Chưa chứng minh một specialized algorithm đủ khác hoặc đủ đóng góp cho Q1; chưa tái lập nguyên bản RSA/JAA hay có independent closest-method review. Live web-search lỗi trong lượt này được ghi rõ, không trình bày coverage như systematic review.

**Quyết định hiện tại:** giữ branch để review; không merge, không deploy lên live Site. GO cho việc dùng artifact này kiểm toán tính đúng/độ chặt của finite-edit retrieval; NO-GO cho claim tăng tốc online5/20request hoặc paper đã đủ Q1. Bản thảo có thể tập trung hẹp vào exact verification nếu có thêm khác biệt phương pháp/closest-method evidence; xem [PAPER_DIRECTION.md](PAPER_DIRECTION.md). Muốn theo hướng online phải hạ chi phí trước khi tạo toàn bộ token-form scores/certificates; đó là giả thuyết nghiên cứu tiếp, chưa triển khai hay được claim là giải pháp đã chứng minh trong lượt này.

Bạn chưa cần chạy local để hoàn tất các kết quả trên. Cloud đã chạy và kiểm tra đầy đủ lượt được báo. Local giúp tái lập độc lập hoặc mở rộng tài nguyên; không tự tăng suy luận của chat hoặc bảo đảm novelty. Không cần GPU trong scope hiện tại.
