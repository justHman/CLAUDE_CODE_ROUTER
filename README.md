# Hướng dẫn sử dụng Claude Code API Router Server

Project này là một API Server đóng vai trò như một proxy (người trung gian) cho công cụ **Claude Code**. Nó giả lập API của Anthropic (đầu nhận) nhưng ở phía sau sẽ chuyển tiếp (route) request của bạn tới các nhà cung cấp LLM khác nhau như NVIDIA, OpenRouter, v.v., đồng thời hỗ trợ chuyển đổi chuẩn dữ liệu (Text, Image, Tool Calling, MCP, Stream) qua lại giữa 2 định dạng (Anthropic <-> OpenAI).

---

## 1. Cài đặt Server

### Bước 1: Khởi tạo môi trường ảo (Khuyên dùng)
Mở Terminal/PowerShell tại thư mục `d:\Project\Code\claude_code_router` và chạy:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Bước 2: Cài đặt thư viện
```powershell
pip install -r requirements.txt
```

---

## 2. Cấu hình Server

### Cấu hình `.env`
Tạo một file `.env` từ file mẫu `config/.env.example` (bạn có thể copy ra thư mục gốc hoặc để ở `config/` đều được, framework pydantic-settings sẽ tự quét):
```env
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8082

# Nhập API Key của các provider bạn muốn dùng
NVIDIA_API_KEY=nvapi-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Cấu hình `config/config.yaml`
Tại đây bạn sẽ định nghĩa các Provider (địa chỉ, loại API) và chỉ định quy tắc `model_mapping`. Có hai cách map:

**Cách 1: Map Cơ Bản (Chỉ trỏ tới Provider)**
Dùng khi tên model mà Claude gửi đi **giống hệt** với tên model trên API của provider (VD: trên OpenRouter).
```yaml
model_mapping:
  "minimax/minimax-m2.5:free": "openrouter"
  "qwen/qwen3-coder:free": "openrouter"
```

**Cách 2: Map Kèm Dịch Tên Model (Model Translation)**
Dùng khi tên model Claude gửi đi khác với tên model thật của Provider (nếu gửi nguyên xi sẽ bị lỗi 404 Not Found). Ví dụ bạn bắt Claude điền model là `"sonnet[1m]"`, nhưng Nvidia API yêu cầu tên chuẩn phải là `"minimaxai/minimax-m2.5"`.
```yaml
model_mapping:
  "sonnet[1m]":
    provider: "nvidia"
    target_model: "minimaxai/minimax-m2.5"
```

Khi map theo cách 2, Router sẽ nhận `"sonnet[1m]"`, rồi ngầm dịch thành `"minimaxai/minimax-m2.5"` trước khi bắn sang Nvidia.

*(Lưu ý: Không được viết trùng lặp 1 tên model ở 2 nơi trong `model_mapping` của yaml. Nếu không dòng bên dưới sẽ ghi đè dòng bên trên)*

---

## 3. Khởi chạy Server
Từ thư mục gốc của project, chạy lệnh sau:
```powershell
python main.py
```
*Server sẽ chạy ở địa chỉ `http://127.0.0.1:8082` và sẵn sàng nhận request từ Claude Code.*

---

## 4. Tích hợp với Claude Code

Để Claude Code gọi vào Router Sever của chúng ta thay vì gọi thẳng lên Anthropic, bạn cần thiết lập biến môi trường thông qua file settings của Claude.

Mở file `c:\Users\Ngô Hoài Nam\.claude\settings.json` và cấu hình phần `"env"` như sau:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:8082",
    "ANTHROPIC_AUTH_TOKEN": "dummy-token",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_MODEL": "sonnet[1m]"
  },
  "model": "sonnet[1m]",
  "language": "Việt Nam",
  "effortLevel": "medium",
  "autoUpdatesChannel": "latest"
}
```
**Giải thích:**
- `ANTHROPIC_BASE_URL`: Trỏ về API Server local đang chạy ở port 8082. Không cần thêm `/v1` vì thư viện client của Claude sẽ tự nối thêm `/v1/messages`.
- `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_API_KEY`: Đặt chuỗi bất kỳ (`dummy-token`) hoặc bỏ trống phần api key (nếu dùng proxy local thì server của chúng ta sẽ không check key này mà tự lấy key trong file `.env` nội bộ để gọi NVIDIA/OpenRouter).
- `ANTHROPIC_MODEL` / `model`: Đặt tên model bạn muốn truyền cho Router (VD: `sonnet[1m]`). 

**💡 Cách đổi Mode / Chuyển Model:**
Nhờ vào thiết kế của server, việc đổi sang model hay provider khác vô cùng đơn giản:
1. Bạn mở `~/.claude/settings.json` của Claude Code.
2. Sửa dòng `"ANTHROPIC_MODEL"` và `"model"` thành tên model bạn muốn xài (Ví dụ: `"qwen/qwen3-coder:free"`).
3. Đảm bảo tên đó đã có khai báo trong `model_mapping` của `config.yaml` (ví dụ `"qwen/qwen3-coder:free": "openrouter"`).
4. Khởi động lại `claude`, server sẽ tự động nhận diện chữ `"qwen/qwen3-coder:free"`, xác định Provider là OpenRouter và chuyển tiếp y chang mà không cần lập trình hay sửa thêm code! Lệnh `claude` của bạn sẽ biến thành Qwen.

---

## 5. Chạy Claude Code

Sau khi Server Router hiển thị "Application startup complete.", bạn hãy mở một tab Terminal mới (Powershell mới).
Di chuyển tới source code bất kỳ bạn muốn thao tác và gõ lệnh chạy claude như bình thường:

```powershell
claude
```

**Workflow Hoạt động:**
1. Trình dòng lệnh `claude` khởi chạy và đọc `settings.json`.
2. Nó gửi request phân tích file/công cụ tới `http://127.0.0.1:8082/v1/messages`.
3. Server Router của bạn (Terminal 1) hiện log đang xử lý file/tool calling và map qua định dạng OpenAI.
4. Nó forward lên `https://integrate.api.nvidia.com/v1`, sau đó nhận Stream text/tool trả về, dịch ngược lại thành định dạng Anthropic Stream.
5. `claude` ở trình dòng lệnh hiện chữ gõ ra tuần tự mượt mà trên màn hình và tiếp tục thực hiện lệnh (agent functionality) như bình thường!
