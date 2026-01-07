"""
Test cases for Authentication module.
TC-AUTH-001 to TC-AUTH-010
"""
import pytest
from httpx import AsyncClient


class TestSignup:
    """Test cases for user registration (signup) endpoint."""

    @pytest.mark.asyncio
    async def test_signup_success(self, async_client: AsyncClient, test_db):
        """
        TC-AUTH-001: Đăng ký tài khoản thành công
        """
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "firstname": "New",
            "lastname": "User",
        }
        
        response = await async_client.post("/api/auth/signup", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Đăng ký thành công"

    @pytest.mark.asyncio
    async def test_signup_duplicate_username(self, async_client: AsyncClient, test_user):
        """
        TC-AUTH-002: Đăng ký thất bại - Username đã tồn tại
        """
        payload = {
            "username": "testuser",  # Same as test_user fixture
            "email": "different@example.com",
            "password": "SecurePass123!",
            "firstname": "Test",
            "lastname": "User",
        }
        
        response = await async_client.post("/api/auth/signup", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        # Check for error message in either 'detail' (HTTPException) or 'message' (custom response)
        error_msg = data.get("detail") or data.get("message", "")
        assert "Username đã tồn tại" in error_msg

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, async_client: AsyncClient, test_user):
        """
        TC-AUTH-003: Đăng ký thất bại - Email đã tồn tại
        """
        payload = {
            "username": "differentuser",
            "email": "testuser@example.com",  # Same as test_user fixture
            "password": "SecurePass123!",
            "firstname": "Test",
            "lastname": "User",
        }
        
        response = await async_client.post("/api/auth/signup", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail") or data.get("message", "")
        assert "Email đã tồn tại" in error_msg


class TestSignin:
    """Test cases for user login (signin) endpoint."""

    @pytest.mark.asyncio
    async def test_signin_success(self, async_client: AsyncClient, test_user):
        """
        TC-AUTH-004: Đăng nhập thành công
        """
        payload = {
            "username": "testuser",
            "password": "TestPassword123!",
        }
        
        response = await async_client.post("/api/auth/signin", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        # Check refresh_token cookie is set
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_signin_wrong_username(self, async_client: AsyncClient, test_db):
        """
        TC-AUTH-005: Đăng nhập thất bại - Username sai
        """
        payload = {
            "username": "nonexistent",
            "password": "anypassword",
        }
        
        response = await async_client.post("/api/auth/signin", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail") or data.get("message", "")
        assert "Username hoặc mật khẩu không chính xác" in error_msg

    @pytest.mark.asyncio
    async def test_signin_wrong_password(self, async_client: AsyncClient, test_user):
        """
        TC-AUTH-006: Đăng nhập thất bại - Password sai
        """
        payload = {
            "username": "testuser",
            "password": "WrongPassword!",
        }
        
        response = await async_client.post("/api/auth/signin", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail") or data.get("message", "")
        assert "Username hoặc mật khẩu không chính xác" in error_msg


class TestRefreshToken:
    """Test cases for refresh token endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client: AsyncClient, test_user):
        """
        TC-AUTH-007: Refresh token thành công
        """
        # First, login to get refresh token
        login_response = await async_client.post(
            "/api/auth/signin",
            json={"username": "testuser", "password": "TestPassword123!"}
        )
        cookies = login_response.cookies
        
        # Use refresh token to get new access token
        response = await async_client.post(
            "/api/auth/refresh-token",
            cookies=cookies
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    @pytest.mark.asyncio
    async def test_refresh_token_missing(self, async_client: AsyncClient, test_db):
        """
        TC-AUTH-008: Refresh token thất bại - Token không tồn tại
        """
        response = await async_client.post("/api/auth/refresh-token")
        
        assert response.status_code == 401
        data = response.json()
        error_msg = data.get("detail") or data.get("message", "")
        assert "Missing refresh token" in error_msg or "refresh token" in error_msg.lower()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client: AsyncClient, test_db):
        """
        TC-AUTH-009: Refresh token thất bại - Token không hợp lệ
        """
        response = await async_client.post(
            "/api/auth/refresh-token",
            cookies={"refresh_token": "invalid_token_here"}
        )
        
        assert response.status_code == 401


class TestLogout:
    """Test cases for logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, test_user):
        """
        TC-AUTH-010: Đăng xuất thành công
        """
        # First, login to get refresh token
        login_response = await async_client.post(
            "/api/auth/signin",
            json={"username": "testuser", "password": "TestPassword123!"}
        )
        cookies = login_response.cookies
        
        # Logout
        response = await async_client.post(
            "/api/auth/logout",
            cookies=cookies
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Đăng xuất thành công"
        
        # Verify refresh token cookie is deleted
        # (Cookie should be set with empty value or expired)
