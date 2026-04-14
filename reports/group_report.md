# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** Nhóm 09  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Hoàng Sơn Lâm | Supervisor Owner | hoangsonlamwk4@gmail.com |
| Lê Tuấn Đạt | Worker Owner | letuandat220@gmail.com |
| Nguyễn Mạnh Tú | MCP Owner | tunm17421@gmail.com |
| Lưu Linh Ly | Trace & Docs Owner | lyluulinh.work@gmail.com |

**Ngày nộp:** 2026-04-14
**Repo:** https://github.com/TuNM17421/Nhom09-E403-Day09  
**Độ dài khuyến nghị:** 600–1000 từ

---

> **Hướng dẫn nộp group report:**
> 
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code/trace** — không mô tả chung chung
> - Mỗi mục phải có ít nhất 1 ví dụ cụ thể từ code hoặc trace thực tế của nhóm

---

## 1. Kiến trúc nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn hệ thống nhóm: bao nhiêu workers, routing logic hoạt động thế nào,
> MCP tools nào được tích hợp. Dùng kết quả từ `docs/system_architecture.md`.

**Hệ thống tổng quan:**

Nhóm xây dựng hệ thống theo pattern Supervisor-Worker với supervisor là `graph.py`, hai worker chính là `workers/retrieval.py` và `workers/policy_tool.py`, và `workers/synthesis.py` chịu trách nhiệm tổng hợp câu trả lời. Supervisor phân luồng câu hỏi, worker thực hiện từng phần cụ thể, và trace lưu lại `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used`, `retrieved_sources`, `confidence` để dễ debug.

**Routing logic cốt lõi:**
> Supervisor dùng rule-based keyword matching thay vì route toàn bộ bằng LLM. `SLA`/`ticket` mặc định qua `retrieval_worker`; `policy`, `access`, `flash sale`, `license`, `store credit` qua `policy_tool_worker`; các câu emergency được đánh dấu `risk_high`.

**MCP tools đã tích hợp:**
- `search_kb`: tìm kiếm nội dung tài liệu và trả về nguồn; ví dụ trace `q03` và `q07` gọi `search_kb` để lấy `it/access-control-sop.md`.
- `get_ticket_info`: dùng khi cần dữ liệu ticket chi tiết để trả lời emergency access request; ví dụ trace `q13` gọi `get_ticket_info`.
- `check_access_permission`: công cụ đã implement trong `mcp_server.py` như khả năng mở rộng, hỗ trợ kiểm tra access level tạm thời.

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn phương án đã chọn.

**Quyết định:** Dùng supervisor rule-based thay vì để toàn bộ routing cho single-agent hoặc LLM classifier.

**Bối cảnh vấn đề:**

Trước Day 09, Day 08 đang chạy single-agent RAG khiến khi lỗi xảy ra không biết lỗi thuộc retrieval, policy hay generation. Nhóm cần giải pháp vừa mở rộng vừa dễ debug, nên quyết định tách supervisor khỏi worker và lưu trace routing rõ ràng.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Rule-based supervisor | Minh bạch, dễ debug, dễ mở rộng | Cần bảo trì keyword list |
| LLM route classifier | linh hoạt với biến thể câu hỏi | khó giải thích, khó đảm bảo route đúng |
| Giữ single-agent | cài đặt nhanh, ít overhead | thiếu trace, khó mở rộng |

**Phương án đã chọn và lý do:**

Nhóm chọn rule-based supervisor vì nó cho trace rõ ràng và giải quyết được yêu cầu Sprint 4 về debugability. Với `route_reason`, chúng tôi có thể biết ngay worker nào được gọi và vì sao, giúp khoanh vùng lỗi nhanh hơn khi so với single-agent.

**Bằng chứng từ trace/code:**

```text
q03 route_reason: task contains policy/access keyword: cấp quyền → chọn MCP
q15 route_reason: task contains policy/access keyword: access → chọn MCP | risk_high flagged (keyword: emergency)
```

---

## 3. Kết quả grading questions (150–200 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Nhóm đạt bao nhiêu điểm raw?
> - Câu nào pipeline xử lý tốt nhất?
> - Câu nào pipeline fail hoặc gặp khó khăn?

**Tổng điểm raw ước tính:** Chưa có dữ liệu chính thức do `grading_questions.json` chưa có trong repo và chưa có file `artifacts/grading_run.jsonl`.

**Câu pipeline xử lý tốt nhất:**
- ID: Dựa trên test set, `q01` và `q02` là hai câu đơn giản được xử lý tốt nhất với retrieval_worker + synthesis_worker. Lý do: route đúng, retrieved_sources chính xác và final answer ngắn gọn, rõ ràng.

**Câu pipeline fail hoặc partial:**
- ID: `q09` — Fail ở phần abstain / thiếu thông tin. Root cause: supervisor vẫn route sang retrieval khi câu hỏi cần xác nhận format lỗi, nên worker chỉ có thể trả về "Không đủ thông tin".

**Câu gq07 (abstain):** Nhóm xử lý thế nào?

Nhóm đã thiết kế `workers/synthesis.py` để trả về câu trả lời abstain rõ ràng khi context không đủ. Mục tiêu là tránh hallucination và giữ grounded khi nguồn không hỗ trợ.

**Câu gq09 (multi-hop khó nhất):** Trace ghi được 2 workers không? Kết quả thế nào?

Trong test question tương tự, trace cho thấy `retrieval_worker` và `synthesis_worker` đều được gọi; retrieved_sources có cả `support/helpdesk-faq.md` và `it/access-control-sop.md`. Multi-hop source hit rate của test run đạt 100.0% với 4/4 trường hợp multi-hop, cho thấy worker orchestration hỗ trợ tốt cho các câu cần kết hợp nhiều nguồn.

---

## 4. So sánh Day 08 vs Day 09 — Điều nhóm quan sát được (150–200 từ)

> Dựa vào `docs/single_vs_multi_comparison.md` — trích kết quả thực tế.

**Metric thay đổi rõ nhất (có số liệu):**

Latency tăng rõ: Day 09 có avg latency `6020 ms`. Bù lại, Day 09 đạt `routing_accuracy` 100.0% và `multi-hop source hit rate` 100.0% trên bộ test nội bộ.

**Điều nhóm bất ngờ nhất khi chuyển từ single sang multi-agent:**

Nhóm bất ngờ là multi-agent vẫn duy trì được độ chính xác route rất cao, trong khi vẫn cho trace rõ. Đây là bằng chứng rằng tách supervisor-worker giúp mở rộng và debug được, dù có thêm overhead.

**Trường hợp multi-agent KHÔNG giúp ích hoặc làm chậm hệ thống:**

Với các câu retrieval đơn giản như `q01`, `q04` và `q05`, multi-agent làm chậm hơn do thêm bước route và worker handoff. Ở trường hợp này, cấu trúc multi-agent chưa tối ưu hơn single-agent về latency, nhưng vẫn có giá trị cao về trace.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Hoàng Sơn Lâm | Supervisor logic và `graph.py`; route_reason, xác định route rules | Sprint 1/4 |
| Lê Tuấn Đạt | `workers/retrieval.py`; retrieval architecture và test tương tác với Chroma/embedding | Sprint 2/4 |
| Nguyễn Mạnh Tú | `mcp_server.py` và `workers/policy_tool.py`; tích hợp `search_kb`, `get_ticket_info` | Sprint 3/4 |
| Lưu Linh Ly | `eval_trace.py`, trace analysis, docs và báo cáo nhóm | Sprint 4 |

**Điều nhóm làm tốt:**

Nhóm phân chia rõ trách nhiệm theo ownership, nhờ đó mỗi thành viên làm chủ một phần code và đẩy tiến độ nhanh. Việc có trace cụ thể giúp cả team debug chung dễ hơn.

**Điều nhóm làm chưa tốt hoặc gặp vấn đề về phối hợp:**

Chưa có chuẩn thống nhất ban đầu cho `route_reason` và trace format nên phải sửa lại một vài lần. Việc chưa có grading run tức thời cũng làm chậm đánh giá final.

**Nếu làm lại, nhóm sẽ thay đổi gì trong cách tổ chức?**

Sẽ dành đầu sprint một buổi sync để thống nhất schema trace và routing keywords, nhằm giảm sửa lại sau khi implement.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> 1–2 cải tiến cụ thể với lý do có bằng chứng từ trace/scorecard.

Nếu có thêm 1 ngày, nhóm sẽ hoàn thiện route `risk_high` thành `human_review` thực tế và tăng cường policy fallback trong `workers/policy_tool.py`. Evidence: `q15` đã flag emergency nhưng chưa có human review, và `q13` cho thấy policy analysis cần ổn định hơn để tránh fallback khi OpenAI trả lỗi.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
