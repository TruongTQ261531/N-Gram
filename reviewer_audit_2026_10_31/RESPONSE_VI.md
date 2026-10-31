# Phân tích phản biện Argon và những sửa đổi có bằng chứng

> Cập nhật: MILP và timing đã hoàn tất trên 970 truy vấn. Các đoạn ghi “bị chặn/chưa chạy” dưới đây thuộc bản phân tích ban đầu; xem mục “Cập nhật sau khi mở mạng” ở cuối và README cho trạng thái hiện tại.

31/10/2026, Asia/Saigon. Kết luận: phản biện chỉ đúng phần lớn; có hai
chỗ cần điều chỉnh cách diễn giải. Đây là sửa scope và kiểm tra bổ sung
sau khi đã biết kết quả, không phải một đợt confirmation độc lập mới.

## A. Session và offline auditing

**Đúng:** không thể dùng số liệu này để bảo vệ tăng tốc interactive edits.
38/128 và1/128 là thất bại của gate đã định; cả32 query full-text trước
cũng không thắng memo ở các phiên đã đo. Định vị đóng góp3 thành
**Index-First Offline Exact-Union Auditing** là hợp lý. Baseline của công
việc offline phải thực sự trả complete union; memo/incremental chỉ trả
các request đã nhận nên không phải cùng output contract ở phép đo đó.

**Cần nói chính xác hơn:** số liệu âm không làm hỏng claim offline, và
2,35x không phải thắng mọi thuật toán. Nó là paired geometric speedup so
với nhanh hơn của HAI control offline đã chạy, thắng107/128 query. Chưa
chạy RSA/JAA thì không được suy thành thắng UTK/SOTA.

Không được sửa lịch sử bằng cách gọi session là secondary ngay từ đầu:
session20 là một primary test cũ và thất bại. Bài được rescope sau kết quả;
giữ thông tin đó. Các điểm1/5/20 không xác định được actual break-even.
Chỉ gọi là short-session boundary/falsification analysis. Với memoization,
cost còn phụ thuộc số chuỗi khác nhau; kéo dài request lặp không tạo cùng
lợi ích như giả định tuyến tính mỗi edit.

**UTK:** offline union vẫn nằm gần uncertain top-k. Chuyển heading không
xóa yêu cầu closest-method comparison. Truy cập bản gốc VLDB hiện403;
hai tìm kiếm repository GitHub theo title/author không có kết quả, không
có nghĩa code không tồn tại. Không viết lại một control rồi gắn tên
RSA/JAA. Điều kiện tiên quyết còn mở được ghi rõ trong paper/report.

## B. MILP và đo thời gian

**Đúng:** Bảng2 thiếu một đối chứng mạnh. Không có bằng chứng rằng970
query MILP đã được chạy rồi bị giấu: mã replication.py cũ chỉ gọi proposed
và genericLP; freeze gốc định primary comparison với bestLP. Tuy vậy một
reviewer có lý khi yêu cầu MILP ở cùng tập và điều kiện, nhất là khi MILP
đã thắng ở một số B3. Không có quyền claim ưu thế phổ quát trước MILP.

Đã viết runner bổ sung giữ đúng199/223/548IDs, B2,K10,1second solver cap,
2million-entry cap và source float index gốc. Nó kiểm tra lại rank LP/
Discrete với archive trước khi chấp nhận hàng mới; báo timeout/skip/bounds/
fallback và replay witness toàn corpus. Cột thiếu phải ghi **unmeasured**,
không dùng0 hoặc tự suy ra coverage từ LP. Solver là numerical reference,
không giả làm một chứng nhận dual đã được formal/interval validation.

**Đúng nhưng không phải quy định cứng của Q1:**10 query/corpus có thể là
microbenchmark thăm dò, không đủ suy rộng phân phối latency. Đã hạ vai trò
bảng này xuống appendix và gỡ mọi claim tốc độ certifier dựa trên nó.
Đã kiểm kê cả970 archival times, nhưng chúng gộp proposed+genericLP+
diagnostics và có thể cạnh tranh CPU; KHÔNG dùng chúng thay timing riêng
từng method. Runner mới đo full pipeline trên tất cả970 trong một pass
balanced-order;48IDs/corpus định trước được lặp thêm hai lần để xem noise,
không chọn lần chạy nhanh nhất làm primary result.

**Trạng thái thật:** chưa chạy phần bổ sung này vì cache/raw source cũ
không còn;20/20 file đầu vào đang thiếu và HuggingFace bị policy403.
Download manifest có hash/version đầy đủ. Có restore script chỉ chấp nhận
đúng byte hash và dựng index khớp canonical fingerprints. Pipeline đã qua
kiểm tra exhaustive nhỏ và6 fixture B2 thật; không coi fixture là970 query.
Thiếu dữ liệu không được đổi thành kết quả âm hoặc synthetic benchmark.

## C. Hai scorer và kiểm tra cầu nối đã chạy

**Đúng về presentation và nguy cơ transfer sai; không có nghĩa hai hướng
toán học tự động là hai paper không liên quan.** Cả hai có cùng hợp đồng
additive finite-query factors, nhưng retention và union là hai output
contracts. Các theorem dùng chung phải tách khỏi numerical instantiation.
Không sửa chữ float thành integer hoặc lowercase thành casefold rồi giữ
nguyên metric cũ. Frozen results luôn giữ đúng model/threat identity.

Đã chạy matched retrospective audit trên CÙNG128 WANDS queries và6.684
trạng thái B2, cùng corpus43.000 xấp xỉ (chính xác42.994), cùng reference
được chỉ định, cùng compact lattice, ba backend:

| Kiểm tra | Integer/lower vs Float/lower | Integer/lower vs Float/casefold |
|---|---:|---:|
| Top-k trạng thái giống nhau |6.684/6.684|6.683/6.684|
| Exact union theo query giống nhau |128/128|128/128|
| Worst reference rank giống nhau |128/128|127/128|
| Quyết định retention K10 giống nhau |128/128|128/128|
| Trạng thái còn UNKNOWN sau exact-boundary refinement |0|0|

Tái dựng unrounded float từ cùng counts/vocabulary rồi round lại tái tạo
đúng TOÀN BỘ26.954.436 trọng số integer. Bound sai số mỗi weight là
5,0000000912e-7. Rule strict-margin đầu chỉ chứng minh6.277 states;407
boundary ties được giữ và kiểm tra bổ sung bằng tổng dyadic chính xác của
các trọng số float đã lưu. Các sum khác xa biên được loại bằng numerical
enclosure; có cap256 ambiguous docs và UNKNOWN fallback (không bị dùng
trong lượt này). Giữ nguyên cả output pass1 lẫn refinement để không giấu
độ bảo thủ của rule ban đầu.

Casefold thật sự làm đổi5 product representations, dù0 raw query đổi.
Ở query110/state[0,0,2], top-k của float/casefold khác integer/lower;
ở query83, worst reference rank là28.874 thay vì28.872. Tuy nhiên union
theo query và quyết định K10 vẫn giống trong tập này. Đây là counterexample
thực nghiệm cho cách nói hai scorer đồng nhất; không được xóa khác biệt.

Do đó paper được sửa thành **một framework, các numerical instantiation
riêng, có matched bridge cho cả retention lẫn union**. Tốc độ2,35x vẫn chỉ
thuộc integer/lower offline implementation. Kiểm tra này không chuyển
metric SciFact/NFCorpus/FiQA hoặc full variant channel sang WANDS compact,
không bảo đảm corpus/language mới, và không phải novelty thuật toán mới.

## Một lỗi diễn giải bổ sung cần sửa

Pool containment không đơn giản là một mệnh đề “mạnh hơn retention”.
P=toàn corpus luôn containment, kể cả khi reference rớt. Ngược lại giữ
một reference không xác định union mọi tài liệu có thể lọt top-k. Hơn nữa
retention dùng worst-case tie rank còn union giữ mọi boundary ties. Paper
phải định nghĩa hai output contracts riêng, không suy luận cái này từ cái
kia. Chỉ containment với đúng original weights mới bảo đảm re-score trên
pool cho cùng top-k của backend đó.

## Kết luận về tình trạng sửa

Đã sửa định vị/claim, giới hạn của timing cũ, sự minh bạch cột MILP, và
thực hiện matched numerical bridge có counterexample công khai. Chưa đóng
được benchmark MILP970, broad controlled timing và original RSA/JAA.
Chúng là thiếu hụt thật, không phải vấn đề có thể giải quyết chỉ bằng câu
chữ, và không có căn cứ nâng đánh giá lên “sẵn sàng Q1”.

## Cập nhật sau khi mở mạng — trạng thái hiện tại

Các đoạn “bị chặn/chưa chạy” phía trên mô tả thời điểm phản biện ban đầu.
Mạng hiện đã mở;20/20 file gốc khớp SHA256 và cả ba index khớp fingerprint.
Đã hoàn tất MILP/controlled timing cho đúng970 query IDs cũ, B2/K10.
Không thay dữ liệu, không đổi freeze, không dùng repeat thuận lợi để chọn
kết quả. Lượt đầu trên tất cả query là kết quả báo cáo chính của supplement.

| Corpus | n | BestLP+enum | Discrete | MILP+enum |
|---|---:|---:|---:|---:|
| SciFact | 199 | 115 | 123 | 123 |
| NFCorpus | 223 | 41 | 45 | 47 |
| FiQA | 548 | 71 | 91 | 90 |

MILP là numerical solver reference; không giả làm formal dual proof.
Các giới hạn1giây solver/2triệu matrix entries, timeout/skip/fallback và
witness replay được công khai. Discrete không vượt MILP nói chung.
Bảng paired mới và runtime đầy đủ nằm trong coverage_and_runtime_status.json.
Đây là phần bổ sung hồi cứu trên query cũ, không gọi là replication mới.

Có3774 method executions:970 lượt đầu cho mỗi method và hai repeat thêm
trên48query/corpus. Chỉ199/223/548 query là các đơn vị thống kê độc lập theo
query; không nhân cỡ mẫu bằng số repeat. Timing đo cả pipeline với warm
index, một numerical thread, các corpus chạy tuần tự. Bảng10query cũ vẫn
chỉ là exploratory B1/B2/B3; archival combined cost cũng không được dùng
thay timing riêng method. Median/IQR/P95, paired ratios, thứ tự chạy và
biến động kết quả MILP ở repeat đều được giữ.

Verifier riêng xét đủ34query có quyết định coverage khác nhau giữa ba method; 34query được upper-enclosure xác nhận K10. Cap lớn chỉ để kiểm tra, không đổi rank/timing của phương pháp trong bảng.
Verifier dùng lại screening và margin enclosures gốc, không là kiểm chứng
độc lập toàn bộ sparse libraries. UNKNOWN/inconclusive không phải bằng
chứng MILP sai.

Đã lấy được bản gốc UTK và một source mirror tự dẫn đúng DOI, pin16466c8.
Native RSA khớp union liên tục trong fixture3doc. JAA với IO harness gốc
bỏ các subregion vì guard dịch bit trả0; giữ nguyên thất bại và tách variant
sửa guard với hashes/logs riêng. Xem native_utk reports cho kết quả thực.
Đây chưa phải đối chứng RSA/JAA trên cùng NLP lattice; việc sửa guard
không chứng minh thuật toán công bố sai. Không publish source/binary bị
hạn chế phân phối, và không đổi tên baseline hiện có thành RSA/JAA.

CostCert đã có shared atomic vote budget. Fixture nguyên nhỏ phân biệt
free allocation với correlated bundle, không nhận là chạy code tác giả
hay chứng minh novelty toàn cục. UTK đã có possible-result union; CertEx
cũng đã có screening số học an toàn. Đổi domain/heading hoặc thêm trích dẫn
không tự tăng novelty. Phần tách biệt thuật toán với closest methods và
benchmark matched UTK vẫn là việc thật cần làm trước khi bảo vệ Q1.

Bản main/bib được sửa cục bộ, ngoài Git; Fig1/Fig2 vẫn chưa vẽ. Các số liệu
âm của session cũ, counterexample casefold, và giới hạn novelty đều còn.
Không có căn cứ gọi bài là global SOTA hoặc cam kết đã đủ Q1.
