# Kết quả kiểm định các đề xuất của Argon — 01/11/2026

Đã thực hiện cả ba hướng còn lại, giữ nguyên dữ liệu đã khóa và các kết quả bất lợi. Mọi bổ sung là phân tích hồi cứu; không được gọi là xác nhận độc lập hay bảo đảm Q1.

| Đề xuất | Bằng chứng | Kết luận hợp lệ |
|---|---|---|
| 1. UTK/RSA/JAA | Đợt trước: 15/121 đoạn NLP có ứng viên ngoài toàn union rời rạc; 7/128 ca vượt cap | Có bằng chứng miền liên tục nới kết quả. Chưa phải so sánh toàn bao lồi hoặc chứng minh chậm hơn nói chung. |
| 2. Exact coloring / higher-order cuts | Cùng đồ thị cũ, greedy tối ưu 266/266; coverage vẫn 259. Kiểm tra đầy đủ các cặp + DSATUR đóng đủ 7 ca còn thiếu | Nút thắt gồm lịch truy vấn chứng minh cặp. Không cần 3-way để đóng quyết định K=10 ở tập đã thử. |
| 3. Cross-encoder | Chấm U rẻ hơn P 52.78 lần, nhưng giữ trung bình 65.0% neural top-10(P); 14/16 ca mất thành viên | Chi phí giảm khi thay bài toán, không phải tăng tốc bảo toàn cùng đầu ra neural. |
| 4. Multiword errors | GTC gốc: B1=89/200, B2=91/200; hai panel JFLEG tăng 2 và 4 cặp | B2 có ích trên một số trường hợp, không có mức tăng lớn được dự đoán trên mẫu GTC này. |

## Kết quả đồ thị có chứng minh cấu trúc

Lấy đỉnh được thêm cuối ở mỗi nhóm first-fit. Nếu đại diện nhóm trước đến sau đại diện nhóm sau, cặp đó không được truy vấn. Nếu đến trước, nhóm trước đã có đủ thành viên cuối cùng; việc từ chối nhóm dừng trước hoặc tại đại diện cuối, nên không chứng minh được cạnh incompatibility giữa hai đại diện. Các đại diện tạo clique trong phần bù của đồ thị đã truy vấn, khớp số nhóm. Vì vậy exact coloring trên đúng phần thông tin này không thể giảm số nhóm. Đây là bổ đề về lịch truy vấn cụ thể, không phải tuyên bố greedy tối ưu trên mọi graph.

Có witness kiểm tra trực tiếp cho đủ 266 graph, kiểm thử oracle graph ngẫu nhiên và hàm refinement không dùng nhãn oracle. Khi kiểm tra đủ cặp rồi dùng DSATUR chuẩn, cả bảy ca thiếu được chứng nhận. DSATUR là kỹ thuật đã có; không gọi đây là thuật toán tô màu mới. Thí nghiệm mới chọn các ca robust đã biết và không thay coverage 259/260 gốc.

## Baseline neural thông thường cũng đã được chạy

Cùng 128 query, cùng checkpoint FP32, cùng tối đa 256 token:

| Tập ứng viên | Median số tài liệu | Mean nDCG@10 | Chi phí neural / U, paired 16 query |
|---|---:|---:|---:|
| Exact union U |45|0.66951|1.000|
| BM25 top-50, giữ ties |50|0.67234|0.794|
| BM25 top-100, giữ ties |100|0.67556|1.501|

Không có ưu thế raw reranking quality/cost cho U so với top-50 trong đợt này. Đặc tính riêng được xác minh là **pool tĩnh đầy đủ cho mọi trạng thái trong kênh**: U đạt 128/128 query; clean top-50 và top-100 nếu được tái sử dụng tĩnh đạt lần lượt 7/128 và 14/128. Đây là bài toán tái sử dụng tĩnh; không gán thất bại này cho retrieval thông thường vốn truy xuất lại ở mỗi query.

Cả 6.684 trạng thái tạo cùng 67.571 neural input pairs cho hai lexical controls dưới cùng memoization theo request/document. Đã chạy actual inference cho 2.560 requests với 23,129 pair mới. Vì input giống nhau, không tự giảm được neural work của cascade đã rerank đúng lexical top-10. Chấm mọi U ở mọi distinct state sẽ tăng số pair lên 310.315. Không cache điểm cross-encoder qua query khác.

Reference PyTorch FP32 kiểm tra đủ 6.175 raw-U pairs: sai lệch lớn nhất 1.19e-05; ordered top-10 và top-10 sets cùng khớp 128/128. Các thời gian từ backend khác nhau không được trộn. Đây là đối chiếu số học quan sát, không phải neural certificate hoặc benchmark RAG end-to-end.

## Dữ liệu GTC có provenance đã phục hồi

S3 hiện vẫn báo NoSuchBucket. Bản lưu ngày 06/09/2020 từ đúng URL tác giả có SHA-1 khớp CDX và SHA-256 được pin. Schema giữ repo/commit/language/is_typo. Chọn 200 hash nhỏ nhất từ 173.179 cặp English multiword đủ điều kiện trước membership; không lọc độ khó hay B1/B2 thành công. Có 25 ca ngoài scope 32 token, giữ trong mẫu số. Nhãn ngôn ngữ/typo tự động không phải human semantic gold; dữ liệu repository correction không phải query log. Không thay hai panel JFLEG hoặc pilot từ đơn bằng nguồn mới để chọn kết quả đẹp.

Replay nguồn đủ 600 cặp đã qua. Tám trường hợp được ghi cost=2 được kiểm chứng độc lập bằng áp dụng edit witness và kiểm tra không có lời giải B1. Không đưa raw corpus text hay model weights vào Git.

## Claim trung tâm nên bảo vệ

Giữ claim về chứng nhận dưới fixed scorer + declared finite edit channel và exact static lexical union. Dùng kết quả graph và neural để nêu đúng giới hạn, thay vì tuyên bố thuật toán graph mới, global neural robustness, dataset natural-query mới, global SOTA hoặc chắc chắn Q1. Nguồn mới củng cố kiểm chứng; các kỹ thuật DSATUR và các corpora tái sử dụng không tự tạo novelty thuật toán/dataset.
