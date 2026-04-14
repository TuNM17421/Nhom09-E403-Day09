# Báo Cáo Cá Nhân - Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Lưu Linh Ly
**Vai trò trong nhóm:** Trace & Docs Owner  
**Ngày nộp:** 2026-04-14

---

## 1. Tôi phụ trách phần nào?

Trong lab này tôi phụ trách chính Sprint 4, tập trung vào [eval_trace.py](/C:/Users/ADMIN/Nhom09-E403-Day09/eval_trace.py) và ba file tài liệu trong `docs/`: [docs/system_architecture.md](/C:/Users/ADMIN/Nhom09-E403-Day09/docs/system_architecture.md), [docs/routing_decisions.md](/C:/Users/ADMIN/Nhom09-E403-Day09/docs/routing_decisions.md), [docs/single_vs_multi_comparison.md](/C:/Users/ADMIN/Nhom09-E403-Day09/docs/single_vs_multi_comparison.md). Phần tôi làm là biến output của pipeline thành artifact có thể đọc, kiểm tra, và dùng làm bằng chứng khi nộp bài.

Các phần tôi trực tiếp hoàn thiện là `run_test_questions()`, `analyze_results()`, `analyze_traces()`, `compare_single_vs_multi()`, `write_docs()`, và cơ chế lưu `latest_test_run.json`. Công việc này phụ thuộc vào output từ graph, workers và MCP; ngược lại, nếu Sprint 4 chưa xong thì nhóm có code chạy được nhưng thiếu trace sạch và tài liệu hoàn chỉnh để nộp.

**Bằng chứng:** thay đổi nằm ở `eval_trace.py`và các file trong `docs/`
![Commit evidence](C:\Users\ADMIN\Nhom09-E403-Day09\reports\individual\LuuLinhLy_commit.png)
---

## 2. Tôi đã ra một quyết định kỹ thuật gì?

**Quyết định:** Tôi chọn phân tích **latest test run** qua một file manifest riêng (`latest_test_run.json`) thay vì quét toàn bộ `artifacts/traces/`.

Lý do là Sprint 4 cần metric đúng cho lần chạy hiện tại, còn thư mục trace lại chứa nhiều file cũ từ các lần test tay. Nếu cứ đọc hết thư mục thì `total_traces`, `avg_latency_ms`, `mcp_usage_rate`, và phần docs sinh ra sẽ bị nhiễu. Tôi cân nhắc hai hướng:  
1. quét toàn bộ trace rồi lọc bằng timestamp, hoặc  
2. mỗi lần chạy thì lưu riêng một manifest của đúng run đó.  

Tôi chọn cách 2 vì đơn giản hơn và dễ giải thích hơn trong report. Mỗi lần `run_test_questions()` chạy xong sẽ lưu `run_id`, `generated_at`, `questions_file`, và `results`. Sau đó `analyze_traces()` ưu tiên đọc đúng latest run. Trade-off là phải thêm một artifact trung gian, nhưng đổi lại toàn bộ metric và docs đều nhất quán. Bằng chứng rõ nhất là sau khi áp dụng cách này, metric không còn bị lẫn trace cũ nữa và latest run được phân tích đúng theo 15 câu public.

---

## 3. Tôi đã sửa một lỗi gì?

**Lỗi:** Metric Sprint 4 ban đầu bị sai vì script trộn trace cũ với latest run.

**Symptom:** Khi phân tích, `total_traces` tăng lên 42 dù `data/test_questions.json` chỉ có 15 câu. Điều này làm lệch `routing_distribution`, `avg_latency_ms`, `mcp_usage_rate`, và kéo sai cả phần docs. Ngoài ra, source hit ban đầu cũng bị thấp giả tạo vì Day 09 đang dùng source kiểu `support/sla-p1-2026.pdf`, còn expected source trong test set lại là `sla_p1_2026.txt`.

**Root cause:** `analyze_traces()` đọc toàn bộ file trong `artifacts/traces/` mà không biết đâu là lần chạy hiện tại. Đồng thời phần so khớp source dùng chuỗi thô, không tính đến việc nhóm build index bằng `index.py` nên source name khác format expected source.

**Cách sửa:** Tôi thêm `latest_test_run.json`, tách `analyze_results()` để phân tích đúng payload của latest run, và chuẩn hóa source name trước khi tính source hit. Sau khi sửa và chạy lại, metric trở về đúng quy mô `15 traces`, `routing_accuracy = 15/15`, `source_hit_rate = 15/15`, `abstain_success = 1/1`.

---

## 4. Tôi tự đánh giá đóng góp của mình

Tôi làm tốt nhất ở phần biến một repo “đã chạy được” thành một repo “có thể nộp và có thể bảo vệ được”. Tôi không trực tiếp viết graph hay worker core, nhưng tôi làm phần giúp nhóm chứng minh hệ thống hoạt động ra sao bằng số liệu và tài liệu cụ thể.

Điểm tôi làm chưa tốt là phần so sánh Day 08 ban đầu mất khá nhiều thời gian. Artifact Day 08 chỉ có scorecard và CSV, trong khi Day 09 lại có thêm `route_reason`, `routing_accuracy`, `workers_called`. Vì hai phía không log cùng một loại dữ liệu nên tôi không thể compare hoàn toàn “apple-to-apple”.

Nhóm phụ thuộc vào tôi ở chỗ nếu Sprint 4 chưa xong thì nhóm chưa có trace sạch, docs chưa điền, và report chưa có dữ liệu để bám vào.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì?

Nếu có thêm 2 giờ, tôi sẽ chuẩn hóa lại **bộ metric chung giữa Day 08 và Day 09**. Khó khăn lớn nhất của tôi không phải là chạy script, mà là Day 08 và Day 09 tạo ra artifact khác nhau. Day 08 mạnh về `faithfulness`, `relevance`, `completeness`, còn Day 09 mạnh về `routing_accuracy`, `mcp_usage_rate`, `workers_called`, `route_reason`. Tôi sẽ viết thêm một bước chuyển đổi artifact Day 08 sang format gần với Day 09, hoặc ít nhất tạo một bảng mapping metric rõ ràng hơn.
