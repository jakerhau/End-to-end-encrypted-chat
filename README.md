# 🔐 End-to-End Encrypted Chat

Ứng dụng nhắn tin bảo mật với mã hóa đầu cuối (E2EE), được xây dựng với React và FastAPI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-19-61DAFB.svg)

## 📋 Tổng quan

Đây là ứng dụng chat bảo mật cho phép người dùng giao tiếp với nhau thông qua các cuộc hội thoại được mã hóa đầu cuối (End-to-End Encryption). Tin nhắn chỉ có thể được đọc bởi người gửi và người nhận, ngay cả server cũng không thể giải mã nội dung.

### ✨ Tính năng chính

- **🔒 Mã hóa đầu cuối (E2EE)**: Tin nhắn được mã hóa bằng AES-GCM với khóa phiên trao đổi qua RSA
- **👥 Chat trực tiếp**: Nhắn tin 1-1 với bạn bè
- **👨‍👩‍👧‍👦 Chat nhóm**: Tạo và quản lý nhóm chat với nhiều thành viên
- **🤝 Hệ thống kết bạn**: Gửi/nhận lời mời kết bạn
- **🔗 Liên kết mời nhóm**: Chia sẻ link mời tham gia nhóm
- **⚡ Realtime**: Cập nhật tin nhắn theo thời gian thực qua WebSocket
- **🎨 Giao diện hiện đại**: UI đẹp mắt với dark mode support
- **📱 Emoji**: Hỗ trợ gửi emoji trong tin nhắn

## 🏗️ Kiến trúc

```
DuAnCNTT/
├── backend/          # FastAPI Server
│   ├── app/
│   │   ├── api/          # HTTP & WebSocket endpoints
│   │   ├── core/         # Cấu hình & bảo mật
│   │   ├── cryptography/ # Thuật toán mã hóa E2EE
│   │   ├── db/           # Models & Repositories (MongoDB)
│   │   ├── services/     # Business logic
│   │   └── ws/           # WebSocket management
│   └── tests/            # Unit & Integration tests
│
└── frontend/         # React Application
    └── src/
        ├── components/   # UI Components
        ├── pages/        # Các trang chính
        ├── services/     # API services
        ├── stores/       # Zustand state management
        ├── lib/          # Crypto & utilities
        └── types/        # TypeScript types
```

## 🛠️ Công nghệ sử dụng

### Backend
| Công nghệ | Mô tả |
|-----------|-------|
| **FastAPI** | Framework Python hiệu năng cao |
| **MongoDB** | Database NoSQL với Beanie ODM |
| **WebSocket** | Giao tiếp realtime |
| **JWT** | Authentication tokens |
| **RSA + AES-GCM** | Mã hóa E2EE |

### Frontend
| Công nghệ | Mô tả |
|-----------|-------|
| **React 19** | UI Library |
| **TypeScript** | Type safety |
| **Vite** | Build tool nhanh |
| **TailwindCSS** | Utility-first CSS |
| **Zustand** | State management |
| **Socket.io** | WebSocket client |
| **Radix UI** | Accessible components |

## 🚀 Cài đặt & Chạy

### Yêu cầu
- Python 3.10+
- Node.js 18+
- MongoDB

### Backend

```bash
cd backend

# Tạo môi trường ảo
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
uvicorn app.main:app --reload
```

> **Lưu ý Windows**: Nếu gặp lỗi PowerShell script, chạy:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

### Biến môi trường

Tạo file `.env` trong thư mục `backend/`:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=e2ee_chat
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔐 Cách hoạt động E2EE

1. **Tạo cặp khóa**: Mỗi user tạo cặp RSA key (public/private) khi đăng ký
2. **Trao đổi khóa**: Khi bắt đầu chat, session key được trao đổi qua RSA
3. **Mã hóa tin nhắn**: Tin nhắn được mã hóa bằng AES-GCM với session key
4. **Xác thực**: Chữ ký RSA-PSS đảm bảo tính toàn vẹn của tin nhắn

```
┌─────────┐                              ┌─────────┐
│  User A │                              │  User B │
└────┬────┘                              └────┬────┘
     │  1. Exchange RSA public keys           │
     │◄──────────────────────────────────────►│
     │                                        │
     │  2. Generate & encrypt session key     │
     │───────────────────────────────────────►│
     │                                        │
     │  3. Encrypt message with AES-GCM       │
     │───────────────────────────────────────►│
     │                                        │
     │  4. Decrypt with shared session key    │
     │                                        │
```
**Nguyên tắc chính:**
- Client tạo khóa RSA, public key đăng ký lên server; private key lưu cục bộ và được mã hóa bằng PIN.
- Mỗi cuộc hội thoại sử dụng khóa AES session (group có key_version), nội dung tin nhắn được mã hóa bằng AES-GCM.
- Server không giải mã; chỉ lưu ciphertext + metadata, phát tán qua WebSocket.
- Khi user offline, session key được lưu vào pending-keys và được client ACK sau khi xử lý.

## API & WebSocket

### REST API (prefix `/api`)
Auth:
- `POST /api/auth/signup`
- `POST /api/auth/signin`
- `POST /api/auth/refresh-token`
- `POST /api/auth/logout`

Users:
- `GET /api/users/me`
- `GET /api/users/search?username=...`

Friends:
- `POST /api/friends/requests`
- `POST /api/friends/requests/{request_id}/accept`
- `POST /api/friends/requests/{request_id}/decline`
- `GET /api/friends`
- `GET /api/friends/requests`

Conversations:
- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/{conversation_id}/messages`
- `PATCH /api/conversations/{conversation_id}/seen`
- `DELETE /api/conversations/{conversation_id}`
- `POST /api/conversations/{conversation_id}/members`
- `POST /api/conversations/{conversation_id}/invite-link`
- `POST /api/conversations/join-group`
- `DELETE /api/conversations/{conversation_id}/leave`

Messages:
- `POST /api/messages/direct`
- `POST /api/messages/group`
- `POST /api/chats/{conversation_id}/messages` (luu ciphertext/metadata)

E2EE:
- `POST /api/e2ee/keys/register`
- `GET /api/e2ee/keys/me`
- `GET /api/e2ee/keys/{user_id}`
- `GET /api/e2ee/keys/conversation/{conversation_id}`
- `POST /api/e2ee/session/exchange`
- `GET /api/e2ee/pending-keys`
- `POST /api/e2ee/pending-keys/ack`

Chi tiet day du: `http://localhost:8000/docs`

### WebSocket
Ket noi: `ws://localhost:8000/ws?token=<ACCESS_TOKEN>`

Su kien tu client:
- `ping`
- `join-conversation` (payload: `conversationId`)

Su kien tu server:
- `online-users`
- `new-message`
- `new-group`
- `group-members-added`
- `group-members-removed`
- `session-key-exchange`
- `pong`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📁 Scripts

| Script | Mô tả |
|--------|-------|
| `npm run dev` | Chạy frontend dev server |
| `npm run build` | Build production |
| `npm run test` | Chạy unit tests |
| `uvicorn app.main:app --reload` | Chạy backend dev server |
| `pytest` | Chạy backend tests |

## 👥 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Made with ❤️ for secure communication
</p>
