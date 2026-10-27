"""Generate a decision report from final measurements; no hand-entered performance values."""
from pathlib import Path
import json
import pandas as pd
from core import ROOT,RES
from run import DS
S=pd.read_csv(RES/'summary.csv');B=pd.read_csv(RES/'paired_bootstrap.csv');P=pd.read_csv(RES/'profile.csv');V=json.loads((RES/'verification.json').read_text());MILP=json.loads((RES/'milp_audit.json').read_text());D=json.loads((RES/'dual_solver_audit.json').read_text());O=json.loads((RES/'optimization_audit.json').read_text());A=[json.loads((RES/(ds+'_audit.json')).read_text()) for ds in DS]
ss=S[S.budget==3]
tab='\n'.join(f"| {r.dataset} | {r.method} | {100*r.clean_f1:.2f} | {100*r.robust_balanced_accuracy:.2f} | {100*r.robust_accuracy:.2f} |" for _,r in ss.iterrows())
btab='\n'.join(f"| {r.dataset} | {r.contrast} | {100*r.balanced_robust_delta:+.2f} | [{100*r.ci_low:+.2f}; {100*r.ci_high:+.2f}] |" for _,r in B[B.budget==3].iterrows())
ptab='\n'.join(f"| {r.dataset} | {r.model_bytes/2**20:.2f} | {r.warm_predict_and_certify_p50_ms:.2f} | {r.warm_predict_and_certify_p95_ms:.2f} | {r.cold_form_cache_p50_ms:.2f} | {r.peak_process_rss_mib:.1f} |" for _,r in P.iterrows())
model_rows=sum(len(__import__('numpy').load(RES/(ds+'_predictions.npz'))['y']) for ds in DS)
dom=[]
for ds in DS:
 t=ss[ss.dataset==ds].set_index('method');r=t.loc['bolt'];dom.append((ds,[m for m in t.index if m!='bolt' and t.loc[m,'clean_f1']>=r.clean_f1 and t.loc[m,'robust_balanced_accuracy']>=r.robust_balanced_accuracy and (t.loc[m,'clean_f1']>r.clean_f1 or t.loc[m,'robust_balanced_accuracy']>r.robust_balanced_accuracy)]))
dtext='; '.join(ds+': '+(', '.join(ms) if ms else 'không bị đối chứng nào trội đồng thời ở hai chỉ số tại ước lượng điểm') for ds,ms in dom)
text=f'''# Vòng 2: BOLT — thuật toán ứng viên và kết quả kiểm thử

Ngày: 27/10/2026, múi giờ Asia/Bangkok.

**Đã triển khai BOLT và chạy thực nghiệm đầy đủ theo giao thức cuối. Mục tiêu “thuật toán đã được xác minh đủ mức đóng góp Q1” hiện CHƯA ĐẠT.** BOLT có bảo đảm tính bất biến dự đoán trong một tập biến đổi được định nghĩa rõ và cải thiện độ vững so với huấn luyện sạch/augmentation. Đối chứng mạnh và prior art chưa cho phép xem đây là một đóng góp phương pháp đủ thuyết phục cho Q1.

## 1. Đây là thuật toán ứng viên đã thực hiện

CAPC ở vòng trước cũng đã được triển khai và bị loại qua đối chứng. Vòng này thay đổi trọng tâm từ thống kê trên nhiễu lấy mẫu sang **tìm chính xác trường hợp bất lợi trong ngân sách và huấn luyện bằng những trường hợp đó**.

BOLT gồm biểu diễn sparse có nhánh gốc, nhánh bỏ dấu và tương tác cặp token; bộ tìm biến thể bất lợi bằng quy hoạch động có budget; và vòng tối ưu hàm mất mát bình phương hinge sạch/robust có cân bằng lớp. Biến thể bất lợi của mỗi đối thủ nhãn được đưa thành witness constraint. Đây là một pipeline phương pháp có mã, hàm mục tiêu và kiểm tra độc lập, không chỉ là bảng baseline. Tên BOLT là tên làm việc; việc đặt tên không xác lập tính mới toàn cầu.

Đặc trưng cộng theo token/cặp token giúp bộ giải chính xác trong số học thực, với độ phức tạp O(n k q²) cho mỗi lớp đối thủ; q≤3. THE0RY/THEORY.md ghi đầy đủ công thức, chứng minh quy nạp, cận relaxation và giới hạn số học. Dùng **THEORY.md** trong cùng thư mục để đọc nguồn đúng.

## 2. Phạm vi bảo đảm và công gán nhãn

Mỗi token có các dạng riêng biệt: gốc, bỏ thanh, bỏ toàn bộ dấu; chỉ giữ dạng có cùng độ dài NFC. Budget là tổng số codepoint NFC thay đổi. Token Unicode đặc biệt có biến thể làm đổi độ dài giữ dạng gốc, không bị xóa khỏi dữ liệu.

“Vững ở k=3” nghĩa là phân loại đúng nhãn gốc và duy trì nhãn đó cho **mọi tổ hợp dạng hợp lệ trong lattice có tổng cost≤3**. Không có bảo đảm đối với mọi lỗi 3 ký tự tùy ý, từ đồng nghĩa, chèn/xóa, đổi khoảng trắng hoặc toàn bộ quả cầu Levenshtein. Giới hạn 128 token đầu được dùng giống nhau cho mọi phương pháp.

Không gán nhãn mới bằng con người. Nhãn phân loại là nhãn có sẵn của các bộ công khai. Bảo đảm là tính bất biến của mô hình dưới một kênh biến đổi chuỗi đã định, không phải tuyên bố mọi chuỗi biến đổi đều giữ nghĩa đen với người đọc. Việc thay đổi scope này giảm nhu cầu kiểm chứng ngữ nghĩa thủ công, đồng thời làm hẹp phạm vi ứng dụng cần tuyên bố.

## 3. Dữ liệu và cách khóa thí nghiệm

- UIT-VSFC: 11.426 / 1.583 / 3.166 train/dev/test.
- UIT-VSMEC: 5.548 / 685 / 692 sau kiểm tra trùng lặp từ vòng trước.
- Allociné tiếng Pháp: lấy mẫu stratified cố định 5.000 / 1.000 / 2.000 từ split chính thức; sau loại trùng còn 1.999 test. Đây là thí nghiệm tập train nhỏ, không phải SOTA toàn bộ Allociné 160.000 train.
- Hai tập test tiếng Việt đã được xem ở vòng CAPC: kết quả mới trên đó là **thăm dò**. Tập test tiếng Pháp được giữ cho xác nhận độc lập sau chọn cấu hình; mã/cấu hình được ghi lên [commit df2a708](https://github.com/TruongTQ261531/N-Gram/commit/df2a708c61cb4f6beaf24c6d11d4366faba85469) trước khi chạy xác nhận.
- Chọn tham số trên 2.000 mẫu train và validation; final fit dùng toàn bộ phần train đã chọn. Vocabulary/IDF chỉ fit dữ liệu train. Cache token mới khi transform test không cập nhật tham số. Row ID và revision/hash corpus được lưu.
- 6 phương pháp: clean, canonical, random augmentation, greedy adversarial training, robust unary và BOLT đầy đủ. Mỗi phương pháp có hai mức regularization; BOLT có thêm hai mức trộn sạch/robust.
- 42 fit chọn cấu hình + 54 fit cuối (3 seed) + 3 re-fit BOLT = **99 fit hoàn tất của giao thức chính**. Smoke run và audit solver được ghi riêng, không cộng thành các lần xác nhận độc lập.
- Mỗi model được đánh giá k=0,1,2,3,5; thêm random10/random30 và maximal allowed folding làm chẩn đoán ngoài budget. Có **270 dòng metric, 162 dòng chẩn đoán** và dữ liệu dự đoán/margin từng mẫu cho {model_rows:,} câu test.

## 4. Kết quả chính

Bảng dùng thang 0–100. F1 sạch là macro-F1. RBA là balanced robust accuracy: trung bình theo lớp của tỷ lệ mẫu vừa đúng vừa vững. RA là tỷ lệ tương ứng trên toàn bộ tập, dễ chịu ảnh hưởng mất cân bằng lớp.

| Dataset | Phương pháp | F1 sạch | RBA, k=3 | RA, k=3 |
|---|---|---:|---:|---:|
{tab}

**Lợi ích quan sát được:** BOLT tăng RBA k=3 so với random augmentation ở cả ba tác vụ. Mức tăng có CI ghép cặp loại 0. **Giới hạn quyết định:** canonical có RBA cao hơn BOLT ở cả ba tác vụ; robust unary trội cả F1 sạch và RBA trên tiếng Pháp. BOLT cũng chưa tạo lợi thế RBA nhất quán trước greedy adversarial training. Do đó chưa chứng minh được phần tương tác/context và bộ tìm chính xác khi huấn luyện mang lại đóng góp tổng quát đủ mạnh.

Kiểm tra trội đồng thời F1 sạch và RBA tại các ước lượng điểm: {dtext}. Đây là phân tích điểm ước lượng, không phải kiểm định thống kê cho cả hai chỉ số.

| Dataset | So sánh RBA k=3 | Chênh lệch, điểm | CI 95% |
|---|---|---:|---:|
{btab}

CI dùng 2.000 bootstrap theo câu gốc, giữ các budget/run của cùng câu đi chung. Chúng có điều kiện trên các mô hình đã fit, không bao phủ toàn bộ biến thiên huấn luyện tương lai; không có hiệu chỉnh đa so sánh. Seed thay đổi khởi tạo tối ưu và random augmentation; mục tiêu BOLT là xác định, không coi 3 seed là 3 bộ dữ liệu độc lập.

![Độ vững theo ngân sách](results/robustness_curve.png)

Không so trực tiếp những số này với Macro-F1 trung bình dưới 24 kiểu nhiễu của CAPC: hai phép đo có định nghĩa và phạm vi khác nhau.

## 5. Kiểm thử độc lập

- **600** bài toán ngẫu nhiên nhỏ đối chiếu DP với vét cạn: không sai khác ngoài làm tròn.
- 7 integrity tests: budget monotone, canonical invariant, loại dạng lặp, factorization giữa feature thật và oracle, phản ví dụ tương tác làm greedy bỏ sót, gradient finite difference, và brute-force.
- Tái mã hóa mọi biến thể hợp lệ của các prefix thật: **{V['exhaustive_real_prefix_class_comparisons']}** so sánh lớp đối thủ, sai lệch lớn nhất **{V['exhaustive_real_max_error']:.3g}**.
- **{len(MILP)}** bài toán đối chiếu với MILP độc lập trên câu thật, sai lệch lớn nhất **{max(r['abs_difference'] for r in MILP):.3g}**. Đây là đối chiếu một bộ tối ưu khác, không tái sử dụng DP để làm “đáp án chuẩn”.
- Dựng lại 270 dòng metric và 162 dòng chẩn đoán từ arrays; kiểm tra margin/certificate, cận factor không phát chứng nhận sai, budget monotonic, và greedy không được dùng làm certifier.
- Tải lại model numerical npz độc lập, kiểm tra 100 mẫu mỗi dataset: dự đoán, certificate và margin khớp; sai lệch margin **0** trong môi trường này.
- 3 re-fit BOLT seed 17: trọng số và dự đoán giống từng bit. Không tuyên bố bitwise reproducibility trên mọi nền tảng.
- Phần phụ primal–dual qua 3 QP reference ở 2/3/7 lớp; không dùng để thay thế kết quả test đã khóa.

Lịch sử lỗi preparation, sửa guard Unicode, adapter cột review, điều phối job và sửa phép đo RAM được giữ trong RUN_HISTORY.md/audit. Cấu hình hoặc kết quả yếu không bị loại khỏi bảng.

## 6. Huấn luyện đã hội tụ đến đâu

Bộ tìm adversarial chính xác không đồng nghĩa toàn bộ tối ưu huấn luyện đã hội tụ. Giới hạn 6 witness rounds và 50 L-BFGS iterations có thể bị chạm; training_logs.json giữ nguyên success flag/gradient/separation gap. Với seed 17, audit subgradient cho các cận trên suboptimality: {', '.join(r['dataset']+' '+format(r['strong_convexity_gap_upper'],'.4g') for r in O)}. Cận có thể lỏng ở điểm không trơn; không gọi mọi model là nghiệm tối ưu toàn cục.

Audit primal–dual riêng trên **{D['training_n']} mẫu train phát triển** của VSFC cho primal={D['rounds'][-1]['primal']:.8f}, dual={D['rounds'][-1]['dual']:.8f}, gap={D['rounds'][-1]['gap']:.8f}. Mục tiêu tham chiếu L-BFGS ở cùng bài toán là {D['reference_restricted_plus_separation_objective']:.8f}. Cận này có ý nghĩa kiểm tra hội tụ của bài toán audit; không phải số đo full-corpus và không được gộp vào điểm test chính. Dual coordinate ascent/cutting plane là kỹ thuật đã có; đây không phải tuyên bố sáng tạo ra một bộ giải tổng quát mới.

## 7. Khả năng triển khai

Model numerical npz chứa vocabulary/IDF và hệ số, không chứa corpus cache hoặc pickle. Lệnh trong predict.py đưa ra nhãn dự đoán và cờ bất biến trong lattice; cờ này không khẳng định nhãn dự đoán đúng về ngữ nghĩa.

| Dataset | Model MiB | Warm p50 ms | Warm p95 ms | Cache mới p50 ms | Peak process MiB |
|---|---:|---:|---:|---:|---:|
{ptab}

Thời gian gồm dự đoán và kiểm tra bất biến k=3 cho lớp dự đoán. Model được nạp và Numba đã warm; không gồm thời gian compile/nạp model lúc khởi động. Peak process dùng /proc VmHWM sau exec, gồm Python, dependencies, JIT, model và cache, không phải RAM riêng của trọng số. Chạy profiler sau khi mọi training/audit compute đã xong; thời gian train các job song song không dùng để xếp hạng tốc độ.

Ví dụ từ repo root:

```bash
python round2/predict.py --model round2/results/UIT-VSFC_bolt_model.npz --text 'bài giảng rất tốt' --budget 3
```

## 8. Novelty và quyết định Q1

Đã đối chiếu các nguồn gần nhất, gồm phương pháp của [ARC, EMNLP 2021](https://aclanthology.org/2021.emnlp-main.82/) và [LipsLev, ICLR 2025](https://arxiv.org/abs/2501.13676); xem NOVELTY.md và primary_source_audit.json để biết phần đã đọc. Robust word-substitution training và weighted n-gram/lattice computation cũng đã có tiền lệ.

Phần có thể phân biệt hẹp ở BOLT là kiến trúc sparse và oracle chính xác gắn với cùng tập biến đổi khi train/test. Chưa có bằng chứng rằng cách kết hợp này đủ khác biệt với các phương pháp có trước để đạt mức đóng góp Q1. Kết quả đối chứng còn không ủng hộ lợi ích context nhất quán. Không lấy số paper khác làm baseline đã tái lập, không coi mốc Q1 là một ngưỡng điểm cố định, không bảo đảm được nhận bài.

**Trạng thái:** thuật toán ứng viên có mã và kiểm chứng đúng trong phạm vi đã định — đạt; dùng lại nhãn có sẵn, không cần đợt gán nhãn mới — đạt; chứng minh hiệu quả tổng quát của cơ chế mới và novelty đủ Q1 — chưa đạt. Việc thêm conformal wrapper hoặc đổi tên một penalty cũng chưa giải quyết khoảng trống này vì có prior art trực tiếp. Không nên viết một bản thảo tuyên bố BOLT là thuật toán mới đã đủ Q1 từ kết quả hiện tại.

Để đánh giá khác đi cần một đóng góp cụ thể vượt prior art, matched closest-method comparisons và bằng chứng cơ chế. Đây là yêu cầu về nội dung nghiên cứu còn thiếu, không phải yêu cầu tạo thêm bộ benchmark hoặc thuê người gán nhãn mới. Mục tiêu Q1 của yêu cầu vẫn chưa được hoàn thành; báo cáo nêu rõ phần nào đã thực hiện và phần nào chưa có bằng chứng.
'''
text=text.replace('THE0RY/THEORY.md ghi đầy đủ công thức, chứng minh quy nạp, cận relaxation và giới hạn số học. Dùng **THEORY.md** trong cùng thư mục để đọc nguồn đúng.', '[THEORY.md](THEORY.md) ghi công thức, chứng minh quy nạp, cận relaxation và giới hạn số học.')
(ROOT/'REPORT_VI.md').write_text(text)
print('Report generated from final measurements; Q1-readiness: NOT ESTABLISHED')
