"""Build the bilingual research report directly from frozen-stage evidence."""
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

Phần còn thiếu trước khi chốt nộp: (1) phản biện novelty/toán và mã bởi người có chuyên môn, đặc biệt gần CostCert và verification rời rạc; (2) chứng minh giá trị triển khai cho truy hồi thật, thêm kiểm tra với dữ liệu lỗi tự nhiên có sẵn hoặc ngôn ngữ khác nếu claim mở rộng; (3) đánh giá quy mô lớn hơn nếu claim production; (4) xác minh scope/quartile đúng năm, hoàn thiện tác giả và yêu cầu tạp chí. Không cần một đợt gán nhãn mới để làm ba việc đầu ở scope hiện tại. Có bản thảo tiếng Anh từ các kết quả đã chạy ở MANUSCRIPT.md, chưa nộp hoặc xác nhận sẵn sàng nộp.

## Bằng chứng và tái lập

`python round3/verify_archive.py` kiểm chứng bản phát hành mà không tải corpus. `checksums.sha256`, hai freeze, khóa kết quả lượt đầu, ID/độ giao input, toàn bộ CSV, JSONL.gz, NPZ, log và fixture đi kèm. Raw corpus/index/Word không công bố. Đọc DATA_LICENSE.md và RUN_HISTORY.md. CI xanh xác nhận các check đã thiết kế, không xác nhận originality hay quyết định của tạp chí.
'''
 for key,value in {'PRIMARY':primary_t,'REPLICATION':rep_t,'VERDICT':verdict,'USEFUL':useful,'QUALITY':q_t,'ABLATION':ab_t,'MECHANISM':mechanism_t,'LATENCY':lat_t}.items():report=report.replace('@'+key+'@',value)
 (ROOT/'REPORT_VI.md').write_text(report)
 english='''# Discrete Shared-Query Certificates for Character n-Gram Retrieval

Research manuscript draft, 29 October 2026. Authors/affiliations and target journal have not been assigned. This document has not been submitted or peer reviewed. Originality and Q1 suitability remain unconfirmed.

## Abstract

An unchanged lexical ranker can be stable under many input variants even when independent pairwise bounds cannot certify its output. We study retention of the clean winner within top-K when one shared, discretely edited query scores an entire corpus. For a fixed character-n-gram BM25 index, we combine safe corpus-wide screening, an affine shared-query relaxation and discrete incompatibility covers. Pairwise exclusions use a support test or capped Pareto dynamic programming; resource exhaustion weakens the bound rather than authorizing a certificate. A generic additive-factor construction separates discrete covers from the matched convex relaxation. Experiments use full SciFact, NFCorpus and FiQA corpora, an initial 300-query confirmation and a separately preregistered 970-query replication. Exact pairwise bounds, feasible enumeration, generic LP and time-limited MILP provide matched controls. We release frozen protocols, per-query bounds, numerical witnesses, 27,000 individual sampled predictions and statistical verifiers. The certificate concerns a finite text-edit model and conservative tie ranking; it does not improve the underlying relevance ranker or establish semantic preservation. Results and statistical limitations are reported by stage.

## 1. Motivation and related work

Top-K certification, common-input robustness and relaxed safety properties are established. CertDR and RobustMask certify neural document-ranking defenses, while randomized-smoothing work derives top-K classifier guarantees. CostCert explicitly identifies the inflation caused by independent pairwise use of a shared attacker budget. We therefore make no novelty claim for that motivation or for top-K containment. Our setting fixes an additive lexical scorer and asks how tightly one can bound a target document's rank over finite shared query states without smoothing or fitting a new model.

Current work also includes calibrated candidate pruning, exact geometric exclusion with rounding certificates, conformal multimodal retrieval decisions and domain contamination control. These have different guarantees and assumptions; their published percentages are not compatible baselines for our threat model. N-gram generative retrieval diagnostics and personalized-query benchmarks motivate practical robustness, but our experiments do not certify generation quality or semantic equivalence. See RELATED_WORK_UPDATE.md and bibliography.bib for sources and inspection depth. The specialization remains subject to a broader conflict-graph/disjunctive-verification prior-art review.

## 2. Problem definition

Let W(d,g) be stored nonnegative float64 BM25 weights, treated as exact real parameters. Normalize text by NFC, casefold and whitespace; retain at most the first 32 query tokens. A token contributes within-token character grams of lengths 3, 4 and 5 with boundary spaces. Every original token i has finite alternatives A_i, with raw state zero. Alternatives consist of all single deletions, adjacent transpositions, repeated-character insertions and QWERTY-neighbor substitutions, deduplicated. The allowed query state a changes at most B original tokens. The SAME a is used to score all documents.

For the clean winner r, define d_j(a)=sum_i[f_i(a_i,j)-f_i(a_i,r)]. Its conservative worst-tie rank is 1+sum_j 1[d_j(a)>=0]. A rank upper bound at most K certifies retention for every allowed state and any deterministic tie-breaking. This property is neither strict invariance of the entire top-K set nor a relevance/semantic claim.

## 3. Certificate construction

First bound each document score using featurewise maximum permitted query counts and nonnegative index weights. Bound the reference score below by an exact token-budget oracle. Discard a competitor only when its upper score is strictly below the reference lower score. This examines the full corpus; there is no hidden candidate cutoff. If an allowed state zeros the reference, nonnegativity makes worst-tie rank N attainable and solver work is unnecessary.

For every remaining competitor, exact pairwise maximization takes the B largest nonnegative token gains relative to the raw state. Remove competitors whose maximum margin is negative. Counting the rest gives a valid pairwise upper bound, but different competitors may require incompatible shared edits.

For valid L_j<0 and 0<=w_j<=1/(-L_j), the inequality 1[d_j>=0]<=1+w_j*d_j gives a count bound m+max_a sum_j w_j*d_j(a). The support maximum uses the same token-budget oracle. A cutting-plane master searches for good feasible weights; its restricted optimum is a LOWER bound on the best relaxation, not the robustness certificate. Every reported bound is re-evaluated through the conservative support oracle. A generic compact primal LP over token-state distributions and expected edit budget solves the equivalent relaxation as a mandatory matched comparator.

Next prove that selected competitor pairs cannot simultaneously have nonnegative margins. A negative midpoint support suffices; otherwise a two-coordinate Pareto DP enumerates nondominated upper margin sums by token and edit cost. Dominated points may be discarded because every continuation preserves coordinatewise dominance. Resource limits return unknown and create no incompatibility edge. Partition all possible competitors into pairwise-incompatible groups. At most one member per group can be promoted, so the number of groups bounds the count. Take the best valid LP, cover and feasible exhaustive-enumeration bound.

**Soundness.** Safe screening retains every potentially promoted competitor; outward margin bounds contain its real score; a verified incompatibility edge rules out simultaneous promotion; each returned clique group contributes at most one. Taking minima of independently valid bounds preserves validity. See THEORY.md for the detailed derivation and numerical assumptions.

**Separation.** A single token has M edited states; state k gives competitor k margin 1 and all others -1/(M-1), while raw margins are -1. At most one competitor is promoted discretely, but the uniform fractional mixture makes every expected margin zero, allowing the LP to count M. A complete discrete cover counts one. Nonnegative additive scores realize these factors after adding a common reference offset. This proves a gap for the general factor family, not a new general LP theorem or a physical realization by every fixed BM25/keyboard collection. General additive worst-count maximization contains budgeted maximum coverage; the concrete implementation is conservative and resource bounded.

## 4. Experimental design

Pinned public BEIR mirrors provide all 5,183/3,633/57,638 corpus documents. No qrels fit the index or guide the certificate. Existing original-query judgments are evaluation context only; no fresh human or LLM labeling is used. Parameters are fixed at k1=1.2, b=.75; K=1/5/10/20/50 and B=1/2/3 are reported for primary confirmation, with K=10 primary.

The original 300 test IDs and predictor source were public at commit 8dd7972 before evaluation. Development selected winner retention after a failed strict-set pilot, which remains archived. Primary B2 gains over best LP+enumeration were +5/+4/+5 points, with insufficient exact paired evidence after the original Holm-18 correction. After observing this, B2/K10 was selected for a NEW independent-query replication, preregistered at 5fcf816. All eligible untouched official test inputs were used, with prior input/text overlap and new duplicates excluded, yielding 199/223/548 queries. We do not pool the two stages to rescue significance. Reusing corpora limits claims to new queries on these fixed indexes.

The matched controls are exact pairwise plus feasible enumeration, the best custom/generic same-formulation LP plus enumeration, and a generic numerical MILP with a one-second solver limit and explicit matrix caps/statuses. All methods share ordinary transpose caching. The candidate uses at most 40 cuts, 120 pair checks, 80 candidates for graph work, 20,000 generated DP points and a 1,000-point frontier. Enumeration is capped at 2,000 states and 2 million state-candidate cells. All skips remain visible and are not equated with attacks. The replication focuses on the selected LP/cover comparison; it does not newly claim MILP/random attacks on all 970 queries.

Use 2,000 paired query bootstrap draws and two-sided exact paired tests. Primary multiplicity is Holm-18; replication primary multiplicity is Holm-3. Confidence intervals condition on each fixed corpus/index/query sample. The statistical family and sample sizes are not changed after looking at replication outcomes.

## 5. Results

Initial confirmation, K=10, counts out of 100:

@PRIMARY@

Independent replication, B=2/K=10:

@REPLICATION@

The second table reports percentage-point differences with paired percentile intervals and Holm-adjusted exact tests; wins/losses are discordant query counts. @VERDICT@

The candidate does not dominate the generic MILP: in primary NFCorpus and FiQA B3 the MILP certifies one additional query. Finite-cut LP optimization gaps are gaps to that relaxation, not to the true worst rank. A solver timeout is not a nonrobustness witness. At B1 feasible enumeration and strong controls often remove any advantage; these zero-gain configurations are retained.

Relevance-conditioned results:

@USEFUL@

An uncertified or unjudged-relevant winner must not be conflated with a genuinely irrelevant document. Stability cannot correct a wrong clean result. Existing qrels describe the original intent and do not validate every perturbed string.

Post-hoc mechanism diagnostic:

@ABLATION@

The support-edge column reuses exactly the tested pairs from recorded runs and removes Pareto-only edges. It is not an independent support-only scheduling experiment or a new confirmation. Synthetic M=3/4/8 gap examples and exported real-query fixtures are separately identified from retrieval results.

Audit of independent-stage gain queries:

@MECHANISM@

All 32 additional certified queries have successful generic LP runs with nominal objective above the count threshold 10 by at least 1e-6; no gain relies only on a capped LP comparator. These are numerical solver objectives, not formally verified lower bounds. Thirteen gains have positive-qrel winners (4/2/7), so relevance-conditioned benefit is smaller than stability benefit. This is post-hoc descriptive mechanism analysis, with no new p-values. All cap/zero-score cases remain in the full denominator.

## 6. Verification and cost

Eighteen unit tests include 1,200 exhaustive pair-budget checks, 49 eligible enumerated LP cases out of 60 generated cases, 200 Pareto/brute-force comparisons, 25 MILP/brute-force instances and 210 high-precision interval checks. Full-corpus controlled replay matches all 300 primary rank profiles and all 300 budget-two restricted profiles. Every saved support/MIP witness and 27,000 seeded sampled queries is re-encoded. Individual state choices, observed ranks, retrieved IDs and relevance grades permit offline metric recomputation. No observed strict rank exceeds its proposed conservative upper bound. This empirical statement does not replace the mathematical certificate or prove the compiled libraries correct.

Twelve exported real-query margin fixtures support numerical solver audits; eight finite lattices are independently enumerated. Proof traces and resource outcomes are retained per replication query. Checksums, public precommits, uncompressed-result hashes and input-disjointness hashes support provenance. CI verifies the published evidence and numerical components; it does not certify originality or acceptance.

All 20 downloaded source-file byte hashes were rechecked. Rebuilding SciFact character and word indexes directly from raw data, without cache pickles, matches their frozen canonical fingerprints. This is a representation reconstruction for SciFact only, not an independent implementation or a claim of rebuilding all three indexes.

We discovered that the original confirmation initialized OpenBLAS with three threads due to import order, despite a one-thread protocol. The original evidence is preserved and concurrent times are not used for latency claims. Controlled replay initializes BLAS/HiGHS with one thread before imports and profiles sequential fresh corpus workers. First ten fixed queries per corpus receive balanced method order, warmed indexes and end-to-end B1/B2/B3 timing. Median seconds:

@LATENCY@

Startup is reported separately; primary FiQA replay peaks near 3.68 GiB. Ten timed queries with one measured pass per method are limited latency evidence, not a production speed claim. The generic MILP time includes setup/oracle work and may exceed its solver time limit. Concurrent independent-stage times are diagnostics only. Execution-only FiQA partitioning after a retained 57-query prefix is documented and source-identity checked; its fixed ID sequence and per-query computation are unchanged.

## 7. Limitations and submission status

The threat model is a finite QWERTY/token-edit lattice, not all edit-distance strings or semantic rewrites. English corpora, bounded queries, conservative ties and fixed corpus reuse limit generalization. Whole-corpus FiQA is moderate scale; no million-document or online serving result is claimed. The unchanged BM25 ranker can retrieve unjudged or wrong results. Float guarantees assume the stated IEEE-754 and sparse-dot error model; there is no mechanized proof of scipy/BLAS/HiGHS. Resource caps may yield loose but valid bounds.

The contribution is a specialized combination with demonstrated behavior, pending a dedicated closest-method review beyond IR and independent theoretical/code review. CostCert and general disjunctive/conflict-graph verification are particularly relevant novelty risks. New-corpus/language or existing natural-typo evaluation is needed before broad deployment claims. Journal scope and current quartile require primary-source verification. Statistical gains, artifacts and this draft do not establish Q1 readiness or guarantee acceptance.

## Data and code availability

Code, frozen protocols, IDs, compressed per-query records, individual prediction arrays, fixtures, CSVs, plots, execution history and offline verifiers are in this repository. Raw corpus/index/Word files are excluded; pinned upstream data are fetched for full reruns. See DATA_LICENSE.md, REPRODUCE.md, THEORY.md, NOVELTY.md, RELATED_WORK_UPDATE.md and bibliography.bib. No experiment in this round requires a GPU, paid API or new human annotation.
'''
 # Keep the manuscript fully English, including its generated statistical note.
 ev=f'{sign} of the three independently preregistered dataset comparisons pass Holm-adjusted p<.05; this supports only the specified certificate comparison, not publication readiness.'
 english=english.replace('@VERDICT@',ev)
 for key,value in {'PRIMARY':primary_t,'REPLICATION':rep_t.replace('n mới','new n').replace('Chênh lệch pp','Difference pp'),'USEFUL':useful.replace('Winner có qrel dương','Winner with positive qrel').replace('Được chứng nhận và có qrel dương','Certified and positive-qrel').replace('Tỷ lệ trên toàn bộ n','Fraction of all n'),'ABLATION':ab_t.replace('Chỉ cạnh support đã lưu','Recorded support edges only').replace('Discrete đầy đủ','Full discrete'),'MECHANISM':mechanism_t,'LATENCY':lat_t}.items():english=english.replace('@'+key+'@',value)
 (ROOT/'MANUSCRIPT.md').write_text(english)
 readme='''# Discrete shared-query certificates for n-gram retrieval

Research round 3, 29 October 2026. A working inference-time certifier for a fixed character-BM25 ranker, with full-corpus experiments, an initial 300-query confirmation and a separately preregistered 970-query replication. **Originality and Q1 readiness remain unconfirmed.** CAPC/BOLT scientific results remain unchanged; no unevaluated hybrid is claimed.

The method certifies that the original winner stays in top-K under a finite common-query token-edit model. It uses safe screening, exact pairwise margins, a matched affine LP and discrete incompatibility covers, with feasible enumeration and generic LP/MILP controls. It does not improve the underlying relevance scores. LP, DP, coloring, pruning and top-K certificates have prior art; the contribution hypothesis is this specialization and its demonstrated value.

## Complete results and interpretation

Independent B2/K10 stage (initial stage reported separately):

@REPLICATION@

@VERDICT@

Read the [Vietnamese report](REPORT_VI.md), [English manuscript draft](MANUSCRIPT.md), [theory](THEORY.md), [initial novelty audit](NOVELTY.md) and [expanded current related work](RELATED_WORK_UPDATE.md). The report includes zero-gain budgets, MILP wins, relevance-conditioned counts, numerical assumptions, a thread execution deviation and the limited isolated latency sample.

## Verify without raw data

From repository root:

```bash
pip install -r requirements-all.txt
python round3/verify_archive.py
python -m unittest discover -s round3 -p 'test_*.py'
```

Published evidence includes all selected per-query records (gzip), 27,000 individual sampled predictions, exact bootstrap draws, proof traces, 12 real-query fixtures, solver outcomes, plots, logs, source/ID freezes and checksums. All 300 primary rank profiles and budget-two adapters matched controlled full-corpus replay. These are implementation/statistical checks, not proof of every compiled library or of novelty.

## Run a new query on CPU

After downloading pinned data and building its local index as described in [REPRODUCE.md](REPRODUCE.md):

```bash
python round3/certify_query.py --dataset scifact --query 'vitamin deficiency affects bone growth' --budget 2 --k 10
```

No new labels, GPU, fitting or paid API is needed. The full corpora have 5,183/3,633/57,638 documents. Queries are limited to 32 normalized whitespace tokens; the guarantee covers only the declared finite per-token delete/swap/repeat/QWERTY model with worst-case ties. It does not certify semantic equivalence or relevance.

Cloud two-core/8 GiB execution completed these experiments. Local execution is optional for independent replication/more throughput; 16 GiB RAM gives useful margin. It does not increase language-model reasoning or automatically establish a contribution.

## Provenance

- Original source/300 IDs before metrics: [8dd7972](https://github.com/TruongTQ261531/N-Gram/commit/8dd7972dc13d85159e908f9b6ea03c394289acd2), [PROTOCOL_RETENTION.md](PROTOCOL_RETENTION.md).
- Independent source/970 fresh IDs/primary-result hashes before new metrics: [5fcf816](https://github.com/TruongTQ261531/N-Gram/commit/5fcf816da7d686427f518845c71e682d95626cee), [PROTOCOL_REPLICATION.md](PROTOCOL_REPLICATION.md). No stage pooling or significance-based stopping.
- Execution-only FiQA range adapter: [fb80e60](https://github.com/TruongTQ261531/N-Gram/commit/fb80e602df947ed12dc00d09c40e510f4e6cbe25), [EXECUTION_ADDENDUM.md](EXECUTION_ADDENDUM.md). Per-query source identity and final ID completeness checked.
- [RUN_HISTORY.md](RUN_HISTORY.md), [DATA_LICENSE.md](DATA_LICENSE.md), pinned `download_manifest.json` and `checksums.sha256`.

Raw corpus/query text, index pickles, literature full text and the uploaded Word file are excluded. Existing qrels evaluate original-query relevance only. No paper has been submitted, accepted or declared guaranteed Q1.
'''
 readme=readme.replace('@REPLICATION@',rep_t.replace('n mới','new n').replace('Chênh lệch pp','Difference pp')).replace('@VERDICT@',ev)
 (ROOT/'README.md').write_text(readme)
 print('Built REPORT_VI.md and MANUSCRIPT.md from complete separate-stage results')
if __name__=='__main__':main()
