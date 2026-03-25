# 🚀 Hướng Dẫn Triển Khai (Deploy) Lên Máy Chủ Fly.io

Tài liệu này hướng dẫn chi tiết cách đưa ứng dụng **Claude Code Router** lên nền tảng đám mây [Fly.io](https://fly.io/), thiết lập cơ sở dữ liệu vĩnh viễn (Persistent Volumes), gán API Key bảo mật, và tự động hóa toàn bộ quy trình đẩy code (CI/CD) qua **GitHub Actions**.

---

## 1. Cài đặt Fly CLI & Khởi tạo

Trước tiên, bạn cần cài đặt công cụ dòng lệnh (CLI) của Fly.io để tương tác với máy chủ.

* **Windows**: Mở PowerShell và chạy lệnh sau (chạy dưới quyền Administrator nếu cần):
  ```powershell
  pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
  ```
* **macOS/Linux**:
  ```bash
  curl -L https://fly.io/install.sh | sh
  ```

Sau khi cài đặt xong, hãy đăng nhập vào tài khoản của bạn:
```powershell
flyctl auth login
```
*(Trình duyệt sẽ mở ra để bạn đăng nhập và cấp quyền)*.

---

## 2. Tạo App & Ổ đĩa Vĩnh viễn (Persistent Volume)

Vì đặc thù của kiến trúc Docker trên Fly.io sẽ tự động xoá mọi file khi máy chủ khởi động lại (restart/redeploy), chúng ta cần thiết lập một ổ đĩa vĩnh viễn (Volume) để tránh mất file lịch sử chat SQL `router.db`.

1.  **Sinh cấu hình App mới** (Đừng chạy lệnh này nếu file `fly.toml` đã tồn tại và được cấu hình chuẩn):
    ```powershell
    flyctl launch
    ```
    *Lưu ý: Hủy (Ctrl + C) khi nó hỏi bạn có muốn Deploy luôn không.*

2.  **Chỉ định Vùng máy chủ (Region)**
    Trong file `fly.toml`, hãy kiểm tra và chỉnh biến `primary_region` về khu vực gần Việt Nam nhất để tối ưu tốc độ ping:
    ```toml
    primary_region = "sin"  # Singapore (Đề xuất)
    # Hoặc "hkg" (Hong Kong)
    ```

3.  **Tạo Ổ Đĩa Vĩnh Viễn**
    Câu lệnh này sẽ cấp cho bạn 1 ổ đĩa cứng 1GB tên là `router_data` gắn cố định tại server Singapore (`sin`).
    ```powershell
    flyctl volumes create router_data --region sin --size 1
    ```
    *(Trọng tâm: Phải cấu hình mount trong `fly.toml` theo [mounts] `destination="/data"`).*

---

## 3. Quản lý Không gian Bảo mật (Fly Secrets)

Bạn **TUYỆT ĐỐI KHÔNG** được bỏ API Key (Nvidia, Gemini...) vào file `fly.toml` hoặc `.env` để Deploy, vì nó không an toàn và file `.env` đã bị khóa bởi `.dockerignore`.
Hãy đẩy thẳng Secret lên két sắt mã hóa của Fly.io bằng Terminal ở máy tính (Chỉ phải làm 1 lần duy nhất):

```powershell
# Nạp các API keys AI (Hỗ trợ nhiều key cách nhau bằng dấu phẩy để tự động xoay vòng)
flyctl secrets set GEMINI_API_KEY="key1,key2,..."

flyctl secrets set NVIDIA_API_KEY="key1,key2,..."

flyctl secrets set OPENROUTER_API_KEY="key1,key2,..."

# Gửi yêu cầu cập nhật lại Server để áp dụng Key mới nạp
flyctl secrets deploy
```

> [!TIP]
> **Tính năng Xoay vòng Key (Rotation):** Nếu bạn nhập nhiều key cách nhau bằng dấu phẩy, Router sẽ tự động nhận diện. Khi một key bị lỗi `429` (Hết hạn mức), hệ thống sẽ tự động chuyển sang key tiếp theo và thử lại yêu cầu đó ngay lập tức mà không làm gián đoạn người dùng.

---

## 4. Triển khai Mã Nguồn (Deploy)

### Cách 1: Deploy Thủ Công Chạy 1 Lệnh Ở Máy Tính
Bất cứ khi nào bạn viết code xong ở máy cá nhân, chỉ cần gõ:
```powershell
flyctl deploy
```
*Lệnh này sẽ tự động đọc `Dockerfile`, đẩy code, cài môi trường, gắn ổ đĩa ảo và khởi động lại Server.*

### Cách 2: Tự Động Hóa Qua GitHub Actions (CI/CD)
Project này đã được setup sẵn file `.github/workflows/fly.yml`. Tức là, mỗi lần bạn gõ `git push` lên nhánh `main`, con Robot của Github sẽ thực thi test và tự gõ lệnh `flyctl deploy` thay cho bạn. Bạn cấu hình mồi như sau:

1. **Lấy Token Quyền Lực của Fly:**
   Mở terminal của bạn, gõ lệnh cấp 1 cái chìa khóa tàng hình có tuổi thọ siêu dài:
   ```powershell
   flyctl tokens create deploy -x 99999h
   ```
   *(Nhớ copy dòng mã token vĩ đại vừa in ra)*.

2. **Gắn Két Sắt Trên Github:**
   Vào Github Repo của bạn ➔ **Settings** ➔ **Secrets and variables** ➔ **Actions**:
   - Thêm `FLY_API_TOKEN` - *Dán cái token dài ngoằng lúc nãy vào*.
   - Thêm `NVIDIA_API_KEY`, `GEMINI_API_KEY`,... *(Cái này chỉ để Github chạy lệnh Test qua Pytest chứ không lưu cho Server chạy thật).*

Kể từ giờ, bạn chỉ việc lập trình và `git push`. Action sẽ lo từ A đến Z!

---

## 5. Danh sách Câu lệnh Kiểm tra Lỗi (Debug) Hữu Ích Dưới Terminal

Nếu máy chủ hay App của bạn gặp sự cố, bạn không cần mở Dashboard web, chỉ cần dùng những lệnh siêu mạnh sau:

- Ngó xem **Log Server đang chạy** theo chuỗi thời gian thực (Giống cửa sổ xem Log):
  `flyctl logs -a <tên-app>`

- Ngó xem **Danh Sách Keys (Secrets)** đã nạp thành công chưa:
  `flyctl secrets list`

- Gỡ bỏ / Vứt bỏ **1 Secret bị lỗi**:
  `flyctl secrets unset TEN_BIEN` *(vd: `flyctl secrets unset NVIDIA_API_KEY`)*

- Mở chế độ **SSH truy cập thẳng vào Linux của máy chủ thật**:
  `flyctl ssh console`

- Kiểm tra xem Server hay Máy Ảo có đang **Sống hay Chết (Status)**:
  `flyctl status`

- Kích hoạt **Khởi động lại toàn bộ máy ảo ngay lập tức**:
  `flyctl apps restart <tên-app>`

- Mở thẳng **Trình duyệt tới trang Monitoring** chi tiết:
  `flyctl dashboard`
