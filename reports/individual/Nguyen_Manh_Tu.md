# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Mạnh Tú  
**Vai trò trong nhóm:** MCP Owner  
**Ngày nộp:** 14/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi phụ trách phần nào?

**Module/file tôi chịu trách nhiệm:**
- File chính: `mcp_server.py` — implement 4 MCP tools (`search_kb`, `get_ticket_info`, `check_access_permission`, `create_ticket`)
- Tích hợp workers vào `graph.py` — thay thế toàn bộ placeholder bằng worker thực
- Functions tôi implement: `tool_search_kb()`, `tool_get_ticket_info()`, `tool_check_access_permission()`, `tool_create_ticket()`, `dispatch_tool()`, `list_tools()`

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Tôi là người tạo repository và phân chia task cho từng thành viên theo sprint. Về mặt kỹ thuật, `mcp_server.py` của tôi là lớp công cụ mà **Worker Owner** gọi qua `_call_mcp_tool()` trong `workers/policy_tool.py`. Khi `policy_tool_worker` cần tra cứu knowledge base hoặc ticket, nó gọi `dispatch_tool()` của tôi. Tôi cũng chịu trách nhiệm tích hợp các worker vào `graph.py` — uncomment imports và thay placeholder nodes bằng lời gọi worker thực, đảm bảo pipeline chạy end-to-end. Ngoài ra, tôi hỗ trợ **Trace & Docs Owner** viết report cho Sprint 4.

**Bằng chứng (commit hash):**
- `9b7ffce` — first commit (tạo repo)
- `31c264d` — Add index
- `fbaa4df`, `fc74243` — Commit sprint 3 (implement MCP server + tích hợp graph.py)
- Merge PRs: `#1`, `#4`, `#5`, `#6` — review và merge code của các thành viên

---

## 2. Tôi đã ra một quyết định kỹ thuật gì?

**Quyết định:** Tôi viết lại `tool_search_kb()` trong `mcp_server.py` để kết nối trực tiếp với ChromaDB thay vì delegate qua hàm `retrieve_dense` của retrieval worker.

**Lý do:**
Code mẫu ban đầu của `search_kb` gọi `from workers.retrieval import retrieve_dense` — nhưng sau khi Worker Owner implement `retrieval.py`, interface thực tế là `_get_embedding_fn()` kết hợp `collection.query()`, không có hàm `retrieve_dense` nào. Thay vì yêu cầu Worker Owner tạo thêm một wrapper function chỉ để phục vụ MCP, tôi quyết định cho MCP server truy cập ChromaDB trực tiếp: lấy embedding function qua `_get_embedding_fn()`, tự tạo `query_embedding`, rồi gọi `collection.query()` với `query_embeddings`, `n_results`, `include=["documents", "distances", "metadatas"]`.

**Trade-off đã chấp nhận:**
MCP server giờ phụ thuộc vào `chromadb` và `_get_embedding_fn` — tức là coupling giữa MCP layer và retrieval layer tăng lên. Nhưng đổi lại, MCP server hoạt động độc lập, không cần Worker Owner phải thay đổi code, và kết quả search chính xác hơn mock data.

**Bằng chứng từ trace/code:**

```python
# mcp_server.py — tool_search_kb() (commit fc74243)
from workers.retrieval import _get_embedding_fn
embed_fn = _get_embedding_fn()
query_embedding = embed_fn(query)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("day09_docs")
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    include=["documents", "distances", "metadatas"]
)
```

---

## 3. Tôi đã sửa một lỗi gì?

**Lỗi:** Pipeline `graph.py` chạy end-to-end nhưng trả về dữ liệu giả (placeholder) thay vì kết quả thực từ workers và MCP tools.

**Symptom (pipeline làm gì sai?):**
Khi chạy `python graph.py`, pipeline hoàn thành không lỗi nhưng mọi câu hỏi đều trả về cùng một `final_answer` là `"[PLACEHOLDER] Câu trả lời được tổng hợp từ 1 chunks."` với `confidence=0.75` cố định. Trace cho thấy `retrieved_chunks` luôn chỉ có 1 chunk mock về SLA P1, bất kể câu hỏi là gì. Đồng thời, `run_id` bị trùng khi chạy nhiều câu hỏi liên tiếp vì format chỉ có precision đến giây.

**Root cause (lỗi nằm ở đâu):**
Trong `graph.py`, ba hàm `retrieval_worker_node()`, `policy_tool_worker_node()`, `synthesis_worker_node()` vẫn đang dùng code placeholder từ Sprint 1 — trả về hardcoded data thay vì gọi worker thật. Imports của workers bị comment out. Thêm vào đó, `run_id` dùng `%Y%m%d_%H%M%S` nên hai lần chạy trong cùng giây sẽ tạo ID trùng.

**Cách sửa:**
- Uncomment imports: `from workers.retrieval import run as retrieval_run`, tương tự cho `policy_tool` và `synthesis`
- Thay toàn bộ body của 3 wrapper functions bằng lời gọi worker thực: `return retrieval_run(state)`, `return policy_tool_run(state)`, `return synthesis_run(state)`
- Thêm `%f` (microseconds) vào `run_id` format: `run_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}`
- Cập nhật `route_reason` cho rõ hơn: thêm `"→ chọn MCP"` và `"→ không chọn MCP"` để trace dễ đọc

**Bằng chứng trước/sau:**
Trước khi sửa:
```
final_answer: "[PLACEHOLDER] Câu trả lời được tổng hợp từ 1 chunks."
confidence: 0.75
run_id: run_20260414_143022
```
Sau khi sửa:
```
final_answer: "SLA P1 yêu cầu phản hồi trong 15 phút và xử lý trong 4 giờ..."
confidence: 0.52
run_id: run_20260414_143022_481753
route_reason: "task contains policy/access keyword: cấp quyền → chọn MCP"
```

---

## 4. Tôi tự đánh giá đóng góp của mình

**Tôi làm tốt nhất ở điểm nào?**
Tôi làm tốt vai trò điều phối: tạo repo, phân task rõ ràng theo sprint, review và merge PR cho cả team. Về code, việc tích hợp workers vào graph.py đúng thời điểm giúp team có pipeline hoạt động thực sự để Sprint 4 chạy trace analysis.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Tôi chưa triển khai được HTTP server cho MCP (bonus +2). `mcp_server.py` vẫn là mock class (in-process), chưa phải real MCP server qua HTTP. Nếu quản lý thời gian tốt hơn, tôi có thể đạt được điểm bonus này.

**Nhóm phụ thuộc vào tôi ở đâu?**
Repo management — mọi PR đều merge qua tôi. MCP tools — nếu `dispatch_tool()` lỗi thì `policy_tool_worker` không có dữ liệu từ knowledge base hay ticket system.

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi cần `_get_embedding_fn()` từ **Worker Owner** để `search_kb` hoạt động. Tôi cũng cần **Supervisor Owner** route đúng sang `policy_tool_worker` để MCP tools được gọi.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì?

Tôi sẽ tạo lại bộ test thống nhất cho Day 08 để so sánh chính xác với Day 09. Hiện tại, bảng so sánh trong `docs/single_vs_multi_comparison.md` có nhiều cột Day 08 để `N/A` vì kết quả phân tích của Day 08 chạy với các tham số khác nhau (embedding model, chunk size, test set) nên không thể so sánh trực tiếp. Tôi đề xuất chạy lại Day 08 pipeline với cùng bộ `grading_questions.json` và cùng embedding model `text-embedding-3-small` để có baseline thực sự, từ đó đánh giá chính xác multi-agent có cải thiện accuracy hay chỉ tăng latency.

---

*File này lưu tại: `reports/individual/Nguyen_Manh_Tu.md`*
