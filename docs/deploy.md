# Deploy Discord RAG Bot

Bot này là **background worker**. Không deploy như web service vì bot không mở HTTP port.

## Chuẩn bị

1. Trong Discord Developer Portal, bật **Message Content Intent** và **Server Members Intent** cho bot.
2. Bảo đảm `data/discord/faiss.index` và `data/discord/metadata.json` có trong image deploy. Nếu thay đổi model embedding hoặc dữ liệu, chạy `python scripts/build_index.py` trước khi deploy.
3. Dùng model `intfloat/multilingual-e5-large`: index hiện có 1024 dimensions và phải khớp model này.

## Render

1. Push repository lên private Git repository và tạo **Background Worker** mới trên Render.
2. Chọn file `render.yaml` khi tạo Blueprint (hoặc để Render tự nhận diện file này).
3. Nhập secret trong Render dashboard: `DISCORD_TOKEN`, `DISCORD_GUILD_ID`, `OPENAI_API_KEY`.
4. Deploy. Lần khởi động đầu có thể lâu hơn vì SentenceTransformer tải model embedding.

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
