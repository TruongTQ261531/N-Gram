# Định vị bài và kế hoạch bảo vệ đóng góp

Ngày chuẩn bị: 30/10/2026, Asia/Saigon. Cơ sở khoa học: commit `94a9f0c`.

## Quyết định trung tâm

Chọn **bộ chứng nhận rời rạc cho truy vấn sửa chung trên toàn corpus**, không
chọn CAPC/BOLT hoặc một thuật toán lai chưa thực nghiệm làm tâm bài.

Mệnh đề cần bảo vệ: với scorer n-gram cộng cố định và tập sửa token hữu hạn,
phân tích bất tương thích rời rạc có thể chứng nhận thêm truy vấn ngoài cận LP
dùng chung truy vấn, trong giới hạn tài nguyên có báo cáo và với trace kiểm
chứng được. Độ vững/khả năng chứng nhận là mục tiêu; không nhận là tăng
relevance, SOTA NLP nói chung, hay bảo đảm câu trả lời RAG.

Ứng dụng pool/cache trả lời một câu hỏi khác: giữ mọi tài liệu có thể lọt
top-k, bao gồm ties. Dùng phần này làm bằng chứng ứng dụng bổ sung; không
coi giữ một winner là chứng minh containment của cả pool. Dataset oracle là
artifact hỗ trợ kiểm tra, chưa định vị thành một bài dataset độc lập.

## Reviewer sẽ phản biện gì và cần trả lời bằng gì

| Phản biện | Hiện đã có | Cần làm trước khi chốt claim |
|---|---|---|
| CostCert đã nhận ra ngân sách dùng chung | Đã thừa nhận overlap; khác cấu trúc voting/image patch với margin cộng thực | Đọc lại đầy đủ method/proof; dựng bảng ánh xạ biến/giả định; thử một đối chứng chuyển được sang cùng bài toán, hoặc chứng minh lý do không chuyển được. Không so phần trăm giữa hai threat model khác nhau |
| Cover/DP/LP là kỹ thuật cũ | Có construction cho khoảng cách LP–rời rạc và đối chứng LP tổng quát | Tìm prior art ngoài IR về disjunctive verification/conflict graphs. Chỉ claim kết quả chuyên biệt thực sự khác; không nhận định lý integrality gap tổng quát là mới |
| UTK đã có possible-top-k, dominance và chia miền | Đã ghi rõ và chưa chạy RSA/JAA gốc | Dẫn xuất reduction của bài toán pool sang UTK nếu có; xây đối chứng cùng miền rời rạc/ngân sách và cùng output contract. Nếu tương đương thuật toán cũ, chỉ giữ phần này như ứng dụng |
| Chỉ thắng baseline yếu hoặc do baseline bị timeout | Best matched custom/generic LP + enumeration; cả 32 gain query có generic LP success | So frontier chứng nhận–wall time–RAM với MILP trên nhiều budget tài nguyên; giữ UNKNOWN/timeouts riêng, không chỉ một timeout 1 giây |
| Có ý nghĩa thống kê nhưng lợi ích nhỏ | Replication mới 970 query; 2/3 phép so sánh đạt Holm | Tách lợi ích chứng nhận và relevance. Báo mọi dataset/configuration và qrel-positive gains; không thêm test để cứu p-value |
| App tiết kiệm mỗi lần nhưng không tiết kiệm cả phiên | Đã có chi phí khởi tạo; hòa vốn dự phóng 35/45 lần ở B2,k10 | Đo phiên đầy đủ 1/2/5/10/20 lần sửa, gồm tạo pool, xác minh scope, nạp model, fallback và rebuild; so luôn lựa chọn không tạo cache |
| Dataset chỉ là lỗi tổng hợp trên corpus cũ | Có oracle đầy đủ, provenance, hai corpus mới với 128 query | Bổ sung lỗi có nguồn tự nhiên/giấy phép rõ và đánh giá channel coverage; tách corpus, chủ đề, query gốc để tránh leakage; không gọi dictionary transplant là log tự nhiên |

## Phần phải hoàn tất và thứ tự làm

1. **P0 — bảo vệ novelty:** ma trận so sánh CostCert/UTK/discrete verification,
   nhận xét tương đương có chứng cứ từ công thức, và người có chuyên môn đọc
   độc lập proof/code. Tài liệu tra cứu ít không chứng minh không có prior art.
2. **P1 — chọn đúng một mở rộng thuật toán:** thử hướng nén trạng thái hiệu ứng
   điểm bên dưới trên development; chỉ khóa confirmation sau khi chọn xong.
3. **P1 — đối chứng cùng tài nguyên:** LP hiện tại, cover hiện tại, memoized
   enumeration, MILP, phiên bản không nén và một baseline nén tổng quát.
4. **P1 — ứng dụng:** đo chi phí toàn phiên và chất lượng giữ kết quả, dùng
   lỗi có provenance tốt; nếu không có lợi ở phiên ngắn, thu hẹp claim.
5. **P2 — dữ liệu:** tăng khó/đa dạng có chủ đích, công bố cả phản ví dụ và
   trường hợp không kết luận; ưu tiên split mới thực sự hơn tăng số lỗi cùng câu.
6. **P2 — hồ sơ bài:** xác minh reference, quartile và author metadata;
   chuyển template; viết cover letter dựa trên đóng góp đã được kiểm chứng.

Không thay hoặc bỏ kết quả cũ. Mỗi nghiên cứu mới có protocol/ID/input hash,
ngân sách, metric và stopping rule riêng trước khi xem confirmation. Không
coi lặp timing là nhiều mẫu khoa học độc lập.

## Hướng tăng novelty được chọn để thử: nén trạng thái theo hiệu ứng xếp hạng

**Trạng thái: mới là đề xuất, CHƯA cài đặt, CHƯA có kết quả, CHƯA xác minh tính
mới.** Không xuất hiện như một đóng góp đã hoàn tất trong abstract/results.

Với factor nguyên F[i,a,j], chọn một tài liệu neo r và xét vector hiệu ứng

`v(i,a) = (F[i,a,j] - F[i,a,r])_{j != r}`.

Hai alternative cùng vị trí chỉ được nhập nếu **cost bằng nhau và toàn bộ
vector hiệu ứng bằng nhau chính xác**. Khi đó thay alternative này bằng
alternative kia chỉ cộng một hằng số chung vào mọi điểm tài liệu; mọi so sánh
xếp hạng và ties được giữ. Cần giữ một witness/backpointer hợp lệ. Hash chỉ
để tìm bucket; phải so vector thật để tránh collision. Nếu lọc tập tài liệu,
phải chứng minh việc lọc an toàn cho đúng target trước khi bỏ tọa độ.

Có thể tiếp tục gộp các partial state có cùng accumulated centered-score
vector và cùng budget đã dùng. DP theo token/budget sinh các vector hiệu ứng
phân biệt, giữ witness; nếu hoàn tất toàn bộ thì thu được rank/union chính
xác với ít trạng thái hơn enumeration theo chuỗi. Phải chứng minh quy nạp
rằng mọi trạng thái query đều có một đại diện tương đương. Trường hợp xấu
vẫn tăng theo hàm mũ; không nhận là giải đa thức bài toán tổng quát. Khi hết
tài nguyên, fallback về cận/pool an toàn đã có, không phát chứng nhận từ tập
partial state chưa bao phủ hết.

**Tại sao đáng thử:** khai thác cấu trúc hiệu ứng của n-gram/corpus thay vì
chỉ đổi heuristic chọn hai token. Nếu nén được nhiều và chi phí nhận dạng
thấp, có thể tăng phạm vi oracle chính xác hoặc giảm chi phí khởi tạo cache.

**Rủi ro:** state minimization, memoization, decision diagrams và quotient
states đều đã có tiền lệ. Một dict khử trùng score vector chưa tự là thuật
toán mới. Vector trên corpus lớn có thể đắt hơn phần tính tiết kiệm; nhiều
query có thể không có collision hữu ích. Nếu chỉ nén được ví dụ tổng hợp dễ,
không dùng nó làm claim chính.

**Thí nghiệm falsification trước confirmation:**

- Đối chiếu exhaustive oracle trên lattice nhỏ: mọi rank, tie và union phải
  trùng; kiểm tra cost, witness, fallback và raw state.
- Đo số state trước/sau, số vector khác biệt, overhead hashing/vector compare,
  peak RAM, thời gian toàn pipeline và số query được giải chính xác trong cap.
- Ablation: không nén / chỉ token-local / thêm partial-state / memoized
  enumeration với cùng scorer và cap; không quy công tối ưu cache phổ thông.
- Bao gồm query không nén được, OOV, ties và dữ liệu nhiễu thực có nguồn.
- Tiêu chí tiếp tục: không có sai khác oracle; có lợi ích end-to-end ổn định
  trên development vượt đối chứng memoization, không chỉ giảm bộ đếm state.
  Chọn ngưỡng/tài nguyên và khóa protocol trước tập xác nhận mới.

Hướng thứ hai chỉ nên xét sau đó: refinement thích nghi tập trung vào các
tài liệu gần biên top-k, có bound giảm độ lỏng và stopping policy tính cả
chi phí phiên. Đây cũng cần đối chiếu branch-and-bound/adaptive verification;
không tăng novelty bằng việc đặt thêm acronym.

## Shortlist tạp chí theo mức phù hợp

Đây là **ứng viên cho mục tiêu Q1**, chưa phải danh sách đã xác minh Q1 năm
hiện hành. Quartile phụ thuộc JCR/SJR, năm và category. Truy cập publisher,
Crossref và SJR trong phiên này bị HTTP403; không có căn cứ gắn số IF,
acceptance rate, APC hay thời gian review. Không dùng con số tự đoán.

| Ưu tiên theo hướng bài | Tạp chí / nguồn chính thức | Phù hợp | Điều kiện trước khi cân nhắc nộp |
|---|---|---|---|
| 1 | [Information Processing & Management](https://www.sciencedirect.com/journal/information-processing-and-management) | IR và xử lý thông tin; hợp bài method gắn utility thực tế | Làm rõ khác biệt certifier và có tác vụ/chi phí truy hồi thuyết phục; xác minh scope, quartile đúng category |
| 2 — mục tiêu tham vọng | [ACM Transactions on Information Systems](https://dl.acm.org/journal/tois) | Đúng chuyên môn IR, có thể phản biện sâu novelty | Cần đóng góp thuật toán đủ rõ, đánh giá mạnh, liên hệ CostCert/UTK chặt và lợi ích ngoài artifact engineering |
| 3 | [Information Sciences](https://www.sciencedirect.com/journal/information-sciences) | Phương pháp tính toán/optimization cho xử lý thông tin | Cần phần thuật toán hoặc lý thuyết mới thực chất và thí nghiệm tổng quát; dashboard không đủ |
| 4 — nếu chuyển trọng tâm data systems | [IEEE Transactions on Knowledge and Data Engineering](https://www.computer.org/csdl/journal/tk) | Possible-top-k, cache và hiệu quả hệ thống dữ liệu | Phải vượt phân hoạch/dominance có trước và có scale/latency/session study; phù hợp yếu nếu chỉ có certifier nhỏ |
| 5 — chỉ khi có use case mạnh | [Expert Systems with Applications](https://www.sciencedirect.com/journal/expert-systems-with-applications) | Hệ thống ứng dụng có đánh giá rõ | Cần bài toán ứng dụng và lợi ích thực, baseline/domain protocol; app demo đơn thuần chưa đủ |

**Chọn trước mắt:** dùng IPM để định hướng nội dung, giữ TOIS làm lựa chọn
tham vọng nếu đóng góp phương pháp qua được P0/P1. Chưa nộp đồng thời nhiều
tạp chí. Chưa coi danh sách này là khuyến nghị trả APC hay bảo đảm được nhận.

Trước khi chọn chính thức, ghi lại: index cơ quan yêu cầu; năm metric mới
nhất đã công bố; category cụ thể; quartile; URL nguồn; ngày truy cập; loại
bài, giới hạn trang, template, chính sách dữ liệu/AI assistance và phí từ
nguồn chính thức. Tác giả quyết định mục tiêu sau khi có thông tin đó.

## Phạm vi branch này

Branch này chỉ bổ sung kế hoạch nghiên cứu bằng Markdown. Không chứa bản
thảo LaTeX, BibTeX, PDF hay template nhà xuất bản; các file đó được lưu riêng
ngoài checkout theo yêu cầu. Chưa triển khai thuật toán nén trạng thái và
không phát sinh kết quả thực nghiệm mới trong branch này.
