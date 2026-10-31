# Đối chứng UTK trên đoạn điểm số NLP — 01/11/2026

Chỉ xử lý đề xuất 1 của Argon. Nhánh xuất phát từ cb45328; không sửa kết quả
đã khóa, không đưa bản thảo LaTeX lên Git, không triển khai website.

## Nhận định của Argon

Hợp lý khi yêu cầu đối chứng RSA/JAA và phân biệt miền rời rạc với bao lồi.
Không hợp lý khi dự đoán trước rằng đối chứng nhất định trả dư và chậm hơn,
hoặc cho rằng chỉ chiếu lên vài token vẫn bảo toàn bài toán. Một phép nhúng
simplex cũng chưa tự làm mất các ràng buộc tương quan giữa token. Chỉ có thể
bỏ câu giới hạn ở đúng phần đã thực sự đo; thí nghiệm thêm không bảo đảm Q1.

Các đề xuất còn lại chưa triển khai: exact coloring có ích nhưng không bảo đảm
vài ms hoặc thay thế việc đối chiếu nghiên cứu trước; cross-encoder không được
bảo toàn thứ hạng chỉ nhờ union lexical, cũng không mặc nhiên tiết kiệm 50 lần;
pilot đa từ hợp lý nhưng dữ liệu GTC gốc hiện không tải được và không thể đoán
trước độ phủ B2 tăng lên 65–70%. B1=B2 trên mẫu chủ yếu từ đơn không bác bỏ
tính hữu ích của B2 trên truy vấn đa từ.

## Đã thực hiện

- Cố định giao thức và mã tại 5693b21, chốt điều kiện cap tại d9b19c9 trước
  khi chạy kết quả. Toàn bộ 128 ID WANDS cũ, cùng scorer, truy vấn đầy đủ.
- Mỗi query dùng trạng thái raw và một trạng thái B2 chọn bằng hash; giữ toàn
  bộ điểm số, không bỏ token. Miền liên tục là đoạn nối hai trạng thái này.
- Nhúng đoạn vào đầu vào 3 chiều của mã RSA/JAA gốc đã vá guard 32-bit như
  đợt trước. Không thêm sửa đổi vào mã thuật toán. Nguồn/binary riêng không
  phân phối lại; upstream mirror và hashes ghi trong metadata.
- Oracle số nguyên/hữu tỉ độc lập, giữ mọi hòa điểm thứ 10. Sàng lọc an toàn
  cho cả đoạn liên tục, không chỉ hai đầu. Grid dyadic 24-bit được float32
  biểu diễn chính xác; kiểm tra riêng union gốc và union sau lượng tử hóa.
- Cả 128 ca giữ trong archive. 121 ca có oracle; 7 ca vượt cap 4 triệu cặp
  nên ghi resource_unknown và không chạy native. Không chọn lại mẫu để bù.

## Kết quả

| Chỉ số | Kết quả |
|---|---:|
| Oracle chính xác / tổng chọn | 121 / 128 |
| Đoạn thêm ứng viên so với hai đầu | 55 / 121 |
| Đoạn thêm ứng viên ngoài cả union lưới đầy đủ | 15 / 121 |
| Tổng query-document membership thêm ngoài lưới | 20 |
| Union gốc bằng union sau lượng tử hóa | 121 / 121 |
| RSA khớp oracle, giữ mọi ties | 43 / 121 |
| JAA khớp oracle, giữ mọi ties | 58 / 121 |
| Native timeout / lỗi tiến trình | 0 / 0 |
| Median wall RSA, gồm launch + R-tree | 17,78 ms |
| Median wall JAA, gồm launch + R-tree | 27,54 ms |
| Median chuẩn bị dữ liệu riêng | 4,26 ms |

RSA có 9 ca thiếu ID và 73 ca dư ID; JAA có 23 ca thiếu và 44 ca dư. Một ca
có thể vừa thiếu vừa dư. Các sai lệch này là chẩn đoán implementation/contract
trên bản mirror cụ thể, chưa phải kết luận lỗi của thuật toán công bố. Việc
exit=0 không có nghĩa đáp án chính xác. Cần giữ điều kiện ties, precision,
harness và mọi cap khi diễn giải.

Ví dụ query 196: document index 19868 (zero-based) không thuộc union đầy đủ
của mọi trạng thái B2, nhưng thuộc top-10 của đoạn tại
t=5628543/10561313. Witness và điểm nguyên trong archive cho phép kiểm tra
chính xác bằng nhân chéo, không dựa vào kết quả native.

**Claim được bổ sung:** miền liên tục có thể nới union trên dữ liệu NLP thật,
không chỉ ví dụ 3-record. **Chưa được bổ sung:** RSA/JAA chậm hơn trên cả lưới,
thất bại của thuật toán gốc về mặt lý thuyết, hoặc đã đủ novelty/Q1. Đây là
miền con 1 chiều của bao lồi, không phải đối chứng toàn bộ 6.684 trạng thái.
Không so tốc độ native ở đây với 24,39 ms cũ trên workload/host khác.

## Kiểm tra và chạy lại

Từ gốc repository, với dependencies của requirements.txt:

```bash
python -m unittest utk_adapter_study.test_adapter -v
python -m utk_adapter_study.check_archive
sha256sum --quiet -c utk_adapter_study/checksums.sha256
```

Archive checker xác minh witnesses bằng nhân chéo độc lập, kết quả native và
summary; differential test so oracle với toàn bộ arrangement của các bài nhỏ.
Receipt source-replay.json xác nhận chọn trạng thái, cả hai điểm số, canonical
index hash và mọi phép loại trừ trên toàn corpus đã được replay đủ 128 ca.
Recompute receipt vào đường dẫn mới để không ghi đè bằng chứng:

```bash
python -m utk_adapter_study.replay --data /path/to/wands --output /tmp/new-replay.json
```

Chạy lại native chỉ khi có bản build riêng khớp metadata; runner từ chối ghi đè:

```bash
python -m utk_adapter_study.run --data /path/to/wands \
  --binary /path/to/private/UTK_source --source /path/to/private/source \
  --qhull-bin /path/to/qhull/bin --output /tmp/new-utk-results \
  --work /tmp/new-utk-work
```

Nguồn WANDS và license giữ nguyên như lazy_cert_study/sources.json. Artifact
chỉ thêm scores, IDs, descriptors, witnesses và execution output; không thêm
corpus text, nguồn/binary bên thứ ba hay main.tex/references.bib.
