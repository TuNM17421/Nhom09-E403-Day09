# System Architecture - Lab Day 09

**Nhóm:** Nhóm 09    
**Ngày:** 2026-04-14  
**Version:** 1.0

---

## 1. Tổng quan kiến trúc

**Pattern đã chọn:** Supervisor-Worker  
**Lý do chọn pattern này (thay vì single agent):**

Nhóm tách pipeline thành 4 phần rõ vai trò: supervisor ở [graph.py](/C:/Users/ADMIN/Nhom09-E403-Day09/graph.py), retrieval worker ở [workers/retrieval.py](/C:/Users/ADMIN/Nhom09-E403-Day09/workers/retrieval.py), policy/MCP worker ở [workers/policy_tool.py](/C:/Users/ADMIN/Nhom09-E403-Day09/workers/policy_tool.py), và synthesis worker ở [workers/synthesis.py](/C:/Users/ADMIN/Nhom09-E403-Day09/workers/synthesis.py). Cách tách này giúp trace ghi được `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used`, `retrieved_sources`, `confidence`, nên khi câu trả lời sai có thể khoanh vùng lỗi nhanh hơn Day 08.

---

## 2. Sơ đồ Pipeline

```text
User Question
   |
   v
Supervisor (keyword routing + risk flag + needs_tool)
   |
   +--> retrieval_worker ------------------+
   |                                       |
   +--> policy_tool_worker --(MCP)---------+--> synthesis_worker --> final_answer
   |
   +--> human_review (placeholder, chỉ khi route human_review)
```

---

## 3. Vai trò từng thành phần

### Supervisor (`graph.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Nhận task, gắn `supervisor_route`, `route_reason`, `needs_tool`, `risk_high` |
| **Input** | `task` từ user |
| **Output** | `supervisor_route`, `route_reason`, `risk_high`, `needs_tool` |
| **Routing logic** | Rule-based theo keyword: SLA/ticket mặc định về retrieval; refund/access/flash sale/level access về policy tool |
| **HITL condition** | Có `human_review_node()` nhưng hiện chưa được route thực tế; `risk_high` mới chỉ gắn cờ |

### Retrieval Worker (`workers/retrieval.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Query ChromaDB collection `day09_docs`, trả về chunks và sources |
| **Embedding model** | `text-embedding-3-small` (OpenAI) |
| **Top-k** | Mặc định 3 |
| **Stateless?** | Yes |

### Policy Tool Worker (`workers/policy_tool.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Gọi MCP tool nếu cần, phân tích policy và exceptions trước khi synthesis |
| **MCP tools gọi** | `search_kb`, `get_ticket_info` |
| **Exception cases xử lý** | Flash Sale, digital product/license, activated product, temporal policy note |

### Synthesis Worker (`workers/synthesis.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **LLM model** | `gpt-4o-mini` (fallback Gemini nếu có) |
| **Temperature** | 0.1 |
| **Grounding strategy** | Chỉ dùng `retrieved_chunks` và `policy_result` để dựng context |
| **Abstain condition** | Nếu thiếu context thì prompt yêu cầu trả về “Không đủ thông tin trong tài liệu nội bộ” |

### MCP Server (`mcp_server.py`)

| Tool | Input | Output |
|------|-------|--------|
| search_kb | query, top_k | chunks, sources, total_found |
| get_ticket_info | ticket_id | ticket details |
| check_access_permission | access_level, requester_role, is_emergency | can_grant, approvers, notes |
| create_ticket | priority, title, description | mock ticket_id, url, created_at |

---

## 4. Shared State Schema

| Field | Type | Mô tả | Ai đọc/ghi |
|-------|------|-------|-----------|
| task | str | Câu hỏi đầu vào | supervisor đọc |
| supervisor_route | str | Worker được chọn | supervisor ghi |
| route_reason | str | Lý do route | supervisor ghi |
| risk_high | bool | Đánh dấu query có rủi ro cao | supervisor ghi |
| needs_tool | bool | Có cần MCP/tool không | supervisor ghi |
| retrieved_chunks | list | Evidence retrieval | retrieval/policy ghi, synthesis đọc |
| retrieved_sources | list | Danh sách nguồn | retrieval ghi |
| policy_result | dict | Kết quả policy analysis | policy worker ghi |
| mcp_tools_used | list | Log tool calls | policy worker ghi |
| final_answer | str | Câu trả lời cuối | synthesis ghi |
| confidence | float | Mức tin cậy | synthesis ghi |
| workers_called | list | Thứ tự worker đã chạy | mọi node ghi |
| history | list | Trace chi tiết từng bước | mọi node ghi |
| latency_ms | int | Tổng thời gian xử lý | graph ghi |
| run_id | str | ID của run | graph ghi |

---

## 5. Lý do chọn Supervisor-Worker so với Single Agent (Day 08)

| Tiêu chí | Single Agent (Day 08) | Supervisor-Worker (Day 09) |
|----------|----------------------|--------------------------|
| Debug khi sai | Khó - không rõ lỗi ở retrieval hay generation | Dễ hơn - trace tách route, workers, sources |
| Thêm capability mới | Phải sửa prompt/pipeline chung | Thêm MCP tool hoặc worker riêng |
| Routing visibility | Không có | Có `route_reason` trong trace |
| Kiểm thử độc lập | Khó tách | Có thể test từng worker standalone |

**Quan sát từ trace thực tế:** latest run có `routing_accuracy` 15/15 (100.0%), `mcp_usage_rate` 6/15 (40.0%), và worker được gọi thực tế gồm policy_tool_worker, retrieval_worker, synthesis_worker.

---

## 6. Giới hạn và điểm cần cải tiến

1. `risk_high` đã được gắn cờ nhưng hiện chưa route sang `human_review`, nên HITL vẫn mới ở mức placeholder.
2. Retrieval và MCP search hiện phụ thuộc OpenAI embeddings, nên môi trường không có mạng sẽ rơi vào fallback/mock.
3. Policy analysis dựa nhiều vào LLM; trace thực tế vẫn có case q13 bị fallback khi lời gọi request thất bại.
