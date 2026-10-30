# Luận đề paper sau kiểm kê: ứng viên, chưa sẵn sàng nộp Q1

Một bản thảo thống nhất nên chọn một bài toán và bộ claim được kết quả hỗ trợ. Đề xuất working title: **Exact, Auditable Candidate Sets for Character n-Gram Retrieval under Bounded Query Edits**. Đây là hướng lập luận cần tiếp tục đánh giá, không phải tiêu đề xác lập firstness.

## Claim có thể bảo vệ khi kiểm tra hoàn tất

1. Với scorer ngram cộng, corpus cố định, bộ biến thể token hữu hạn và budget đã định, một safe projection cùng quotient có coverage/cost/multiplicity được kiểm tra có thể cho hợp top-k chính xác, gồm ties. Tính chính xác gắn với mathematical assumptions và integer index cụ thể.
2. Có thể loại tính lại cận và điểm biến thể giống nhau mà giữ nguyên scorer/certificate target. Đây là tối ưu kỹ thuật phải tách khỏi novelty phương pháp.
3. Có thể tái lập/counterexample-check từ source pins, full queries, factor matrices, từng quotient state/witness và independent original-state oracle. Artifact không cần tạo nhãn relevance mới.
4. Lợi ích ứng dụng phụ thuộc initialization, số request và tỷ lệ lặp. Các kết luận phải dựa actual5/20request sessions và ordinary memoization, bao gồm cấu hình chậm hơn.

## Claim hiện chưa được hỗ trợ

- Đầu tiên đề xuất possible-top-k, equivalence reduction, caching hoặc safe threshold/dominance: có prior art trực tiếp.
- Thuật toán vượt mọi phương pháp gần nhất: chưa chạy original RSA/JAA và nhiều verification optimizers khác.
- Cải thiện relevance/RAG correctness hay chịu mọi typo tự nhiên: không phải đối tượng đo.
- Dataset mới thu thập hoặc đại diện lỗi tự nhiên: dữ liệu kế thừa với lỗi compact tổng hợp.
- Speedup production hoặc mọi phiên sử dụng: workload kiểm soát nhỏ, CPU/cloud và index warm cố định; có negative cases.
- Đủ Q1 hoặc chắc chắn được nhận: chưa có bằng chứng/đánh giá tạp chí tương ứng.

## Cấu trúc bản thảo có thể phát triển

Problem/related work về uncertain top-k và verification -> finite-edit/scorer/cost/ties contract -> safe whole-corpus projection -> compiled bounds -> rank-equivalence/multiplicity/witness proof -> independent exactness validation -> matched ablations -> whole-session utility and ordinary memoization -> artifact/provenance -> negative findings/limits.

CAPC/BOLT là lịch sử khám phá và nguồn công cụ/kiểm thử; không cộng metric khác nhiệm vụ thành một điểm tổng hay tuyên bố có hybrid được huấn luyện. Kết quả retention vòng3 có thể cung cấp bối cảnh verifier, nhưng không gán số liệu float64 cho scorer integer hoặc target result-union.

## Điều kiện còn thiếu trước khi quyết định nộp

- Independent closest-method review xác định chuyên biệt hóa nào thực sự chưa có hoặc đủ khác về kỹ thuật. Rà soát thuật toán tương đương ngoài IR/within formal verification là cần thiết; live web-search trong lượt này bị lỗi nên coverage còn hạn chế.
- Đối chiếu nguyên bản hoặc tái triển khai có kiểm tra phương pháp gần nhất theo cùng output contract, không chỉ thành phần tự chọn. Nếu đóng góp chỉ là caching/vectorization/symmetry thông thường thì cần điều chỉnh claim hoặc nghiên cứu phương pháp khác.
- Kênh lỗi có nguồn/quyền rõ và workload session độc lập phù hợp claim ứng dụng. Có thể dùng tài nguyên có nhãn sẵn để giảm gán nhãn mới; synthetic edits không được gọi natural logs.
- Scalability và generality tương ứng claim: hiện thực nghiệm chính B2,k10 và hai corpus, không tự suy rộng B lớn, dynamic corpora hoặc ngôn ngữ mới.
- Chốt tác giả/đóng góp, journal scope và quartile đúng năm/hệ thống phân hạng; hoàn thiện bản thảo theo evidence cuối. Chưa thực hiện submission.

Các bước này là nội dung nghiên cứu còn thiếu, không phải yêu cầu người dùng cấp thêm quyền cho công việc đã được giao. Branch lưu đầy đủ để review; main và live Site giữ nguyên cho tới khi có yêu cầu khác.
