# CAPC và BOLT trong một project chính thức

Ngày 29/10/2026. Bản nghiên cứu thống nhất để tái lập và đánh giá; chưa có thuật toán lai được triển khai/kiểm thử và chưa có đủ bằng chứng đóng góp Q1.

## Công việc và kết quả đã có

CAPC: 156 fit theo giao thức, hai tập tiếng Việt, chín phương pháp, năm seed; 2.430 metric và 18 re-fit kiểm tra. So với augmentation dưới nhiễu: VSFC -0,09 điểm F1, VSMEC +0,19; cả hai CI chứa 0. Chưa chứng minh ích lợi của trọng số nhập nhằng trước đối chứng xáo trộn.

BOLT: 99 fit, ba tập, sáu phương pháp, ba seed; 270 metric và 162 chẩn đoán. RBA@3 hơn augmentation +5,15 / +10,85 / +1,66 điểm trên VSFC/VSMEC/Allociné-FR. Canonical có RBA cao hơn ở cả ba tập. Robust unary trội cả F1 sạch và RBA trên tiếng Pháp; exact training chưa hơn nhất quán greedy training.

Oracle BOLT được đối chiếu với 600 bài toán vét cạn ngẫu nhiên, 180 so sánh trên prefix thật và 45 bài toán MILP độc lập. Exact oracle không đồng nghĩa mọi lượt huấn luyện đã đạt tối ưu toàn cục. Không có đợt gán nhãn mới; nhãn có sẵn không chứng minh mọi biến đổi đều giữ nghĩa. Log, đối chứng mạnh, thất bại và dự đoán từng mẫu được giữ nguyên.

## Khác nhau và chung nền tảng

CAPC đặt trọng số consistency giữa câu gốc và câu bỏ dấu. Trọng số là proxy token–nhãn, chưa xác lập là nhận biết nhập nhằng ngữ nghĩa thật.

BOLT tìm margin bất lợi trong lattice có budget, dùng witness cho mục tiêu robust. Bảo đảm chỉ cho các biến đổi cùng độ dài NFC đã định, không cho mọi lỗi gõ hay quả cầu Levenshtein.

Cả hai dùng character n-gram, biểu diễn thưa, chuẩn hóa và phân loại tuyến tính. Mình đã đề xuất/cài đặt hai cách kết hợp trong dự án; các thành phần nền tảng có tiền lệ. Hai ứng viên khác cơ chế chính, chưa được xác lập là hai phát minh mới đủ Q1.

## Khả năng bổ trợ

Ở mức project: có. CAPC kiểm tra giả thuyết trọng số consistency; kết quả âm tính giúp thiết kế đối chứng và chỉ ra giới hạn của proxy. BOLT cung cấp công cụ tìm trường hợp xấu nhất và kiểm chứng. Hai vòng cùng hỗ trợ nghiên cứu n-gram dưới biến thể chính tả trên CPU.

Ở mức thuật toán: có thể đặt giả thuyết thêm consistency có trọng số vào mục tiêu robust trên cùng encoder. **Thiết kế này chưa triển khai/chưa chạy trong bản hợp nhất.** Không suy ra điểm của tổ hợp bằng cách ghép điểm hai vòng.

Những vấn đề phải kiểm tra:

1. Proxy CAPC có thể không mang tín hiệu hữu ích, như đối chứng shuffled ở vòng 1 cho thấy.
2. Hai mục tiêu có thể cùng ép bất biến, gây dư thừa hoặc mất tín hiệu. Bỏ dấu có thể đổi nghĩa.
3. Nếu bỏ biến đổi khỏi bộ chứng nhận dựa vào trọng số, tập đe dọa đã thay đổi; không được công bố bảo đảm cho tập ban đầu.
4. Nếu chỉ đổi loss còn giữ encoder/lattice, oracle có thể tiếp tục dùng cho model mới, nhưng phải kiểm tra lại factorization và số học. Tương tác phi cục bộ mới có thể phá cấu trúc DP.
5. Cộng thêm penalty hoặc đặt tên mới không tự tạo novelty.

## Thí nghiệm tối thiểu nếu tiếp tục giả thuyết lai

Sàng lọc prior art và xác định đóng góp dự kiến trước. Giữ cùng encoder, dữ liệu, tập biến đổi, budget, cách chọn tham số và điều kiện tối ưu:

| Consistency kiểu CAPC | Worst-case training | Vai trò |
|---|---|---|
| Tắt | Tắt | Đối chứng sạch |
| Bật | Tắt | Kiểm tra consistency trên cùng biểu diễn |
| Tắt | Bật | Đối chứng BOLT |
| Bật | Bật | Ứng viên kết hợp |

Đây là CAPC-style trên biểu diễn chung, không phải tái lập nguyên xi CAPC gốc. Thêm uniform và shuffled weights; giữ canonical, robust unary và greedy training. Không bỏ các đối chứng mà BOLT đã thua.

Sàng lọc trên train/dev, kiểm tra lợi ích cơ chế và ngân sách tối ưu. Chỉ giữ ứng viên có lợi ích thực dụng trước đối chứng. Đánh giá cuối trên dữ liệu chưa phát triển; công bố CI ghép cặp, tốc độ/RAM và thất bại. Hai test tiếng Việt cũ không trở thành xác nhận độc lập khi đổi thuật toán.

Không dùng ngưỡng điểm tùy ý làm chuẩn Q1. Một kết hợp có điểm cao hơn vẫn cần đóng góp khác biệt và so sánh tương đương với công trình gần nhất. Hai novelty report và ARC/LipsLev là điểm xuất phát, không phải systematic review hoàn tất.

## Ý nghĩa của bản hợp nhất

Merge đưa hai cây mã/lịch sử vào main, không cộng trọng số model hay tạo thuật toán mới. Bản chính thức gồm hai nghiên cứu và một quy trình kiểm chứng chung.

Đã có: mã, thực nghiệm theo giao thức, kiểm tra độc lập, bằng chứng tái lập và nguyên mẫu CPU.

Chưa có: thuật toán lai được đánh giá; lợi ích cơ chế mới nhất quán; novelty đủ thuyết phục; so sánh tương đương với phương pháp gần nhất; bản thảo hoàn chỉnh đủ cơ sở nộp Q1.

Mục tiêu Q1 của yêu cầu ban đầu vẫn chưa hoàn thành. Phân hạng Q1 phụ thuộc hệ/năm/ngành tạp chí, không do merge repository hoặc số lần chạy quyết định.
