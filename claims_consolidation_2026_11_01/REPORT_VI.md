# Củng cố các claim hiện tại — 01/11/2026

Đợt này không bổ sung novelty, thuật toán, mô hình, corpus hay kênh lỗi mới.
Ba việc đã thực hiện là tổ chức lại bản thảo, rà soát nghiên cứu gần nhất và
đánh giá refinement đã có trên toàn bộ 970 truy vấn, không dùng nhãn để định tuyến.

## Một câu hỏi và hai đầu ra

Câu hỏi xuyên suốt: **với một bộ xếp hạng từ vựng cố định và một ngân sách sửa
truy vấn dùng chung, có thể chứng nhận đầu ra nào và phải trả chi phí bao nhiêu?**

Giữ tài liệu tham chiếu trong top-K là phương pháp trung tâm. Exact union là
ứng dụng kiểm toán bổ trợ, xác định mọi tài liệu có thể vào top-k. Hai đầu ra
có lượng từ và quy tắc tie khác nhau; chúng không kéo theo nhau. Cùng một
khuôn khổ nhân tử hữu hạn không có nghĩa các scorer/channel lịch sử giống
nhau về số học. Phần float/casefold/full channel và integer/lowercase/compact
channel được giữ rõ; bridge còn phát hiện khác biệt thật.

Các corpus lỗi gõ kiểm tra phạm vi của kênh. Cross-encoder kiểm tra tác động
và giới hạn chuyển tiếp. Chúng không được viết thành hai đóng góp phương pháp
mới hay bốn bước của một hệ thống đầu cuối đã được đo. Fig1/Fig2 vẫn chưa vẽ.
Bản thảo được giữ ngoài Git; các bảng, phương trình và chứng minh cũ được
chuyển vị trí khi cần, không sửa số liệu hay xóa kết quả bất lợi.

## Rà soát gần nhất

Đã đọc nguồn chính của CostCert, UTK, Wong–Kolter, fuzzy search và CertEx;
phiên bản, mục đã đọc và hash PDF có trong PRIMARY_SOURCES.json. Nguồn
CostCert đã đọc là preprint v1; DOI trích dẫn là bài QRS xuất bản, không tự
khẳng định hai bản giống hệt. Bản PDF tác giả của fuzzy search có trường DOI
placeholder: không dùng trường đó làm DOI xuất bản.

Shared budget, possible-top-k union, conflict cuts, DP, LP/MILP và DSATUR đều
có tiền lệ. Bài chỉ bảo vệ certifier được định nghĩa, chứng minh có điều kiện
và kết quả đối chứng đã chạy. Fixture không thay thế thực thi CostCert;
RSA/JAA segment pilot không thay thế benchmark toàn miền NLP. Rà soát hữu
hạn này không phải chứng minh ưu tiên toàn cầu. Ma trận claim/evidence và
những điều không được suy rộng nằm trong CLOSEST_WORK_AUDIT.md.

## Replay refinement trên toàn bộ truy vấn

Giữ nguyên 970 ID, index, preprocessing, B=2/K=10 và nguồn thuật toán cũ.
Runner không mở nhãn ROBUST/NONROBUST. Chỉ sau khi chạy xong mới ghép bộ nhãn
kiểm chứng hiện có. Default bound khớp hoàn toàn dữ liệu đã lưu.

| Corpus | Truy vấn | Default | Refinement | Robust đã kiểm chứng | Prefix median (s) | Total median (s) | Total p95 (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| SciFact | 199 | 123 | 123 | 123 | 0.180 | 0.182 | 1.422 |
| NFCorpus | 223 | 45 | 47 | 47 | 0.102 | 0.105 | 0.335 |
| FiQA | 548 | 91 | 96 | 96 | 1.120 | 1.235 | 2.545 |

Tổng **259 → 266 chứng nhận**, đạt 266/266 ca robust; không chứng nhận nhầm
ca nào trong 704 ca nonrobust theo bộ kiểm chứng hiện có. Đây là replay
hồi cứu trên dữ liệu đã biết, không phải xác nhận mới trên truy vấn chưa xem.
Số 259/260 của Discrete/MILP và các kiểm định gốc giữ nguyên.

259 truy vấn đã có chứng nhận nên bỏ qua refinement; 522 vượt cap 80
competitor; 11 có zero witness giữ cận hạng toàn corpus. Có 178 truy vấn
vào full-pair, gồm 7 robust và **171 nonrobust**. Thực hiện 189.303 phép thử
cặp, không gặp cap Pareto hay guard xây dựng 120 giây. 144 cận hạng giảm;
cận giảm không đồng nghĩa có chứng nhận hay có witness tấn công. 704 ca
không được chứng nhận bởi refinement không tự trở thành bằng chứng tấn công;
nhãn nonrobust ở đây đến từ bộ witness kiểm chứng riêng.

Phần thêm tốn tổng **121,792 giây**, trong đó **120,198 giây** trên các ca
nonrobust. Trong 178 ca vào full-pair, median phần thêm 0,427 giây, p95
1,978 giây. Trên toàn 970 truy vấn, median tổng 0,719 giây và p95 2,163 giây;
tổng thời gian pipeline ghi nhận 809,529 giây. Prefix và refinement được đo
trong cùng một lượt tích hợp, không phải hai phương pháp chạy độc lập theo
thứ tự ngẫu nhiên. Các số này loại trừ tải index dùng chung đã warm; không
suy rộng sang GPU hay production. Phân bố theo robust/nonrobust, corpus,
route và trạng thái cap được giữ đầy đủ trong results/analysis.json.

## Những giới hạn vẫn xuất hiện ở phần chính

- MILP có cấu hình tốt hơn; không có claim Discrete thắng mọi trường hợp.
- 2,35 lần chỉ là tỷ lệ chi phí xây union offline so với control đã chạy.
  Gate session 20 request gốc thất bại và không bị đổi thành thành công.
- GTC B=2 là 91/200 = 45,5%, không phải 91% lỗi tự nhiên; JFLEG có mục tiêu
  khác và không gộp tỷ lệ. Các trường hợp ngoài scope vẫn trong mẫu số.
- Top-10 neural của coarse pool chỉ được union giữ trung bình 65% ở panel
  đã đo. Hai cascade đối chứng có cùng 67.571 neural pairs; không claim
  giảm công việc neural hay bảo toàn top-10 neural toàn cục.
- Top-50 thông thường rẻ hơn ở panel cost và raw nDCG nhỉnh hơn union.
  Giá trị union là static completeness dưới kênh hữu hạn đã khai báo.

Không phát triển thêm nhánh nghiên cứu hay mở rộng novelty trong đợt này.
Mục tiêu là một bài có trọng tâm, claim khớp bằng chứng và giới hạn rõ ràng;
không tuyên bố đã bảo đảm được nhận Q1.
