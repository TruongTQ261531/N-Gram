# Báo cáo kiểm chứng claim — 5/11/2026

Đã hoàn thành panel bổ sung có giới hạn và rà soát toàn bộ cohort cũ. Không tạo mô hình, corpus hay đóng góp độc lập mới; không thay đổi các scientific freeze trước đây. Các kết quả dưới đây là **hồi cứu**, không phải xác nhận mới trên dữ liệu chưa từng quan sát.

## Những gì đã thực hiện

1. Verifier toàn bộ archive và18 test round3 đạt trên worktree riêng; bao gồm1.200 so sánh exhaustive và210 kiểm tra interval độ chính xác cao. Sáu test cho wrapper ablation mới đạt trước khi chạy panel.
2. Ghép đủ970 truy vấn gốc với runtime, MILP, decision labels và refinement. LP227, Discrete259, MILP260;266 robust/704 nonrobust. Không chạy lại970 solver rồi gọi là dữ liệu mới.
3. Chọn36 truy vấn:12/corpus, phân tầng độ dài và hash cố định, không dùng nhãn/kết quả để chọn. Chạy684 pipeline mới; giữ mọi cap/unknown. Xuất2.736 quyết định tại K=1/5/10/20 từ cùng các rank bound, không tính chúng là2.736 lượt đo thời gian.
4. Xây oracle độc lập cho12 miền tổng hợp nhỏ,16 tài liệu/miền: tự đếm n-gram, điểm dùng số nguyên dyadic chính xác trên trọng số float64 đã lưu; duyệt Cartesian product và ngân sách vị trí thay đổi.396 kiểm tra,0 cận sai,185 outcome có chứng nhận dương không tầm thường.

## Kết quả mới và hệ quả cho claim

| Cấu hình | B2,K10 — số chứng nhận/36 |
|---|---:|
| Pair + enum |11|
| Best LP + enum |13|
| Discrete support-only |14|
| Discrete đầy đủ |15|
| Discrete bỏ LP |15|
| Discrete bỏ enum |15|
| MILP + enum |14|

Graph có thêm coverage so với LP; Pareto/lịch chứng minh đầy đủ thêm một outcome so với support-only ở K10. Nhưng **LP và enumeration không tăng số chứng nhận K10 sau graph trên mẫu này**. Chúng vẫn siết12 và1 cận rank. Không bảo vệ được câu “mọi thành phần đều thiết yếu cho quyết định” từ các dữ liệu này.

Tại K20, support-only đạt19 so với bản đầy đủ18. Truy vấn NFCorpus PLAIN-2430 dùng hết120 kiểm tra ở cả hai cấu hình: full tạo68 cạnh incompatibility (6 Pareto), support-only62, nhưng cover có20 nhóm so với19. Oracle mạnh hơn làm thay đổi first-fit/check schedule; tổng số cạnh nhiều hơn không bảo đảm partition tốt hơn. Không có vi phạm soundness; đây là giới hạn của pipeline bị chặn tài nguyên.

Tại K10,B1, cả bốn control chính đạt28/36. Tại B3: pair/LP/Discrete/MILP đạt10/10/11/12, gồm3 context cap chung mỗi phương pháp. Không có ưu thế đồng đều trước MILP. Bỏ screening chạm cap20M dense cells trên8/36 case và chỉ đạt13 chứng nhận; thời gian giảm do bỏ dở không được tính là speedup.

## Bất đồng trên toàn970

Giữ đủ34 truy vấn thuộc hợp bất đồng coverage, bao gồm32 gain trước LP. Cả32 gain có generic LP giải thành công và proof receipts; không phải chỉ thắng vì LP bị skip. Chỉ13 clean winner của chúng có positive qrels.

- NFCorpus PLAIN-2240: pair/LP/Discrete/MILP =26/23/12/7.
- NFCorpus PLAIN-1141:40/36/22/9.
- FiQA5369:24/19/8/13; MILP time-limit, gap0.714286.

Hai NFCorpus MILP solve báo optimal; enumeration bị cap trong cả ba bất đồng. Optional refinement hồi cứu có thể khôi phục bảy chứng nhận còn thiếu nhưng chi thêm121,792 giây, trong đó120,198 trên nonrobust. Số259/260 ban đầu và các test chính không đổi.

## Chi phí, bộ nhớ và giới hạn suy luận

Runtime archive có3.774 dòng, gồm2.910 first-pass whole-pipeline runs trên đủ970 truy vấn x3 phương pháp. Không thay first pass bằng subset lặp. Các stage time và method-local memory không được đo trong archive được giữ là thiếu, không điền0.

Panel mới có stage times và process RSS lấy mẫu20ms. Mức cao nhất3.119,1MiB bao gồm index thường trú và allocator; không phải bộ nhớ tăng thêm chính xác của từng method. CPU quota4, RAM32GiB, một numerical thread. Host không độc quyền; một tiến trình kiểm tra miền nhỏ có chạy trong một phần panel. Một pass nhỏ chỉ hỗ trợ mô tả, không hỗ trợ claim speedup thống kê mới.

## Những claim cũ vẫn giữ nguyên

- Locked970: Discrete259 vs LP227, hai trong ba test vượt Holm; numerical MILP260 hồi cứu.
- Optional all-query replay:266 robust được chứng nhận,0/704 false certifications, điều kiện numerical/screening vẫn áp dụng; không phải xác nhận độc lập mới.
- WANDS offline: tỷ số geometric2,3474 với hai baseline gốc, không phải native RSA/JAA speedup.
- Session gate thất bại:38/128, ratio0,7472; lặp1/128. Không tuyên bố online/cache acceleration hay break-even đã đo.
- RSA-FD/JAA-FD hoàn tất đối chứng hữu hạn cùng contract; đây là adapter Python có instrumentation, không phải tái hiện hiệu năng C++ gốc.
- Lexical union giữ đầu vào cascade nhưng không giảm67.571 neural pairs khi memoization tương đương; coarse neural top10 containment65%, mất trên14/16 query.
- Dataset/correction panels là audit computational/channel membership, không phải corpus truy vấn lỗi tự nhiên mới hoặc bảo đảm semantics.

## Đánh giá IP&M

**Có cơ sở để xem IP&M là mục tiêu nộp nghiêm túc, nhưng chưa thể nói tính mới chắc chắn vượt desk review.** Phần vững là bài toán reference retention dưới một shared edit domain, cận kiểm chứng có điều kiện và evidence coverage/cost truy xuất được. Novelty mang tính chuyên biệt hóa và đánh giá thực nghiệm; DP, conflict cuts, coloring, shared budgets và possible-top-k đều có antecedents mạnh. Ablation làm rõ cơ chế và giới hạn, không tự biến mức novelty này thành đột phá.

Rủi ro reviewer chính là độ đáng kể của chuyên biệt hóa và giá trị IR của việc giữ một clean winner khi winner có thể chưa có positive qrel. Union nên giữ vai trò ứng dụng bổ trợ, correction/neural là scope checks; không kể như bốn contribution ngang hàng hoặc claim SOTA. Không thêm novelty mới chỉ để tăng số lượng kỹ thuật. Bản thảo đã được tổ chức theo hướng một câu hỏi trung tâm và chuyển phần kỹ thuật phụ sang supplementary.

Trước nộp cần hình chính, thông tin tác giả/declarations, kiểm tra Guide for Authors hiện hành và phản biện nội bộ bởi người chuyên IR/verification. Trang hướng dẫn IP&M trả403 trong môi trường này nên chưa xác minh được style bắt buộc hay giới hạn từ hiện hành. Bản thảo giữ numeric citations theo yêu cầu tác giả; không khẳng định mọi journal Elsevier đều dùng numeric. Không có tỷ lệ acceptance hay xếp hạng năm cụ thể được suy đoán.

Mã/kết quả nằm trên branch local ghi trong README. Chưa push/merge. Các tệp manuscript và reference audit được giữ ngoài GitHub theo yêu cầu tác giả.

## Bản thảo local sau chỉnh sửa

Main biên dịch18 trang: TeXcount4.115 đơn vị không bibliography +1.233 bibliography =5.348; đếm whitespace toàn PDF5.723, gồm cả bảng/công thức/đầu trang. Đây là cách kiểm tra dưới7.000 từ theo yêu cầu tác giả, không phải quy tắc word count đã xác minh của IP&M. Main có29 references được trích; bibliography dùng chung33 mục,28 DOI xuất bản và5 ngoại lệ chính thức chưa có DOI xác minh. Supplementary28 trang,9 references (có giao với main). Không còn mục arXiv/preprint trong bibliography đang dùng.

Giữ nguyên25 bảng gốc trên hai file; thêm2 bảng follow-up ở supplementary. Nội dung khoa học A–M giữ nguyên, chỉ sửa2 tham chiếu văn bản từ main Table8 cũ sang main Table6 mới. Fig1/Fig2 vẫn là vị trí chờ, chưa vẽ artwork. Cả hai PDF không có citation/reference chưa resolve hoặc overfull box. Các file nguồn, PDF, incoming uploads và audit DOI được giữ ngoài repository.
