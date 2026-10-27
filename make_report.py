"""Generate the Vietnamese decision report directly from recorded measurements."""
from pathlib import Path
import json,re
import pandas as pd
from study import ROOT,RES,DATASETS
S=pd.read_csv(RES/'summary.csv');B=pd.read_csv(RES/'paired_bootstrap.csv');E=pd.read_csv(RES/'isolated_efficiency.csv');Q=pd.read_csv(RES/'solver_audit.csv')
audit=json.loads((RES/'data_audit.json').read_text());verify=json.loads((RES/'verification.json').read_text())
rows=[]
for _,r in S.iterrows():
 rows.append(f"| {r.dataset} | {r.method} | {100*r.clean_f1:.2f} | {100*r.noise_mean_f1:.2f} | {100*r.heldout_family_mean_f1:.2f} | {100*r.fullfold_f1:.2f} |")
table='\n'.join(rows)
contrasts='\n'.join(f"| {r.dataset} | {r.contrast} | {100*r.delta:+.2f} | [{100*r.ci_low:+.2f}, {100*r.ci_high:+.2f}] |" for _,r in B.iterrows())
profiles='\n'.join(f"| {r.dataset} | {r.method} | {r.batch1_p50_ms:.3f} | {r.batch1_p95_ms:.3f} | {r.peak_process_rss_mib:.1f} | {r.serialized_bytes/2**20:.2f} | {r.batch_throughput_docs_s:.0f} |" for _,r in E[E.method.isin(['svm','aug','capc'])].iterrows())
passed=True
for ds in DATASETS:
 ss=S[S.dataset==ds].set_index('method');bb=B[B.dataset==ds].set_index('contrast')
 passed &= all(bb.loc['capc - '+x,'ci_low']>0 for x in ['aug','uniform'])
 passed &= ss.loc['capc','clean_f1']>=ss.loc['char','clean_f1']-.01
verdict='PASS sàng lọc thực nghiệm; vẫn chưa đủ kết luận Q1' if passed else 'NO-GO cho CAPC hiện tại: chưa đủ bằng chứng đóng góp để xây bài Q1'
maxres=Q.relative_normal_equation_residual.max();hit=Q.hit_max_iter.any()
text=f'''# Báo cáo khả thi: n-gram tiếng Việt dưới nhiễu và kiểm tra novelty

Ngày tra cứu/chạy: 27/10/2026, múi giờ người dùng Asia/Bangkok.

**Kết luận: {verdict}.**

Đã triển khai và chạy một ứng viên thuật toán, đối chiếu nghiên cứu gần đây và kiểm thử thực tế. Báo cáo này là kết quả sàng lọc có thể kiểm chứng; không phải bản thảo đã đủ điều kiện được nhận ở tạp chí Q1. Không có cách trung thực để bảo đảm một thuật toán chưa đánh giá là mới, hữu ích trong mọi bối cảnh hoặc chắc chắn được nhận.

## 1. Đề tài nên giữ và khoảng trống cần chứng minh

Tài liệu đầu vào đề xuất so sánh mô hình phân loại tiếng Việt sạch/nhiễu. Phần “Task 1” trong file được xem là bối cảnh, không phải yêu cầu bắt buộc ghi đè yêu cầu nghiên cứu mới. Để phù hợp mục tiêu triển khai nhanh, vòng này chuyển trọng tâm sang bộ phân loại n-gram chạy CPU, có đối chứng cơ chế.

Các nghiên cứu gần nhất làm giảm novelty của một benchmark thuần túy:

- **22/10/2026:** [How Well Do Decision Models Transfer to Vietnamese?](https://arxiv.org/abs/2610.31422) đã khảo sát nhiều tác vụ và nhiễu teencode/lỗi gõ/bỏ dấu. Bối cảnh zero-shot khác vòng supervised này, nhưng ý tưởng “thêm nhiễu rồi so sánh mô hình tiếng Việt” đã rất đông.
- **2025–2026:** [ViSoLex](https://aclanthology.org/2025.coling-demos.18/) và [ViGoEmotions](https://aclanthology.org/2026.eacl-long.129/) cho thấy normalization và cách xử lý emoji đã được nghiên cứu. Chỉ thêm tiền xử lý không đủ thành một phương pháp mới.
- **2026:** [FLUKE](https://aclanthology.org/2026.findings-eacl.269/) và [MulTypo](https://aclanthology.org/2026.acl-long.729/) hướng tới nhiễu có cơ sở ngôn ngữ, phụ thuộc tác vụ và kiểm tra tính hợp lệ. Một bộ thay ký tự tùy ý chỉ là stress test.
- **Tháng 10/2026:** [One Meaning, Many Romanizations](https://aclanthology.org/2026.mrl-1.29/) đã nghiên cứu selective stability: co các cách viết tương đương nhưng giữ khác biệt ngữ nghĩa. Ý tưởng bất biến có chọn lọc cần được đối chiếu trực tiếp, không thể nhận là ý tưởng hoàn toàn mới.

Hướng có thể nghiên cứu tiếp là **giữ bằng chứng ngữ nghĩa khi chuẩn hóa, đồng thời chịu được mất dấu trên CPU**. Đây là giả thuyết nghiên cứu cần thêm bằng chứng. Chi tiết 12 công trình và giới hạn tra cứu nằm ở RELATED_WORK.md. Đã đọc các trang/abstract liên quan và một số nội dung HTML; chưa thực hiện systematic review toàn diện hay tái lập mọi công trình.

## 2. Thuật toán đã thực sự triển khai

Tên ứng viên: **CAPC — Collision-Aware Paired Consistency**; tên làm việc, chưa xác minh tính mới toàn cầu.

1. TF-IDF character n-gram độ dài 2–5, tối đa 30.000 feature, fit trên train gốc và phiên bản train bỏ dấu.
2. Huấn luyện ridge đa lớp trên ba view mỗi mẫu: gốc, bỏ dấu hoàn toàn và một bản nhiễu ngẫu nhiên. Có cân bằng lớp.
3. Thêm penalty bình phương giữa điểm dự đoán của bản gốc và bản bỏ dấu.
4. Giảm penalty ở các mẫu có tín hiệu nhập nhằng: trọng số r=exp(-4 max JSD) từ phân phối nhãn của dạng có dấu và họ bỏ dấu. Thống kê được tính out-of-fold trên train, không dùng nhãn validation/test.

Penalty được triển khai bằng cách thêm hàng hiệu feature với target 0 vào bài toán ridge thưa. Với alpha>0, mục tiêu là một bài toán lồi chặt có nghiệm duy nhất về mặt toán học. Đây là tính chất tiêu chuẩn, không phải định lý mới. Không dựng nghịch đảo ma trận 30.000 × 30.000.

**Giới hạn cơ chế:** trọng số chỉ là tương quan token–nhãn, chưa chứng minh được nhập nhằng ngữ nghĩa theo ngữ cảnh. Mọi phương pháp augmentation vẫn dùng bản bỏ dấu với nhãn gốc; CAPC không loại bỏ giả định giữ nhãn đó. Hàm consistency bình phương cũng có phân rã đại số quen thuộc. Vì vậy, phần có thể đóng góp chỉ là chất lượng cơ chế trọng số và lợi ích vượt các đối chứng; kết quả bên dưới quyết định có giữ ý tưởng này không.

## 3. Giao thức và số lần chạy

- Hai bộ công khai, pin revision và SHA-256: UIT-VSFC sentiment 3 lớp; UIT-VSMEC emotion 7 lớp gồm Other.
- UIT-VSFC: train/validation/test sau kiểm tra là **11.426 / 1.583 / 3.166**. CSV validation có thêm một dòng hoàn toàn rỗng, đã loại trước huấn luyện.
- UIT-VSMEC: **5.548 / 685 / 692** sau khi loại một validation trùng train và một test lặp nội bộ. Train vẫn giữ các dòng lặp/xung đột nhãn và công khai số lượng trong data_audit.json.
- ViHSD ở nguồn được nêu trong đề cương yêu cầu chấp nhận điều kiện truy cập: **không tải/không chạy ViHSD**. Thay bằng VSMEC để vòng CPU tái lập ngay được.
- 9 phương pháp: word ridge, char ridge, char LinearSVC, folded ridge, raw+folded concat ridge, augmentation, uniform consistency, CAPC, xáo trộn trọng số CAPC.
- Chọn alpha/C/lambda chỉ trên validation với seed 17 và nhiễu seed 9001. Lưu toàn bộ search, cấu hình và hash trước đánh giá test. Khi không cấu hình nào đạt điều kiện sạch, chọn fallback đã quy định và gắn cờ rõ trong dev_search.json.
- 5 lượt seed **17, 29, 43, 71, 101**; augmentation và bản nhiễu thay đổi theo seed. Baseline tất định lặp lại để có so sánh ghép cặp; không coi đó là 5 lần huấn luyện ngẫu nhiên độc lập.
- 8 loại nhiễu: bỏ dấu từng token, sai thanh, bàn phím, xóa ký tự, đảo ký tự, lặp ký tự, nối khoảng trắng, teencode. Mỗi loại có xác suất chọn token 10/20/30%. Thêm sạch, bỏ dấu hoàn toàn và NFD: **27 điều kiện**. Token ở đây là đơn vị cách nhau bởi khoảng trắng, thường là âm tiết tiếng Việt, không phải word segmentation.
- Vòng cuối hoàn tất **48 fit chọn tham số + 90 fit đánh giá + 18 fit lặp kiểm tra = 156 fit**. Có **{verify['metric_rows']:,} dòng chỉ số** và **{verify['predictions']:,} dự đoán từng mẫu**. Số này không tính những lần thử bị hủy do lỗi generator.
- CI dùng **2.000 bootstrap theo câu gốc**, giữ chung tất cả view và run của cùng câu. Không dùng từng ô nhiễu như một mẫu độc lập. CI có điều kiện trên các mô hình/generator đã chạy, không bao phủ mọi lần huấn luyện tương lai; đây là phân tích chẩn đoán, không có hiệu chỉnh đa so sánh.

Một bản đầu có lỗi ánh xạ bàn phím về chính ký tự nguồn. Đã dừng, lưu code/log/đầu ra còn có vào audit/superseded_keyboard_v0, sửa map và kiểm tra đủ 26 chữ cái, rồi chạy lại toàn bộ selection và test. **Bản lỗi không đi vào kết quả cuối.** Xem RUN_CORRECTIONS.md. Commit khóa code/cấu hình trước phân tích test: [98c99a5](https://github.com/TruongTQ261531/N-Gram/commit/98c99a51536fda6b5da4ef90e1ef06af8c499b89). Commit được tạo khi test đang chạy, không được trình bày là đăng ký trước độc lập trước mọi tính toán.

## 4. Kết quả toàn bộ phương pháp

Macro-F1 quy đổi về thang 0–100. “Nhiễu” là trung bình 24 ô × 5 lượt; không gồm sạch/fullfold/NFD. “Họ chưa thấy” gồm sai thanh, xóa, đảo, nối khoảng trắng; các họ này không dùng trong augmentation/validation. Việc có họ nhiễu chưa thấy không đồng nghĩa đã chứng minh tổng quát hóa sang lỗi người dùng thật.

| Dataset | Phương pháp | Sạch | Nhiễu TB | Họ chưa thấy TB | Bỏ dấu toàn bộ |
|---|---|---:|---:|---:|---:|
{table}

Độ lệch chuẩn giữa các run, CI từng phương pháp, accuracy và F1 từng lớp nằm trong summary.csv / metrics.csv / family_summary.csv. Biểu đồ dưới đây dùng CI bootstrap theo câu, có điều kiện trên các run đã fit.

![Macro-F1 dưới nhiễu tổng hợp](results/robustness.png)

Chênh lệch CAPC với đối chứng, đơn vị **điểm F1**; baseline mạnh nhất được chọn bằng validation, không dùng test để chọn đối thủ:

| Dataset | So sánh | Chênh lệch | CI 95% |
|---|---|---:|---:|
{contrasts}

Điều kiện go/no-go nội bộ yêu cầu lợi thế trước augmentation và uniform ở cả hai tác vụ, không giảm sạch quá 1 điểm so với char ridge; đây là tiêu chí sàng lọc của dự án, không phải tiêu chuẩn chung của tạp chí. Báo cáo này kiểm tra thêm CI có loại được 0 hay không. Kết quả quyết định: **{verdict}**. Lợi thế trước một baseline yếu hơn không chứng minh được cơ chế mới; đối chứng xáo trộn đặc biệt quan trọng.

## 5. Kiểm thử, độ tin cậy số liệu và hiệu suất

- 12 kiểm tra integrity: p=0, seed, Unicode, idempotence bỏ dấu, toàn bộ map bàn phím, split không trùng, vocabulary chỉ fit train, cận trọng số, nghiệm ridge trên hệ nhỏ, phân rã đại số consistency và generator thực sự thay đổi đầu vào.
- 18 lần re-fit seed 17 kiểm tra dự đoán sạch giống từng bit trong cùng môi trường.
- verify_results.py dựng lại độc lập toàn bộ {verify['metric_rows']:,} dòng F1/accuracy/per-class từ arrays, không gọi lại hàm metric của pipeline. Đồng thời kiểm tra hash cấu hình/giao thức đã khóa và checksum artifact.
- NFD phải có dự đoán giống sạch ở mọi run/phương pháp; đây là kiểm tra normalization, không phải một thành tích robustness.
- Kiểm tra bỏ thêm test có canonical key trùng train được báo trong fold_overlap_sensitivity.csv; VSFC có 10 key test bỏ dấu trùng train. Chưa kiểm tra mọi near-duplicate, nguồn người viết hay leakage theo thời gian vì metadata không đủ.
- Kiểm tra solver trên dữ liệu thật seed 17: residual phương trình chuẩn tương đối lớn nhất **{maxres:.3g}**; có chạm giới hạn iteration: **{bool(hit)}**. Đo cho ridge; SVM chỉ ghi số iteration. Không gọi đây là chứng nhận số học tuyệt đối.

Đo bổ sung mỗi mô hình trong process riêng sau khi training kết thúc: batch=1 gồm normalize + TF-IDF + predict, 450 phép đo; throughput batch 512 lặp 5 lần. CPU một thread; hardware.json ghi CPU được container nhìn thấy. Bảng dưới là một phần, file isolated_efficiency.csv có đủ 18 model–dataset:

| Dataset | Model | p50 ms | p95 ms | Peak process MiB | Artifact MiB | Batch docs/s |
|---|---|---:|---:|---:|---:|---:|
{profiles}

Peak process RSS gồm Python, thư viện, dữ liệu, model và working set, **không phải bộ nhớ riêng của trọng số model**. Fit time trong efficiency.csv chưa gồm vectorization/augmentation dùng chung. Số đo không đại diện cho mọi độ dài văn bản hay phần cứng; không so tốc độ với Transformer chưa chạy.

## 6. Đánh giá mức đóng góp cho Q1

**Chưa đủ để nộp như một bài phương pháp mới đã được xác thực.** Các thành phần chính đã có tiền lệ; không thể dùng số lượng điều kiện test để thay thế novelty. Hai bộ dữ liệu cũ với nhiễu tổng hợp cũng chưa xác thực lợi ích trên lỗi người dùng thật. Kiểm tra số học và tái lập có thể làm đầy đủ cho giao thức này, còn tính giữ nghĩa/giữ nhãn cần bằng chứng độc lập.

Các phần chưa làm: PhoBERT/ViSoBERT/fastText matched baselines; ViSoLex normalization baseline; benchmark nhiễu thật được người Việt kiểm tra; contrast set nhập nhằng được gán nhãn độc lập; thêm miền/ngôn ngữ nếu tuyên bố tổng quát; power analysis và đánh giá cuối trên dữ liệu chưa từng dùng. Không mượn số paper khác để thay cho các lần chạy này.

Scope nên giữ nhỏ: phân loại CPU dưới mất dấu/biến thể chính tả, chuyển từ trọng số token–nhãn sang cơ chế ngữ cảnh giữ được khác biệt ngữ nghĩa. NEXT_STUDY.md có thiết kế đối chứng, ví dụ kế hoạch audit 400 cặp với hai annotator và nguyên tắc dừng. Con số 400 là kế hoạch ban đầu, chưa phải bảo đảm power. [ViLexNorm](https://aclanthology.org/2024.eacl-long.85/) có thể cung cấp cặp chuẩn hóa thật; nhãn chuẩn hóa không tự trở thành nhãn sentiment/emotion.

Có thể xét scope của Expert Systems with Applications nếu xây được một hệ thống thực dụng và cơ chế thuyết phục; hoặc Information Processing & Management nếu có đóng góp xử lý/truy hồi thông tin phù hợp. Chưa xác minh trực tiếp bảng JCR/Scimago chính thức; nguồn đại học hiển thị Q1/2025 được ghi trong RELATED_WORK.md và phải đối chiếu hệ xếp hạng/năm/ngành mà đơn vị của bạn yêu cầu. Không có cam kết được nhận hay thời hạn hoàn thành một bài Q1.

## 7. Bằng chứng bàn giao

- Mã nguồn, requirements pin phiên bản, download manifest + hash và lệnh tái lập trong README.md.
- Giao thức, toàn bộ search, cấu hình khóa và audit dữ liệu.
- Tất cả metric, dự đoán từng mẫu, bootstrap và phép đo hiệu suất; log hoàn tất và lịch sử sửa lỗi.
- Mã tự dựng lại chỉ số và kiểm tra checksum.
- Không đưa văn bản dataset, file Word gốc hoặc checkpoint lên repo; nguồn dữ liệu có CC BY-NC-SA 4.0 theo các dataset card. Xem results/DATA_LICENSE.md.

Repo: https://github.com/TruongTQ261531/N-Gram ; branch research/vietnamese-noise-audit-2026-10-27. Kết quả được bàn giao bằng pull request để xem xét, chưa merge main.
'''
(ROOT/'REPORT_VI.md').write_text(text)
print(verdict)
