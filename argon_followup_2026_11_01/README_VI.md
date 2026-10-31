# Kiểm tra các đề xuất còn lại của Argon — 01/11/2026

Các khối này là bổ sung hồi cứu trên branch nghiên cứu hiện có. Mã/kết quả cũ
giữ nguyên. Main và references vẫn chỉ nằm cục bộ ngoài Git. Không vẽ Fig1/Fig2.
Không có tuyên bố bảo đảm Q1, đạt global SOTA hoặc thuật toán graph mới.

## Đề xuất 2: xác định đúng nút thắt của graph

Đã đánh giá đủ266ca robust đã kiểm chứng ởB2/K10. Trên đúng đồ thị được dựng
bằng120pair-checks của phương pháp cũ, greedy cover đã tối ưu266/266: cả
exact coloring và maximum compatible clique xác nhận cùng giới hạn. Coverage
kết hợp vẫn259/266. Vì thế chạy exact coloring trên đồ thị CŨ không tự sửa
bảy ca thiếu.

Trên TOÀN BỘ7ca robust bị default bỏ sót, kiểm tra đủ mọi cặp (300–1035pairs,
0,044–0,774giây/query, không pair nào vượt resource cap), rồi dùng DSATUR:

| Corpus/query | Default rank UB | Full pairs + first-fit | Full pairs + DSATUR | Exact cover UB |
|---|---:|---:|---:|---:|
| NFCorpus PLAIN-2240 |12|7|7|7|
| NFCorpus PLAIN-1141 |22|9|9|9|
| FiQA 10122 |23|10|10|10|
| FiQA 4102 |18|9|8|8|
| FiQA 7747 |15|11|10|10|
| FiQA 1150 |32|10|10|10|
| FiQA 89 |15|10|10|10|

DSATUR đạt nghiệm tối ưu trên cả7đồ thị này, được chứng minh bằng clique lower
bound khớp cover. Không cần triển khai3-way cuts để đóng quyết địnhK10 ở các
ca đã thử. Không suy rộng điều đó thành exact worst-rank hay mọiB/K.
Mọi cặp được kiểm tra bằng proof bảo thủ; thiếu conflict không tự chứng minh
hai đối thủ thật sự đồng thời khả thi. Max-clique và minimum coloring là hai
bài toán khác nhau; testC5 kiểm tra sự phân biệt này.

Có hàm `refine.pairwise_refine(D,Du,current_rank,...)` không nhận oraclelabel,
chỉ chạy khi bound chưa đủ và n<=80. Đây là refinement bằng kỹ thuật chuẩn,
không đổi các số259/260đã khóa. Thí nghiệm266case vẫn là tập chọn theo kết quả,
chưa phải970-query performance replay hay một xác nhận mới độc lập.

## Đề xuất 3: giữ đúng hợp đồng lexical-to-neural

Full-domain replay giữ128query/6684states. Cả hai retrieval controls tạo cùng
67571unique(request-text,document)pairs với memoization riêng mỗi query.
Nếu chấm mọi thành viênU ở mỗi distinct state thì cần310315pairs, tức4,5924x
trace đúng của cascade. Cross-encoder không được cache điểm qua query khác.

Đã có phản ví dụ PyTorchFP32 ởquery361: top10neural(P) chứa documentindex9971
và37909ngoàiU. Overlap-logit discrepancy chỉ9,54e-7. Vì thế U không bảo toàn
global/coarse neural top10. Thời gian tiết kiệm khi chỉ chấmU phải đi cùng
đánh giá mất đầu ra, không thể gọi tự động là speedup của cùng một bài toán.

Đợt đầy đủ dùng checkpointMiniLM-L6v2 pin233902d..., FP32ONNX, max256tokens,
length-sorted dynamic padding,batch32,4CPUthreads;128rawU,16coarse cost IDs và
20request/query. Primary cost làrepeat0cho mọi query; ba query đầu có thêm
repeat1được giữ riêng. Các phase chỉ ghép completed query blocks rời nhau,
không bỏ hoặc đổi ID theo kết quả. Metadata và phase receipts ghi rõ đường đi.
Thời gian gồm tokenization,padding,inference,ranking cho cost diagnostic;
không cộng số đo trên các backend khác nhau.

Các lần thử fixed-padding PyTorch, ONNXFP32 và INT8 được giữ riêng cùng lý do
dừng tối ưu tài nguyên. INT8 là scorer số học khác và có thể phụ thuộc batch;
không trộn vào số liệu đầy đủFP32. ReferencePyTorchFP32 trên6175rawU pairs
kiểm tra sai số backend thay vì giả định đồng nhất. Không có benchmarkGPU,
productionRAG hay end-to-end acceleration được suy ra từ component timings.
Nhãn qrel ở biến thể là proxy dùng lại nhãn query gốc, không phải annotation
ngữ nghĩa mới. Số đo grade-recall chỉ áp dụng cho các phán đoán WANDS đã có.

## Đề xuất 4: dữ liệu đa từ vàB2

GTC bucket gốc vẫn404/NoSuchBucket; mirror duy nhất tìm được thiếu provenance
labels nên không được gọi là corpus gốc. Hai proxy từ repository tác giảJFLEG,
commit ee06ff806a208aba815ac45313f4e750a48330a5:

| Đích sửa | Sample | B1 | B2 | Tăng | Ngoài32token |
|---|---:|---:|---:|---:|---:|
| Human ref0, sửa grammar/fluency nói chung |200|9|11|2|22|
| Enchant, đích spellcheck tự động của tác giả |200|51|55|4|30|

Lấy200hash nhỏ nhất từ1285/601eligible pairs trước membership, không lọc edit
distance hay ưu tiên lỗi hai từ. Không gọi Enchant là human gold, hoặc các câu
learner-English là search-query logs. Các panel có thể chồng dữ liệu và không
là hai replication độc lập. B2 có ích ở một số ví dụ, nhưng không có mức tăng
45%->65–70% mà Argon dự đoán. Không lấy kết quả thấp ở panelGEC rộng để suy
ra độ phủ natural spelling traffic; hai phân phối/đích sửa khác nhau.

Giữ licenseJFLEG CC BY-NC-SA4.0. Public artifact chỉ có hashes,line IDs,trace
operations,aggregate; không publishrawtext. Các publications bổ sung đã xác
minh DOI: Brélaz10.1145/359094.359101; JFLEG10.18653/v1/E17-2037;
GUG10.3115/v1/P14-2029. BibTeX của bài báo vẫn ở ngoài repository.

## Chạy và xác minh

`PROTOCOL.md` và các amendment được giữ theo chronology thật; không gọi đây
là preregistered confirmation. Các script từ chối ghi đè evidence. Từ repo root:

```bash
python -m unittest argon_followup_2026_11_01.test_graph argon_followup_2026_11_01.test_multiword -v
python -m argon_followup_2026_11_01.check_archive
sha256sum --quiet -c argon_followup_2026_11_01/checksums.sha256
```

Archive checks kiểm tra graph witnesses,ranking,qrels,phase selection và
analysis; replay nguồn/model cần cache riêng. Không có neural package hoặc
trọng số bên thứ ba trong Git. Cài neural-requirements.txt khi cần chạy lại
inference; model files/hash nằm trong MODEL_SOURCE.json/ONNX_SOURCE.json.
Xem results/analysis.json cho toàn bộ số đo cuối, không chỉ những ca thuận lợi.


## Cập nhật nguồn GTC và đối chứng chuẩn đã hoàn tất

Đã phục hồi payload gốc qua Internet Archive, digest khớp CDX; xem GTC_SOURCE.json và GTC_ADDENDUM.md. Mẫu English đa từ: B1=89/200, B2=91/200, ngoài 32 token=25. Giữ nguyên hai panel JFLEG trước đó.

Đã đo đủ 128 raw query, 16 coarse cost block và 2.560 session requests. Chi phí P/U=52.78, nhưng neural top-10(P) chỉ được giữ 65.0% trung bình. Đối chứng top-50/top-100 đầy đủ ở FIXED_DEPTH_ADDENDUM.md; xem RESPONSE_TO_ARGON_VI.md và analysis.json cho kết luận, gồm kết quả bất lợi.

Bổ đề lịch first-fit và 266 clique witnesses ở schedule_certificate.py/analysis.json. Chạy mới toàn inference bằng neural_recompute.py vào folder trống; không dùng continuation nếu muốn tái chạy toàn 128 query. WANDS giữ nguồn/license gốc; checkpoint giữ Apache-2.0 theo model card. Main/bib vẫn ngoài Git.
