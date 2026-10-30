# Tổng kiểm kê project N-Gram và tiến độ hướng tới paper Q1

Ngày30/10/2026, Asia/Bangkok. Bản nền main:94a9f0c16ab2bd312621682cb842fb9b439deabe. Lượt nghiên cứu tiếp theo nằm riêng trên branch `research/rank-equivalence-2026-10-30`; không gộp vào main, không thay đổi website đang phục vụ. Các mục bên dưới phân biệt công việc đã hoàn tất với giả thuyết hoặc mục tiêu chưa có đủ bằng chứng. Không dùng phần trăm hoàn thành giả định hay coi CI xanh là chứng nhận novelty/Q1.

## 1. Mục tiêu và yêu cầu ban đầu

Từ tài liệu N-gram tiếng Việt, người dùng yêu cầu tìm hướng có đóng góp đủ mạnh cho tạp chí Q1, triển khai nhanh/dễ trên tài nguyên sẵn có, được phép đổi scope và không chỉ xây benchmark. Thuật toán phải thực sự có mã, chạy nhiều lần, có đối chứng và kết quả minh bạch. Sau đó bổ sung hạn chế công gán nhãn thủ công, đóng góp ứng dụng/dataset, triển khai web và lưu mã/kết quả trên GitHub.

**Đã hoàn tất nhiều vòng phương pháp và kiểm toán; mục tiêu xác lập novelty đủ Q1 và sẵn sàng nộp vẫn chưa hoàn thành.** Đóng góp hiện có mạnh nhất là bộ chứng nhận truy hồi dùng chung truy vấn, các bằng chứng thực nghiệm cụ thể, công cụ web và bộ oracle có thể kiểm tra. Việc bổ sung nhiều thành phần chưa tự tạo thành một thuật toán mới hoặc paper được nhận.

## 2. Bảng công việc theo yêu cầu

| Mã | Hạng mục yêu cầu | Đã làm và bằng chứng | Trạng thái thực chất | Đóng góp còn thiếu |
|---|---|---|---|---|
| R01 | Phân tích đề cương, điều chỉnh scope | Từ phân loại tiếng Việt sang huấn luyện robust, rồi chứng nhận/truy hồi có ứng dụng; giao thức riêng từng vòng | Hoàn tất các quyết định scope đã thực hiện | Chốt một luận đề paper cuối cùng, phù hợp kết quả thay vì ghép mọi vòng |
| R02 | Tra cứu hướng mới và novelty | Các báo cáo RELATED_WORK/NOVELTY, nguồn chính và mức độ đã đọc; tìm thấy ARC/LipsLev, CertDR, CostCert, UTK, fuzzy caching và các công cụ counterfactual | Có rà soát theo mục tiêu, đã nêu nguồn làm giảm novelty | Chưa loại trừ thuật toán tương đương trên toàn bộ IR/verification/optimization; chưa có phản biện độc lập |
| R03 | Một phương pháp mới thay vì baseline | CAPC, BOLT, chứng nhận rời rạc và reusable-pool đều có mã, mục tiêu, đối chứng, kiểm tra cơ chế | Hoàn tất triển khai các ứng viên; không xác nhận chúng mới toàn cầu | Lợi ích của cơ chế riêng phải vượt đối chứng gần nhất và có khác biệt phương pháp đáng kể |
| R04 | Chạy nhiều lần, không tạo kết quả giả | CAPC156 fit, BOLT99 fit; retrieval300+970 query; synthetic288case; pool512case; lưu log, predictions/factors và lỗi/sửa lỗi | Hoàn tất các giao thức công bố trước lượt mới | Lặp thời gian/seed không phải dữ liệu xác nhận độc lập; cần đúng phạm vi khi diễn giải |
| R05 | Kiểm thử đầy đủ, số liệu xác thực | Verifier độc lập, brute force/DP/LP/MILP/Decimal, source hash, oracle từng trạng thái, re-encode, witness, checksum/CI | Có bằng chứng sâu cho các đối tượng đã định nghĩa | Không phải formal proof mọi compiled library; không bao phủ mọi typo/ý nghĩa/người dùng |
| R06 | Hạn chế nhãn người kiểm chứng | Dùng nhãn công khai có sẵn ở phân loại/relevance; các audit mới dùng nhãn tính toán,0 đợt nhãn mới bằng người/LLM | Đạt trong các lượt hiện tại | Oracle thứ hạng không thay nhãn liên quan, bảo toàn nghĩa hoặc chất lượng RAG |
| R07 | Baseline mạnh và kết quả âm | Uniform/shuffled/greedy/unary/canonical; LP/MILP+enum; root intervals/dominance/fixed splits; giữ cap/timeout/no-go | Hoàn tất các đối chiếu đã công bố | Chưa chạy nguyên bản mọi thuật toán gần nhất, đặc biệt UTK RSA/JAA; không gọi là thắng những phương pháp chưa chạy |
| R08 | Giá trị ứng dụng | CLI chứng nhận, web local-worker EN/VI, import/export, witness, finite-error channels, reusable top-k cache và invalidation | Đã triển khai; Site đang hoạt động owner-private | Cần lợi ích toàn phiên sử dụng, kênh lỗi và workload đại diện; không suy ra production latency từ demo |
| R09 | Dataset có đóng góp | Audit48 tài liệu/48 seed EN/VI/12family;288case/334815states; audit dẫn xuất ArguAna/SciDocs với512case và full integer factors/oracle | Artifact kiểm toán có thể tái lập đã công bố | Chưa là dataset lỗi tự nhiên hay dữ liệu tự thu thập mới; novelty dataset và tính đại diện còn thiếu |
| R10 | Tái lập và truy xuất từng kết quả | Source pins, query IDs, freeze commits, per-sample arrays, all-state traces, source replay, licenses và hướng dẫn | Hoàn tất bản công bố main hiện tại;6CI đạt tại94a9f0c | Cần phản biện/reproduction bên ngoài; mọi rerun sau khi xem test phải được gọi đúng loại |
| R11 | GitHub và tổ chức phiên bản | Mã các vòng cùng repo; lịch sử cũ đã hợp nhất; main là bản công bố nền; lượt này là branch mới riêng | Đạt yêu cầu quản lý phiên bản hiện tại | Không có pipeline hybrid CAPC+BOLT+retrieval đã huấn luyện/đánh giá; việc gộp source không chứng minh hiệu quả hybrid |
| R12 | Bản thảo và nộp tạp chí | Có bản thảo tiếng Anh vòng3 và các báo cáo, lý thuyết, bibliography, reproduction | Bản thảo ứng viên đã có; chưa sẵn sàng nộp | Chốt claim cuối, closest-method review, tác giả, journal scope/quartile đúng năm, yêu cầu nộp; chưa nộp/được nhận |
| R13 | Cải thiện chi phí và độ chặt còn thiếu | Lượt branch mới: compiled bounds, exact projected unions, gộp hiệu ứng thứ hạng, truy vấn mới nguyên câu, đo phiên20request có initialization | Xem kết quả thực tế ở [báo cáo lượt mới](exact_pool_study/REPORT_VI.md) | Lợi ích phải được quy đúng thành phần; có thể vẫn chưa tạo khác biệt novelty đủ mạnh |

## 3. Vòng1 — CAPC: đã thực sự làm gì

**Bài toán:** phân loại tiếng Việt trên CPU khi chuỗi bị nhiễu tổng hợp. CAPC dùng character TF-IDF, ridge nhiều view, consistency giữa bản gốc/bỏ dấu và trọng số từ thống kê nhập nhằng out-of-fold trên train.

Hoàn tất9 phương pháp,5 seed,27 điều kiện trên UIT-VSFC/UIT-VSMEC. Có48 fit chọn tham số,90 fit đánh giá,18 fit lặp =156 fit;2430 dòng metric và4687470 dự đoán từng mẫu. Tuning dựa validation, kiểm tra split/Unicode/normalization/vocabulary train-only, nghiệm solver và bootstrap theo câu gốc. Một lỗi generator bàn phím đã được mô tả trong audit, sửa và chạy lại giao thức; backup bản lỗi giữ cục bộ, không trộn vào gói kết quả cuối. Commit mã/cấu hình vòng này được tạo khi test đang chạy, không được gọi là preregistration trước mọi tính toán.

**Kết quả quyết định:** CAPC chưa vượt augmentation/uniform/shuffled một cách thuyết phục, và kém char-SVM trên một đối chiếu chính. Chưa chứng minh cơ chế trọng số có tác dụng riêng. **NO-GO cho CAPC như phương pháp paper Q1 hiện tại.** Đóng góp của vòng này là pipeline và bài học đối chứng/đánh giá, không phải một kết quả phương pháp tích cực đã được xác nhận.

[Báo cáo đầy đủ](REPORT_VI.md), [giao thức](PROTOCOL.md), [sửa lỗi](RUN_CORRECTIONS.md), [metric/predictions](results/), [rà soát trước](RELATED_WORK.md).

## 4. Vòng2 — BOLT: oracle và huấn luyện robust

**Bài toán:** mô hình sparse với nhánh gốc/bỏ dấu và tương tác cặp token; oracle DP tìm biến thể bất lợi chính xác trong lattice; training dùng witness constraints. Cost ở đây đếm codepoint NFC thay đổi, khác budget đếm token ở các vòng retrieval.

Hoàn tất42 fit chọn cấu hình,54 fit cuối với3seed và3 re-fit =99 fit. Có270 dòng metric/162 dòng chẩn đoán trên5857 câu test. Tiếng Việt đã xem ở CAPC được gọi là thăm dò; Allociné-FR dùng mẫu train nhỏ và test giữ riêng cho xác nhận sau khóa. Đối chứng canonical, greedy adversarial, robust unary và random augmentation đều được chạy.

**Kết quả:** RBA k3 của BOLT cao hơn random augmentation trên cả ba tác vụ, nhưng canonical có RBA cao hơn trên cả ba; unary trội cả F1 sạch/RBA ở tiếng Pháp. Chưa có lợi thế context hoặc exact-training nhất quán trước greedy. Oracle chính xác không đồng nghĩa training đã đạt tối ưu toàn cục: cap L-BFGS/witness rounds và khoảng suboptimality đã được báo.

Kiểm tra gồm600 DP-vét cạn,180 so sánh biến thể prefix thật,45 MILP độc lập, tái dựng metric, load model/re-fit, primal-dual audit và profiler. **Chưa đủ bằng chứng phương pháp cho Q1.** Đóng góp là oracle có phạm vi bảo đảm rõ và triển khai CPU tái lập, kèm kết quả âm của cơ chế được đề xuất.

[Báo cáo](round2/REPORT_VI.md), [lý thuyết](round2/THEORY.md), [giao thức](round2/PROTOCOL.md), [novelty](round2/NOVELTY.md), [mã/kết quả](round2/).

## 5. Vòng3 — Chứng nhận truy hồi dùng chung truy vấn

**Bài toán:** giữ tài liệu winner gốc trong top-K khi mọi tài liệu cùng nhận một truy vấn bị sửa, dưới scorer character-BM25 cố định. Có pairwise screening, shared-query LP, incompatibility support/Pareto, cover rời rạc, enumeration và generic LP/MILP làm đối chứng. Đây là bộ chứng nhận cho ranker cố định; không huấn luyện ranker mới.

Pilot giữ nguyên cả tập top10 cho0/40development nên mục tiêu đó đã được đổi trước confirmation. Sau đó chạy300 truy vấn xác nhận ban đầu, rồi970 truy vấn mới được khóa ID/giả thuyết trước metric; hai giai đoạn giữ riêng. Các corpus đầy đủ là SciFact5183, NFCorpus3633 và FiQA57638 tài liệu, tối đa32token truy vấn. Không cắt ngầm top100 tài liệu.

| Corpus | n mới | Best LP+enum | Rời rạc | p paired sau Holm |
|---|---:|---:|---:|---:|
| SciFact |199|115|123|0,015625|
| NFCorpus |223|41|45|0,125|
| FiQA |548|71|91|0,000005722|

Kết quả B2/K10 hỗ trợ một lợi ích chứng nhận cụ thể ở2/3corpus; NFCorpus chưa đạt ngưỡng thống kê. Cả32gain có generic LP giải thành công, nhưng chỉ13winner tăng thêm có qrel dương. MILP tốt hơn ứng viên ở một số cấu hình B3. Không diễn giải ổn định thứ hạng thành relevance, answer quality hay tốc độ hơn mọi đối chứng.

Có18unit test, LP/MILP/DP/Decimal checks,12fixture thật,27000 dự đoán nhiễu từng mẫu và300/300cận khớp khi replay một luồng. Đã kiểm tra20sourcehash và dựng lại index SciFact từ byte gốc. Sai lệch OpenBLAS3thread của lượt đầu được công khai và profile/replay riêng một luồng; không dùng thời gian đó để tuyên bố speedup. Lý thuyết có guard/assumptions và họ additive-factor; chưa chứng minh formal compiled code hoặc global firstness của định lý.

**Đóng góp mạnh nhất tới hiện tại:** bộ chứng nhận cụ thể, lý thuyết có điều kiện, đối chứng cùng bài toán và xác nhận mới minh bạch. **Nút thắt:** overlap CostCert/top-K verification/LP/DP/graph cover và giá trị triển khai còn hạn chế. [Báo cáo](round3/REPORT_VI.md), [theory](round3/THEORY.md), [manuscript](round3/MANUSCRIPT.md), [novelty](round3/RELATED_WORK_UPDATE.md), [lịch sử](round3/RUN_HISTORY.md).

## 6. Ứng dụng web và audit dataset v0.1

Đã triển khai [N-Gram Lab](https://ngram-research-lab-tq261531.tealrook33.chatgpt.site), quyền hiện tại chỉ chủ sở hữu. Tính trong Web Worker; nhập JSON/JSONL/CSV; query EN/VI; bộ lỗi keyboard/curated/accents/mixed; budget0/1/2; cận pair/cover/oracle; witness replay; tạo batch; xuất corpus/trọng số/proof/dataset có nguồn. Không có API nhận nội dung corpus/query, không thu nội dung người dùng để tạo dataset. Giới hạn500tài liệu/500000ký tự và16querytoken được báo/kiểm tra, không cắt ngầm.

Scorer trọng số nguyên web có định danh khác scorer float64 vòng3. Corpus mẫu tự biên soạn48tài liệu/48seed EN-VI/12family. Có288case,334815state, independent Python arbitrary-precision score/rank/conflict checks;0vi phạm cận. Cover cải thiện17case, mỗi case một tài liệu; **không tăng acceptance tại cap1/5/10/20 đã định trước**. Có2identity lattice được giữ nguyên, không gọi là robustness rộng.

**Đóng góp:** công cụ hoạt động, computational ground truth và provenance có thể tải/kiểm tra. **Thiếu:** bộ này nhỏ/dễ/tổng hợp, không phải natural query logs; web/adaptiveK/counterfactual UI/typo dataset đã có prior art. Corpus CC0 và phần codespell-derived CC BY-SA3.0 được phân biệt. User corpus giữ quyền riêng, không tự được cấp phép lại.

[Báo cáo](application_study/REPORT_VI.md), [giao thức](application_study/PROTOCOL.md), [nguồn/novelty](application_study/RELATED_WORK.md), [mã web](webapp/).

## 7. Bộ đệm bao phủ mọi kết quả top-k và audit văn bản mới

Đã bổ sung target khác với reference-retention: pool chứa mọi tài liệu có thể vào top-k dưới đúng lattice; replay trong subset vẫn dùng trọng số gốc. Web kiểm tra membership và từ chối hash/corpus cũ; export mang scope/proof.

Lượt đã công bố ở main dùng128query trên ArguAna8674+SciDocs25657tài liệu,512cấu hình B1/2,k5/10. Dùng16token đầu nên64/64ArguAna và3/64SciDocs bị cắt. Oracle tính đủ98023cấu hình token tại B2;103013lượt state-budget; độc lập kiểm tra97964788điểm token-document,0thiếu kết quả oracle. Mọi factor, top-k trace, cap và trường hợp heuristic kém fixed split đều công bố.

| B2/k10 | Cận từng cặp | Pool chia miền | Hợp chính xác | Hòa vốn trung vị dự phóng |
|---|---:|---:|---:|---:|
| ArguAna |139,16|72,97|27,77|45lần sửa|
| SciDocs |305,75|135,08|37,16|35lần sửa|

Giảm47,56%/55,82%số tài liệu so với đối chứng coupled; chưa hòa vốn trong20lần sửa ở cấu hình này. Thời gian cũ dựa microbenchmark thành phần, không phải whole-session đo trực tiếp; browser QA có chạy ngắn cùng giai đoạn nên không coi là timing cách ly sản xuất. Thuật toán UTK đã có possible-top-k/dominance/partition, TASTIER đã có fuzzy caching; chưa chứng minh mới đủ Q1.

**Đóng góp dataset:** bộ audit dẫn xuất có set-valued oracle trên văn bản kế thừa thật, không phải corpus tự thu thập hoặc natural typo logs. Nguồn pin/hashes và CC BY-SA4.0 ghi rõ; không có qrels/nhãn người mới. [Báo cáo](pool_study/REPORT_VI.md), [lý thuyết](pool_study/THEORY.md), [kết quả](pool_study/results/), [novelty](pool_study/RELATED_WORK.md).

## 8. Lượt branch mới cải thiện phần nào

Hướng mới có ba phần tách đối chứng: (1) cache các cận budget để giảm tính lại; (2) exact union sau sàng lọc toàn corpus an toàn; (3) gộp phép sửa có cùng hiệu ứng thứ hạng và vị trí token có cùng lựa chọn, giữ multiplicity/budget. Closure bằng witness áp dụng giống nhau cho các phương pháp exact, không quy riêng cho ứng viên.

Giao thức chọn32query mới và code được đẩy lên branch trước metric. Lần này giữ nguyên toàn query; có query ArguAna351token. Đo actual20-request sessions có chi phí initialization,3repeat cân bằng; xác minh độc lập raw projected oracle, group coverage, every saved quotient state và witness toàn corpus. Những phần này trực tiếp xử lý pool lỏng, initialization đắt, truncation và phép đo thời gian cũ. Kết quả, cap và hạn chế thực tế ở [exact_pool_study/REPORT_VI.md](exact_pool_study/REPORT_VI.md); không xem kết quả development hoặc tên thuật toán là bằng chứng novelty.

## 9. Đánh giá sẵn sàng paper

| Điều kiện | Hiện trạng |
|---|---|
| Có mã/ứng viên thực sự chạy được | Đạt nhiều vòng, không chỉ bảng baseline |
| Có bằng chứng và kết quả âm minh bạch | Đã công bố đầy đủ trong phạm vi từng giao thức |
| Hạn chế công gán nhãn mới | Đạt,0đợt human/LLM annotation mới |
| Có ứng dụng và artifact dataset | Có; usefulness/novelty/generality là ba câu hỏi cần tách |
| Một cơ chế mới đủ khác prior art, được đối chiếu gần | Chưa xác lập |
| Lợi ích đo trực tiếp trên workload đại diện | Đang thu hẹp thiếu hụt; chưa có natural user-session validation |
| Bản thảo thống nhất theo claim cuối | Có draft vòng3; chưa hoàn tất bản chốt theo toàn bộ kết quả mới |
| Journal/Q1 theo đúng năm/chuyên ngành và submission | Chưa xác minh/chốt/nộp; không có bảo đảm nhận bài |

Ưu tiên tiếp theo là quyết định luận đề paper từ kết quả mới và đối chiếu cách chuyên biệt hóa với phương pháp gần nhất, thay vì thêm tên hoặc gộp mọi mô hình. Natural typo channel có nguồn/quyền rõ và reproduction/phản biện chuyên môn độc lập vẫn cần cho claim rộng. Local tăng tài nguyên/quy mô tái lập, không tự tăng khả năng suy luận của chat; cloud2CPU/8GiB đã đủ thực hiện các lượt hiện tại. Không cần GPU trong scope đang chạy.

Lưu file cục bộ không tự đẩy tất cả Word/Markdown/code lên GitHub. Chỉ các file được commit/push trong repo mới thuộc branch; dữ liệu thô/index lớn hoặc tài liệu có quyền riêng được giữ ngoài gói nếu đã quy định. Lượt mới giữ main nguyên tại commit nền và có branch riêng để review trước bất kỳ quyết định gộp sau này.
