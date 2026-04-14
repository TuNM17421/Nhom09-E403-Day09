# Single Agent vs Multi-Agent Comparison - Lab Day 09

**Nhóm:** Nhóm 09    
**Ngày:** 2026-04-14

> Day 09 dùng số liệu thật từ latest test run. Day 08 để `N/A` vì repo hiện tại không chứa baseline.

---

## 1. Metrics Comparison

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 0.513 | 0.501 | -0.012 | |
| Avg latency (ms) | 2233.0 | 6020 | 3787.0 | |
| Abstain rate (%) | {'count': 2, 'total': 20, 'pct': 10.0, 'display': '2/20 (10.0%)'} | 6.7 | N/A | q09 là case abstain |
| Multi-hop accuracy | {'count': 20, 'total': 20, 'pct': 100.0, 'display': '20/20 (100.0%)'} | 100.0 | N/A | proxy theo expected source hit |
| Routing visibility | ✗ Không có | ✓ Có route_reason | N/A | |
| Debug time (estimate) | 30 | 5-10 phút | N/A | đọc trace thay vì lần mò toàn pipeline |
| Routing accuracy | N/A | 100.0 | N/A | so với `expected_route` trong test set |

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | N/A | Route thường đúng, source hit cao |
| Latency | N/A | Thấp hơn nhóm policy/multi-hop |
| Observation | N/A | Các câu retrieval như q01, q04, q05 chạy ổn với retrieval_worker + synthesis_worker |

**Kết luận:** Multi-agent không nhất thiết nhanh hơn single-agent, nhưng ở câu đơn giản vẫn giữ được luồng xử lý gọn và trace rõ.

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | N/A | Proxy source hit: 4/4 (100.0%) |
| Routing visible? | ✗ | ✓ |
| Observation | N/A | Các câu q13-q15 cho thấy policy tool + MCP hữu ích, nhưng vẫn còn case chưa gom đủ cả 2 nguồn |

**Kết luận:** Multi-agent hữu ích nhất ở câu cần kết hợp policy/access/SLA, vì trace cho thấy worker nào xử lý phần nào.

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | N/A | 1/15 (6.7%) |
| Hallucination cases | N/A | Cần review thủ công thêm |
| Observation | N/A | q09 là case quan trọng để kiểm tra grounded abstain |

**Kết luận:** Day 09 đã có signal để đo abstain success (1/1 (100.0%)), nhưng vẫn nên thêm rule rõ hơn khi retrieval không có evidence.

---

## 3. Debuggability Analysis

### Day 08 - Debug workflow
```text
Khi answer sai -> phải đọc toàn bộ RAG pipeline code -> tìm lỗi ở indexing/retrieval/generation
Không có trace route_reason -> khó biết bắt đầu từ đâu
```

### Day 09 - Debug workflow
```text
Khi answer sai -> đọc latest trace -> xem supervisor_route + route_reason
  -> nếu route sai: sửa keyword routing trong graph.py
  -> nếu retrieval sai: test workers/retrieval.py độc lập
  -> nếu policy sai: test workers/policy_tool.py hoặc mcp_server.py
  -> nếu synthesis sai: test workers/synthesis.py độc lập
```

**Câu debug thực tế:** q13 từng fallback ở policy analysis khi OpenAI trả lỗi request body, nhưng trace vẫn giữ được route, worker sequence và confidence để khoanh vùng ngay ở `policy_tool_worker`.

---

## 4. Extensibility Analysis

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Phải sửa prompt/pipeline chung | Thêm MCP tool trong `mcp_server.py` |
| Thêm 1 domain mới | Khó tách riêng | Có thể thêm worker mới |
| Thay đổi retrieval strategy | Sửa trực tiếp pipeline | Sửa `retrieval_worker` độc lập |
| A/B test một phần | Khó | Dễ hơn vì thay từng worker |

**Nhận xét:** Day 09 tách biên giới code rõ hơn giữa supervisor, workers và MCP. Đây là lợi ích lớn nhất của repo hiện tại.

---

## 5. Cost & Latency Trade-off

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 1 retrieval embedding + 1 synthesis LLM |
| Complex query | 1 LLM call | 1 MCP search + 1 policy LLM + 1 synthesis LLM |
| MCP tool call | N/A | Có khi query policy/access |

**Nhận xét về cost-benefit:** Day 09 tốn nhiều bước hơn, latency trung bình hiện là 6020 ms, nhưng đổi lại có khả năng trace, route, và mở rộng tốt hơn.

---

## 6. Kết luận

**Multi-agent tốt hơn single agent ở điểm nào?**

1. Dễ debug hơn nhờ `route_reason`, `workers_called`, `mcp_tools_used`, `retrieved_sources`.
2. Dễ mở rộng hơn vì có thể thêm MCP tool hoặc worker mà không đụng toàn bộ pipeline.

**Multi-agent kém hơn hoặc không khác biệt ở điểm nào?**

1. Latency và số bước xử lý cao hơn, đặc biệt với câu policy/multi-hop.

**Khi nào KHÔNG nên dùng multi-agent?**

Khi domain quá nhỏ, chỉ có câu hỏi retrieval đơn giản và nhóm không cần trace chi tiết hay khả năng mở rộng.

**Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**

Thêm real HITL route cho `risk_high`, giảm phụ thuộc mạng ở retrieval/MCP search, và thêm bộ chấm bán tự động cho expected source + abstain correctness.

**Nguồn nổi bật trong latest run:** it/access-control-sop.md (7), policy/refund-v4.pdf (5), support/sla-p1-2026.pdf (5), hr/leave-policy-2026.pdf (3), support/helpdesk-faq.md (3)
