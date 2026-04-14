# Routing Decisions Log - Lab Day 09

**Nhóm:** ___________  
**Ngày:** 2026-04-14

> Ghi từ trace thực tế của latest test run.

---

## Routing Decision #1

**Task đầu vào:**
> SLA xử lý ticket P1 là bao lâu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `general knowledge query → không chọn MCP, default retrieval`  
**MCP tools được gọi:** None  
**Workers called sequence:** retrieval_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): SLA xử lý ticket P1 như sau: 1. Phản hồi ban đầu: 15 phút kể từ khi ticket được tạo. 2. Xử lý và khắc phục: 4 giờ. 3. Escalation: Tự động escalate lên Senior...
- confidence: 0.52
- Correct routing? Yes

**Nhận xét:**

Route kỳ vọng theo `data/test_questions.json` là `retrieval_worker`. Trường hợp này cho thấy supervisor đang route đúng/sai ra sao và trace có đủ thông tin để debug ngay từ `route_reason`.

## Routing Decision #2

**Task đầu vào:**
> Sản phẩm kỹ thuật số (license key) có được hoàn tiền không?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task contains policy/access keyword: license → chọn MCP`  
**MCP tools được gọi:** search_kb  
**Workers called sequence:** policy_tool_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): Sản phẩm kỹ thuật số (license key) không được hoàn tiền. Điều này được quy định rõ trong tài liệu nội bộ: "Sản phẩm thuộc danh mục hàng kỹ thuật số (license...
- confidence: 0.43
- Correct routing? Yes

**Nhận xét:**

Route kỳ vọng theo `data/test_questions.json` là `policy_tool_worker`. Trường hợp này cho thấy supervisor đang route đúng/sai ra sao và trace có đủ thông tin để debug ngay từ `route_reason`.

## Routing Decision #3

**Task đầu vào:**
> ERR-403-AUTH là lỗi gì và cách xử lý?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `general knowledge query → không chọn MCP, default retrieval`  
**MCP tools được gọi:** None  
**Workers called sequence:** retrieval_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): Không đủ thông tin trong tài liệu nội bộ để xác định lỗi ERR-403-AUTH và cách xử lý.
- confidence: 0.3
- Correct routing? Yes

**Nhận xét:**

Route kỳ vọng theo `data/test_questions.json` là `retrieval_worker`. Trường hợp này cho thấy supervisor đang route đúng/sai ra sao và trace có đủ thông tin để debug ngay từ `route_reason`.

## Routing Decision #4

**Task đầu vào:**
> Ticket P1 lúc 2am. Cần cấp Level 2 access tạm thời cho contractor để thực hiện emergency fix. Đồng thời cần notify stakeholders theo SLA. Nêu đủ cả hai quy trình.

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task contains policy/access keyword: access → chọn MCP | risk_high flagged (keyword: emergency)`  
**MCP tools được gọi:** search_kb, get_ticket_info  
**Workers called sequence:** policy_tool_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): Để xử lý Ticket P1 lúc 2am, cần thực hiện hai quy trình sau: ### 1. Quy trình thông báo theo SLA: - **Bước 1: Tiếp nhận** - On-call engineer nhận alert hoặc...
- confidence: 0.62
- Correct routing? Yes

**Nhận xét:**

Route kỳ vọng theo `data/test_questions.json` là `policy_tool_worker`. Trường hợp này cho thấy supervisor đang route đúng/sai ra sao và trace có đủ thông tin để debug ngay từ `route_reason`.


---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 9 | 60.0% |
| policy_tool_worker | 6 | 40.0% |
| human_review | 0 | 0% |

### Routing Accuracy

- Câu route đúng: 15 / 15
- Câu route sai: 0
- Câu trigger HITL: 0

### Lesson Learned về Routing

1. Keyword routing đủ nhanh và minh bạch cho domain nhỏ của lab, miễn là `route_reason` ghi rõ keyword nào match.
2. Query policy/access nên route sang policy tool sớm để tận dụng MCP search và `get_ticket_info`, thay vì để retrieval làm toàn bộ.

### Route Reason Quality

`route_reason` hiện đã đủ để biết vì sao supervisor chọn worker nào, nhưng vẫn nên cải tiến thêm bằng cách ghi cả `matched_keywords` dạng list thay vì chỉ lấy keyword đầu tiên.
