# Bảo vệ claim bằng hợp đồng, đối chứng và điều kiện bác bỏ

Luận đề trung tâm vẫn là **chứng nhận rời rạc cho một truy vấn sửa chung
trên toàn corpus của scorer cộng cố định**. Vòng index-first xử lý chi phí
của phần ứng dụng exact-pool; không thay luận đề thành một ranker mới.
Không có tiêu chí số học nào tự chứng nhận bài đủ Q1.

## Những câu có thể bảo vệ và bằng chứng cần đi kèm

| Claim | Phát biểu chính xác | Bằng chứng / điều kiện bác bỏ |
|---|---|---|
| Soundness của pool | Với đúng index nguyên không âm, lattice hữu hạn, budget token gốc và mọi ties tại biên, pool chứa mọi kết quả top-k cho phép | THEORY.md; kiểm tra độc lập bằng re-encode toàn câu, toàn corpus; chỉ một kết quả thiếu cũng bác bỏ claim |
| Exactness | Chỉ trả exact sau khi bao phủ hết miền hoặc mọi phần tử của một superset an toàn đã có witness | So union với oracle gốc; cap/timeout phải là resource_unknown, không được gọi exact |
| Chi phí certificate | So toàn bộ thời gian khởi tạo với parent và vét cạn theo lô, cùng scorer và phép tối ưu thông thường | 64 development;128 confirmation khóa trước; so paired theo truy vấn, giữ tất cả trường hợp |
| Chi phí phiên | Bao gồm certificate, tạo view và phục vụ20 yêu cầu; so memo và cập nhật điểm gia tăng | Là gate riêng. Giảm pool hoặc nhanh hơn parent không đủ chứng minh nhanh hơn phiên không tạo pool |
| Lợi ích phương pháp trung tâm | Cover rời rạc có thể chứng nhận thêm ngoài LP+enumeration đã đối chiếu | Bằng chứng970 query trước ở round3; 2/3 corpus đạt Holm, không gọi thắng nhất quán mọi corpus/MILP |
| Ứng dụng và dữ liệu | Audit computational có nguồn, oracle và domain sản phẩm mới | WANDS là nguồn kế thừa; session/edits tổng hợp; không gọi corpus mới tự thu thập hoặc dữ liệu lỗi tự nhiên |

Vòng xác nhận này cố định B=2,k=10, một scorer và một domain sản phẩm.
Không suy ra mọi ngân sách, ngôn ngữ, kiểu lỗi hoặc hệ thống IR. nDCG sạch
chỉ mô tả ranker được chứng nhận; mọi certifier dùng cùng thứ hạng nên
không có relevance gain do certifier.

## Câu đóng góp nên dùng

“Chúng tôi triển khai và kiểm tra một bộ chứng nhận chuyên biệt cho scorer
n-gram cộng dưới các phép sửa token dùng chung, đối chiếu độ chặt với LP và
phương pháp rời rạc cùng bài toán. Phần ứng dụng nghiên cứu cách tạo exact
result-union trước khi phục vụ truy vấn và đo cả chi phí khởi tạo.”

Sau khi xác nhận hoàn tất, chỉ bổ sung số liệu qua được gate tương ứng.
Các từ “đầu tiên”, “SOTA NLP”, “bảo toàn nghĩa”, “cải thiện relevance”,
“production speedup” và “đủ Q1” chưa có căn cứ trong bộ bằng chứng này.

## Điều reviewer có quyền yêu cầu thêm

1. Một khác biệt thuật toán/lý thuyết cụ thể ngoài screening, LP, clique-cover,
   caching và symmetry reduction vốn có trước; đối chiếu công thức đầy đủ
   với CostCert, UTK và verification rời rạc. Đổi domain không tự đủ mới.
2. Frontier chất lượng chứng nhận–walltime–RAM với MILP và phương pháp gần,
   cùng tài nguyên. Chưa chạy RSA/JAA gốc thì không claim thắng RSA/JAA.
3. Một workload lỗi có nguồn tự nhiên hoặc use case audit offline được
   kiểm chứng. Không biến session tổng hợp thành log người dùng thật.
4. Người có chuyên môn rà soát proof/code và tái lập độc lập. Self-check
   hiện tại sâu hơn một unit test, nhưng chưa phải phản biện bên ngoài.

Không tiếp tục điều chỉnh theo128 confirmation để cứu một claim thất bại.
288 query dự trữ còn lại giữ chưa đánh giá cho một phương pháp/giao thức
mới thật sự; trước khi dùng phải khóa lại giả thuyết và phương pháp.
