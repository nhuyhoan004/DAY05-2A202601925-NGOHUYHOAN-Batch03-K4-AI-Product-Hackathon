# Deploy Discord RAG Bot

Bot này là **background worker**. Không deploy như web service vì bot không mở HTTP port.

## Chuẩn bị

1. Trong Discord Developer Portal, bật **Message Content Intent** và **Server Members Intent** cho bot.
2. Bảo đảm `data/discord/faiss.index` và `data/discord/metadata.json` có trong image deploy. Nếu thay đổi model embedding, số chiều hoặc dữ liệu, chạy `python scripts/build_index.py` trước khi deploy.
3. Index hiện dùng OpenRouter model `openai/text-embedding-3-small` với 1024 dimensions.

## Render

1. Push repository lên private Git repository và tạo **Background Worker** mới trên Render.
2. Chọn file `render.yaml` khi tạo Blueprint (hoặc để Render tự nhận diện file này).
3. Nhập secret trong Render dashboard: `DISCORD_TOKEN`, `DISCORD_GUILD_ID`, `OPENROUTER_API_KEY` (có thể dùng `OPENAI_API_KEY` cho cấu hình tương thích cũ).
4. Deploy. Worker gọi OpenRouter cho cả chat và embedding, không tải model embedding local.

## Railway

1. Tạo project mới từ GitHub repository. Railway tự nhận diện `railway.json` và `Dockerfile`.
2. Thêm cùng ba secret ở mục **Variables**.
3. Deploy và kiểm tra log có dòng bot đã đăng nhập thành công.

## Kiểm tra sau deploy

- Slash command `/ask` xuất hiện trong Discord server.
- Gửi một câu hỏi có dữ liệu trong knowledge base và kiểm tra câu trả lời có nguồn.
- Kiểm tra worker vẫn hoạt động sau ít nhất một chu kỳ đồng bộ 15 phút.

## Bảo mật dữ liệu

Không đưa `data/discord/` lên public repository. Nếu cần deploy public, thay bằng data demo đã được phê duyệt hoặc dùng private storage; không commit `.env` hay token vào Git.
