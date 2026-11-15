"""Build only the historical Vietnamese report from frozen-stage evidence.

The maintained README and separately managed manuscript are not generated here.
"""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
def table(headers,rows):
 return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def main():
 S=pd.read_csv(R/'confirmation_summary.csv');P=pd.read_csv(R/'paired_differences.csv');T=pd.read_csv(R/'replication_summary.csv');D=pd.read_csv(R/'replication_paired.csv');L=pd.read_csv(R/'controlled_latency.csv');Q=pd.read_csv(R/'retrieval_quality.csv')
 datasets=['scifact','nfcorpus','fiqa'];primary=[];rep=[];lat=[];quality=[];ab=[]
 for ds in datasets:
  for b in [1,2,3]:
   z=S[(S.dataset==ds)&(S.budget==b)&(S.k==10)].set_index('method');primary.append([ds,b]+[int(z.loc[m,'certified']) for m in ['pair_enum','best_lp_enum','proposed','mip_enum']])
  z=T[T.dataset==ds].set_index('method');p=D[(D.dataset==ds)&(D.baseline=='best_lp_enum')].iloc[0]
  rep.append([ds,int(z.loc['proposed','queries'])]+[f"{int(z.loc[m,'certified'])} ({100*z.loc[m,'coverage']:.2f}%)" for m in ['pair_enum','best_lp_enum','proposed']]+[f"{100*p.difference:+.2f} [{100*p.ci_low:+.2f}, {100*p.ci_high:+.2f}]",f'{p.holm_primary_p:.6g}',f'{int(p.wins)}/{int(p.losses)}'])
  ll=L[L.dataset==ds].set_index('method');lat.append([ds]+[f'{ll.loc[m,"median_seconds"]:.3f}' for m in ['pair_enum','lp_enum','direct_lp_enum','proposed','mip_enum']])
  q=Q[Q.dataset==ds].iloc[0];quality.append([ds,f'{q.char_ndcg10:.4f}',f'{q.word_ndcg10:.4f}',f'{100*q.judged_relevant_winner:.0f}%'])
 A=pd.read_csv(R/'posthoc_edge_diagnostics.csv')
 for ds in datasets:
  for b in [2,3]:
   a=A[(A.dataset==ds)&(A.budget==b)];ab.append([ds,b]+[int((a[m]<=10).sum()) for m in ['best_lp_enum','recorded_support_edges_cover','proposed']])
 primary_t=table(['Corpus','B','Pair+enum /100','Best LP+enum /100','Discrete /100','MILP+enum /100'],primary)
 rep_t=table(['Corpus','n mới','Pair+enum','Best LP+enum','Discrete','Chênh lệch pp [95% CI]','p Holm (3)','Win/loss'],rep)
 lat_t=table(['Corpus','Pair+enum','Custom LP+enum','Generic LP+enum','Discrete','MILP+enum'],lat)
 q_t=table(['Corpus','Char nDCG@10','Word nDCG@10','Winner có qrel dương'],quality)
 ab_t=table(['Corpus','B','Best LP+enum','Chỉ cạnh support đã lưu','Discrete đầy đủ'],ab)
 M=pd.read_csv(R/'mechanism_summary.csv');M=M[M.stage=='independent']
 mechanism_t=table(['Corpus','Gain queries','Generic LP success on gains','Positive-qrel gain queries','Generic LP cap skips / all','Zero-score shortcuts / all'],[[z.dataset,int(z.wins),int(z.wins_generic_lp_success),int(z.positive_qrel_wins),int(z.generic_lp_cap_skips_total),int(z.zero_shortcuts)] for z in M.itertuples()])
 sign=int((D[(D.baseline=='best_lp_enum')].holm_primary_p<.05).sum())
 verdict=f'Lượt xác nhận độc lập có {sign}/3 so sánh chính đạt p Holm < 0,05. Đây là kết luận thống kê cho mục tiêu đã khóa, không phải tiêu chuẩn xác lập Q1.'
 useful=table(['Corpus','n','Winner có qrel dương','Được chứng nhận và có qrel dương','Tỷ lệ trên toàn bộ n'],[[ds,int(z.queries),int(z.judged_relevant_winners),int(z.judged_relevant_certified),f'{100*z.useful_coverage:.2f}%'] for ds in datasets for z in [T[(T.dataset==ds)&(T.method=='proposed')].iloc[0]]])
 report='''# Vòng 3: chứng nhận rời rạc cho truy hồi character n-gram

Ngày 29/10/2026. **Đã xây dựng và chạy một ứng viên thuật toán, không chỉ chạy baseline. Chưa xác lập được novelty toàn cầu hoặc bảo đảm đủ Q1.** Đây là hướng chứng nhận khi suy luận; CAPC/BOLT là hai nghiên cứu trước và không bị đổi kết quả hay ghép thành một mô hình lai chưa kiểm thử.

## Vấn đề và thuật toán thực sự làm gì

Giữ nguyên character-BM25. Với truy vấn gốc, lấy tài liệu đứng đầu r. Tìm một cận trên của thứ hạng tệ nhất của r khi cùng một truy vấn bị sửa được dùng chấm điểm mọi tài liệu. Nếu cận không quá 10, r chắc chắn còn trong top-10 trong mô hình nhiễu đã định. **Tăng tỷ lệ chứng nhận không có nghĩa tăng accuracy, recall hay nDCG của bộ xếp hạng.**

Pipeline: (1) sàng lọc an toàn trên toàn corpus; (2) cực đại margin chính xác cho từng cặp; (3) LP dùng chung lựa chọn sửa truy vấn; (4) kiểm tra hai đối thủ không thể cùng vượt r bằng support/Pareto DP; (5) phân hoạch các đối thủ xung đột để chặn số tài liệu cùng vượt; (6) lấy cận tốt nhất cùng liệt kê chính xác khi lattice nhỏ. Có LP tổng quát và MILP tổng quát làm đối chứng trên cùng bài toán. Các kỹ thuật LP, DP, coloring, BM25 và pruning đã có từ trước.

Sự khác biệt cần bảo vệ nằm ở bộ chứng nhận cụ thể cho các lựa chọn text-edit rời rạc được dùng chung trên corpus, và lợi ích sau khi so với các đối chứng mạnh. [THEORY.md](THEORY.md) chứng minh tính an toàn có điều kiện, đưa một họ additive-factor có khoảng cách LP/cover tăng theo số trạng thái, và chỉ ra độ khó ở họ tổng quát. Không suy diễn rằng định lý này là phát hiện đầu tiên hoặc mọi họ đó đều hiện thực được bằng corpus BM25/QWERTY hiện tại.

## Phạm vi được kiểm chứng

- Corpus đầy đủ: SciFact 5.183, NFCorpus 3.633, FiQA 57.638 tài liệu. Không cắt ngầm top-100. Giữ các ID chính thức kể cả nội dung tài liệu trùng.
- Character gram 3/4/5 trong token; BM25 k1=1,2, b=0,75. Tối đa 32 token đầu sau chuẩn hóa NFC/casefold/whitespace. Đây không phải báo cáo BEIR SOTA với mọi truy vấn nguyên vẹn.
- Mỗi token gốc được giữ nguyên hoặc sửa đúng một lần: xóa ký tự, đảo hai ký tự liền nhau, lặp ký tự hoặc thay bằng phím QWERTY kề. Tối đa B token gốc bị sửa. Không bao gồm mọi chuỗi trong bóng Levenshtein, đổi dấu tiếng Việt, mọi typo tự nhiên, synonym hoặc bảo toàn nghĩa.
- Ties được tính theo hướng bất lợi cho r. Nếu một sửa đổi cho điểm r bằng 0, mọi điểm đều không âm nên trả cận N; không loại các truy vấn khó/OOV này khỏi mẫu.
- Chỉ dùng qrels công khai có sẵn để đánh giá. Không gán nhãn mới bằng người hoặc LLM, không huấn luyện thêm, không cần GPU/API trả phí.

## Khóa trước kết quả và xác nhận độc lập

Pilot yêu cầu giữ nguyên cả tập top-10 cho tỷ lệ chứng nhận bằng 0 trên 40 truy vấn development. Pilot được giữ ở `audit/set_invariance_screen_v0/`. Đổi mục tiêu sang giữ winner trong top-K dựa trên development, trước khi chạy confirmation.

Mã/cấu hình và 100 test ID mỗi corpus được công bố tại [8dd7972](https://github.com/TruongTQ261531/N-Gram/commit/8dd7972dc13d85159e908f9b6ea03c394289acd2), trước metric test. Kết quả 300 truy vấn của lượt này được giữ nguyên. Mức tăng B2 là 5/4/5 điểm phần trăm so với best LP+enum nhưng chưa đủ bằng chứng exact paired sau điều chỉnh 18 so sánh chính. Không dùng bootstrap CI để che kết quả exact test đó.

Sau khi xem lượt đầu, chọn giả thuyết B=2, K=10 và best LP+enum để xác nhận trên dữ liệu mới. [5fcf816](https://github.com/TruongTQ261531/N-Gram/commit/5fcf816da7d686427f518845c71e682d95626cee) công bố protocol, hash kết quả cũ và toàn bộ 970 ID mới **trước metric mới**. Loại ID/chuỗi hiệu dụng đã đánh giá và chuỗi trùng: còn 199/223/548 truy vấn. Hai lượt báo cáo riêng, không gộp để làm p-value đẹp hơn, không dừng theo p-value. Xác nhận mới dùng lại corpus, nên không phải kiểm tra tổng quát hóa sang corpus/ngôn ngữ mới.

FiQA được chia lịch chạy sau khi hai corpus nhỏ hoàn tất: giữ 57 dòng đầy đủ, chạy hai đoạn không giao nhau [57,302), [302,548), rồi ghép đúng thứ tự ID đã khóa. Mã tính mỗi truy vấn được đối chiếu nguyên văn với driver khóa. [fb80e60](https://github.com/TruongTQ261531/N-Gram/commit/fb80e602df947ed12dc00d09c40e510f4e6cbe25) công bố thay đổi lịch chạy trước các đoạn đó; log SIGINT và mọi phần kết quả được giữ. Không thay đổi thuật toán, tham số, mẫu hay phép kiểm định.

## Kết quả lượt đầu: cả các cấu hình không có lợi

@PRIMARY@

K=10; mỗi ô là số được chứng nhận trên 100. Enumeration được dùng cho mọi baseline khi trong cap, nên không quy công cho phương pháp ở trường hợp brute force đã giải được. MILP có giới hạn solver 1 giây và cap ma trận 2 triệu entries; status, dual bound, skip và timeout được công bố. Timeout không đồng nghĩa có tấn công thành công. MILP tốt hơn phương pháp đề xuất ở NFCorpus/FiQA B3; không có tuyên bố thắng mọi đối chứng.

## Kết quả xác nhận độc lập: B=2, K=10

@REPLICATION@

@VERDICT@

CI bootstrap cặp theo truy vấn, 2.000 lần; p exact paired hai phía và Holm trên ba so sánh chính mới. CI điều kiện theo corpus/index và tập truy vấn cố định; không phải khoảng bất định của mọi hệ thống NLP. Đối chiếu pair+enum là mô tả bổ sung, không mở rộng family để chọn p có lợi. Xem toàn bộ số liệu ở `results/replication_*.csv`, không chỉ bảng thuận lợi.

## Tính hữu ích và giới hạn về relevance

@USEFUL@

Winner được giữ lại có thể sai hoặc không có qrel dương. “Không có qrel dương” không nhất thiết là người đã phán không liên quan vì qrels có thể không đầy đủ. Các tỷ lệ hữu ích ở trên yêu cầu qrel dương; không đánh đồng ổn định với đúng. Nhãn của truy vấn gốc cũng không chứng minh truy vấn sau sửa giữ nguyên nghĩa.

Hiệu quả xếp hạng sạch ở 300 truy vấn lượt đầu:

@QUALITY@

Đây là bối cảnh của scorer, không phải lợi ích do bộ chứng nhận tạo ra. Không tuyên bố character-BM25 vượt word-BM25 trên mọi corpus.

## Phần rời rạc đóng góp thêm ở đâu

@ABLATION@

Phân tích hậu kiểm, mỗi cấu hình 100 truy vấn lượt đầu. Cột support-only tái dùng **đúng các cặp đã kiểm tra/lưu**, bỏ cạnh chỉ Pareto chứng minh rồi phân hoạch lại; không phải một scheduler support-only đã chạy độc lập. Các số này mô tả cơ chế, không phải phép xác nhận mới. Họ chẩn đoán tổng quát M=3/4/8 có exact count=1, LP=M, discrete cover=1; đây là additive factors, không được trình bày như corpus BM25 thực.

Kiểm tra riêng các truy vấn tăng thêm ở lượt độc lập:

@MECHANISM@

Cả 32 truy vấn tăng thêm đều có generic LP giải thành công và objective số lớn hơn ngưỡng count=10 ít nhất 1e-6; không có gain nào chỉ do baseline bị cap. Đây là đối chiếu numerical LP, không phải lower bound đã được chứng minh cơ học. Trong 32 gain có 13 winner với qrel dương (4/2/7); lợi ích relevance thực tế nhỏ hơn lợi ích ổn định. Mọi cap/zero shortcut vẫn trong mẫu. Không tạo phép kiểm định mới từ phân tích cơ chế hậu kiểm này.

## Kiểm thử, đối chiếu và bằng chứng có thể kiểm tra

18 unit test đã qua: 1.200 đối chiếu margin-budget với liệt kê độc lập; 49 trường hợp LP đủ điều kiện trong 60 trường hợp ngẫu nhiên sinh ra; 200 kiểm tra Pareto với brute force; 25 MILP với brute force; 210 dot-product intervals với Decimal 80 chữ số; kiểm tra sàng lọc, phân rã scorer, ties và cap không được tạo chứng nhận sai. Mọi trường hợp bỏ qua được nêu thay vì tính như đã giải.

300 truy vấn lượt đầu được chạy lại với một luồng BLAS: 300/300 cận rank khớp; adapter B2 cũng khớp 300/300. Re-encode đầy đủ các witness và 27.000 mẫu nhiễu (3 seed × 3 budget × 10 mẫu × 300 truy vấn) trên toàn corpus, không thấy rank quan sát vượt cận. Lưu choice từng token, rank, top document ID và relevance grade trong NPZ để tái tính metric. Không coi 27.000 phép thử là bằng chứng vét hết mọi biến thể.

Kiểm tra lại hash của đủ 20 tệp nguồn tải về. Dựng lại cả index character/word SciFact trực tiếp từ dữ liệu, không dùng pickle cache, cho fingerprint canonical trùng bản đã khóa. Không gọi đây là dựng lại cả ba corpus; kết quả và mã chạy ở `results/index_rebuild.json`/`index_rebuild.py`.

12 ma trận truy vấn thật được xuất làm fixture; tám lattice nhỏ được liệt kê độc lập và đối chiếu LP/MILP. Các lượt mới lưu từng cận, LP weights/lịch sử, cạnh/nhóm xung đột, solver outcomes và witness được re-encode. Verifier ngoại tuyến tái tính metric, CI, exact p/Holm, thứ tự/đủ ID, hash input không giao, nguồn khóa và checksum. Kiểm tra cấu trúc artifact không thay thế chứng minh compiled code hay chạy lại trên corpus.

Float guarantee giả định IEEE-754 float64 và mô hình sai số sparse/BLAS đã nêu; có khoảng sai số hướng ra ngoài và guard số. Không có chứng minh cơ học của scipy/BLAS/HiGHS. Chi tiết và hạn chế ở THEORY.md.

## Thời gian và tài nguyên thực tế

Phát hiện vòng confirmation gốc import numpy trước thiết lập biến luồng nên OpenBLAS dùng ba luồng; HiGHS vẫn một luồng. Đây là sai lệch thực thi đã lưu ở `audit/threading_observation.json`. Không dùng thời gian chạy đồng thời đó để tuyên bố tốc độ. Sau đó replay và profile riêng, xác nhận BLAS/HiGHS một luồng, scorer/thuật toán giữ nguyên.

Median giây/truy vấn, gồm toàn pipeline B1/B2/B3, index đã warm, 10 truy vấn đầu đã khóa mỗi corpus, thứ tự phương pháp cân bằng:

@LATENCY@

Đo một lượt mỗi phương pháp trên 10 truy vấn không đủ để khẳng định phân bố latency sản xuất hay speedup phổ quát. Các phương pháp dùng chung tối ưu cache transpose thông thường; không quy nó thành novelty. Có startup load/transpose riêng và VmHWM từng process; replay FiQA đạt khoảng 3,68 GiB. Không gọi giới hạn 1 giây solver là tổng wall time của MILP.

Cloud hai lõi/8 GiB đã chạy được. **Bạn chưa cần chạy local để hoàn thành các kết quả này.** Máy local RAM 16 GiB trở lên có thể chạy tái lập độc lập/nhanh hơn; không làm tăng khả năng suy luận của mô hình hoặc tự tạo novelty. Chạy tuần tự nếu RAM ít; hướng dẫn từng bước ở REPRODUCE.md.

## Đánh giá so với mục tiêu Q1

Đã khắc phục việc chỉ có baseline/benchmark: có ứng viên thuật toán chạy được, phân tích lý thuyết, đối chứng mạnh cùng bài toán, xác nhận mới được khóa trước, dự đoán từng mẫu, log và kiểm chứng công khai. Mức tăng ở bảng là tăng khả năng chứng nhận của scorer cố định.

**Chưa được gọi là đã đạt Q1.** CostCert đã có ý tưởng tránh phóng đại ngân sách ở top-K; CertDR/RobustMask và chứng nhận top-K bằng smoothing đã có từ trước; pruning, LP, conflict graph và DP cũng không mới. Novelty cần đánh giá ở chuyên biệt hóa/thuật toán cụ thể và giá trị thực tế, không ở tên phương pháp. Đã bổ sung nguồn đến tháng 10/2026; bảng so sánh và mức độ đọc ở RELATED_WORK_UPDATE.md. Chưa có rà soát hệ thống đầy đủ ngoài IR hoặc phản biện độc lập để loại trừ thuật toán tương đương.

Phần còn thiếu trước khi chốt nộp: (1) phản biện novelty/toán và mã bởi người có chuyên môn, đặc biệt gần CostCert và verification rời rạc; (2) chứng minh giá trị triển khai cho truy hồi thật, thêm kiểm tra với dữ liệu lỗi tự nhiên có sẵn hoặc ngôn ngữ khác nếu claim mở rộng; (3) đánh giá quy mô lớn hơn nếu claim production; (4) xác minh scope/quartile đúng năm, hoàn thiện tác giả và yêu cầu tạp chí. Không cần một đợt gán nhãn mới để làm ba việc đầu ở scope hiện tại. Bản thảo được quản lý riêng ngoài repository; báo cáo này ghi lại giai đoạn lịch sử của vòng 3.

## Bằng chứng và tái lập

`python round3/verify_archive.py` kiểm chứng bản phát hành mà không tải corpus. `checksums.sha256`, hai freeze, khóa kết quả lượt đầu, ID/độ giao input, toàn bộ CSV, JSONL.gz, NPZ, log và fixture đi kèm. Raw corpus/index/Word không công bố. Đọc DATA_LICENSE.md và RUN_HISTORY.md. CI xanh xác nhận các check đã thiết kế, không xác nhận originality hay quyết định của tạp chí.
'''
 for key,value in {'PRIMARY':primary_t,'REPLICATION':rep_t,'VERDICT':verdict,'USEFUL':useful,'QUALITY':q_t,'ABLATION':ab_t,'MECHANISM':mechanism_t,'LATENCY':lat_t}.items():report=report.replace('@'+key+'@',value)
 (ROOT/'REPORT_VI.md').write_text(report)
 print('Built historical REPORT_VI.md; maintained READMEs and manuscript files are not generated')
if __name__=='__main__':main()
