# Tự phản biện có hệ thống — 5/11/2026

Môi trường đã hoạt động trở lại; vòng này trực tiếp đọc mã, kiểm tra artifact và chạy thêm đối chứng. Đây vẫn là tự phản biện của cùng trợ lý, không phải chuyên gia bên ngoài.

## Kết quả kiểm tra

- Gói trước:970 truy vấn/684 pipeline/396 kiểm tra miền nhỏ tiếp tục qua verifier, hash nguồn không đổi.
- Verifier archive tổng thể đạt trong worktree riêng;76 test của9 nhóm khoa học đạt. Bốn test mới đạt: scheduler thật với64 oracle đồ thị; phản ví dụ không chạm cap;192 phép thêm cạnh trên đồ thị hoàn chỉnh;63 instance separation nguyên chính xác.
- Replay đủ970 context gốc và hai graph layer, tái dùng prefix pair/custom-LP/enum đã đóng băng. Full tái lập mọi rank bound gốc,259 chứng nhận. Equal-weight support đạt250, full-only9, support-only0; không có chứng nhận support sai trong704 NONROBUST. Không chạy lại LP/MILP hay báo runtime pipeline mới.
- Equal-weight support vẫn chứng nhận23/32 gain trước Best LP. Phải phân biệt lợi ích của cấu hình với tính thiết yếu của DP và với mọi convex separator.
- Probe21 trọng số:155/285 Pareto edges có linear-support proof;130 chưa giải bằng grid. Trong172 Pareto edges nằm trong nhóm cuối,76 chưa được grid chứng minh. Ba partition có thể recertify hoàn toàn bằng linear supports, nhưng partition được chọn bằng full prover; không suy ra thuật toán support-only sẽ tìm được partition ấy.
- Qrel-positive clean winners:311, LP/Discrete/MILP145/158/160. Nhóm không có positive judgment:659, coverage82/101/100. Không gán nhãn irrelevant cho nhóm này và không tuyên bố tăng relevance.

## Phát hiện và xử lý

1. **Cách viết tính đơn điệu cần sửa — đã sửa bản thảo.** Optimum cover không xấu đi khi thêm incompatibility edges, nhưng first-fit và on-demand schedule có thể xấu đi. Hiện tượng có thể xảy ra khi chưa hết cap. Phản ví dụ không bác Supplementary Proposition3 về disclosed query graph. Mỗi cover vẫn sound.
2. **DSATUR/complement — mã đang đúng.** Đã đối chiếu `complement` và `greedy` trong optional refinement; chỉ làm rõ lời văn, không báo đây là lỗi code đã sửa.
3. **Attribution cho Pareto — đã bổ sung full-cohort control và proof diagnostic.** Equal-weight support không phải optimized linear separator. Dữ liệu không bảo vệ claim mọi thành phần đều cần thiết, Pareto luôn tăng coverage hoặc toàn bộ32 gain đòi hỏi nonconvex reasoning. Giữ đúng separation cho matched formulation/general additive family.
4. **Trục bài — đã thu hẹp.** Retention procedure và evidence là hai đóng góp chính; union là complementary audit dùng chung representation, không phải tầng triển khai cover. Correction/neural là scope checks.
5. **Ý nghĩa IR — đã bổ sung phân tầng qrel.** Kết quả chỉ nói retention theo nhãn gốc; không biến thành relevance của query đã sửa.

## Những phần kiểm tra được là nhất quán

Cover theorem và last-representative proposition phù hợp mã/checks. Generic LP không dùng trực tiếp solver objective làm certificate: dual weights được clip rồi đánh giá lại bằng outward support; restricted-master optimum chỉ dùng để tìm trọng số/dừng. Với32 gain, raw numerical objective10.08094–19.45593, không phải chỉ tiny rounding qua ngưỡng10; đây vẫn là numerical diagnostic. Candidate caps, unknowns và unfavorable ties được giữ đúng phạm vi. Các baseline MILP, session failure, numerical-backend mismatch và neural losses không bị bỏ.

## Còn giới hạn gì

Grid21 trọng số không tối ưu hóa mọi separator; failure không chứng minh DP thiết yếu. Không có full970 benchmark end-to-end mới cho các graph variants; context/graph times chia sẻ prefix nên không dùng làm speedup. Không tái hiện runtime C++ UTK gốc. Bibliography vẫn publication-only nhưng metadata DOI không chứng minh global novelty; mạng môi trường hiện bị tắt nên không giả vờ đã tìm lại toàn bộ tài liệu mới.

**Đánh giá IP&M:** đóng góp là specialization có kiểm chứng, chưa có cơ sở gọi là đột phá hay SOTA toàn cục. Bộ kiểm chứng và cách kể chuyện đã rõ hơn; rủi ro desk review vẫn là mức đáng kể của specialization và giá trị IR của contract. Có thể xem IP&M là mục tiêu thử sau khi hoàn thiện hình, tác giả/declarations và style theo guide hiện hành; không bảo đảm acceptance. Không cần thêm kỹ thuật rời rạc để trang trí novelty.

Các kết quả mới nằm ngoài mọi freeze cũ. Main/supplementary/bib/PDF tiếp tục nằm ngoài GitHub; code/results chỉ ở branch local cho đến khi tác giả push.

## Bản thảo sau rà soát

Main18 trang, TeXcount5,575 đơn vị tính cả bibliography; PDF whitespace5,943. Supplementary31 trang. Đây là kiểm tra mục tiêu dưới7.000 từ của tác giả, không phải giới hạn journal đã xác minh. Giữ nguyên25 bảng nguồn, bổ sung5 bảng từ hai đợt follow-up. Bibliography33 nguồn xuất bản,28 DOI và5 ngoại lệ DOI, main cite29 mục. Fig1/Fig2 vẫn chưa vẽ. Cả hai PDF không có unresolved citation/reference hoặc overfull box.
