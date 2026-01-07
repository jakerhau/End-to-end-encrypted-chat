"""
Test cases for Friends module.
TC-FRIEND-001 to TC-FRIEND-007
"""
import pytest
from httpx import AsyncClient
from bson import ObjectId

from app.db.models.friend_request import FriendRequest


class TestSendFriendRequest:
    """Test cases for sending friend requests."""

    @pytest.mark.asyncio
    async def test_send_friend_request_success(
        self, async_client: AsyncClient, test_user, test_user_2, auth_headers
    ):
        """
        TC-FRIEND-001: Gửi friend request thành công
        """
        # Correct payload format: to_user instead of receiver_id
        payload = {
            "to_user": str(test_user_2.id),
            "message": "Hello, let's be friends!",
        }
        
        response = await async_client.post(
            "/api/friends/requests",
            json=payload,
            headers=auth_headers
        )
        
        # Accept both 200 and 201 for success
        assert response.status_code in [200, 201]
        data = response.json()
        assert data.get("success") is True

    @pytest.mark.asyncio
    async def test_send_friend_request_user_not_found(
        self, async_client: AsyncClient, test_user, auth_headers
    ):
        """
        TC-FRIEND-002: Gửi friend request thất bại - User không tồn tại
        """
        payload = {
            "to_user": str(ObjectId()),  # Non-existent user
            "message": "",
        }
        
        response = await async_client.post(
            "/api/friends/requests",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 404, 422]

    @pytest.mark.asyncio
    async def test_send_friend_request_already_sent(
        self, async_client: AsyncClient, test_user, test_user_2, auth_headers, test_db
    ):
        """
        TC-FRIEND-003: Gửi friend request thất bại - Đã gửi request trước đó
        """
        # First, create an existing friend request
        friend_request = FriendRequest(
            from_user=test_user.id,
            to_user=test_user_2.id,
        )
        await friend_request.insert()
        
        payload = {
            "to_user": str(test_user_2.id),
            "message": "",
        }
        
        response = await async_client.post(
            "/api/friends/requests",
            json=payload,
            headers=auth_headers
        )
        
        # Should return error (duplicate request)
        assert response.status_code in [400, 409]


class TestAcceptFriendRequest:
    """Test cases for accepting friend requests."""

    @pytest.mark.asyncio
    async def test_accept_friend_request_success(
        self, async_client: AsyncClient, test_user, test_user_2, 
        auth_headers_user2, test_db
    ):
        """
        TC-FRIEND-004: Chấp nhận friend request thành công
        """
        # Create a pending friend request from user1 to user2
        friend_request = FriendRequest(
            from_user=test_user.id,
            to_user=test_user_2.id,
        )
        await friend_request.insert()
        
        # User2 accepts the request
        response = await async_client.post(
            f"/api/friends/requests/{str(friend_request.id)}/accept",
            headers=auth_headers_user2
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    @pytest.mark.asyncio
    async def test_accept_friend_request_not_receiver(
        self, async_client: AsyncClient, test_user, test_user_2, test_user_3,
        auth_headers, test_db
    ):
        """
        TC-FRIEND-005: Chấp nhận thất bại - Request không phải của mình
        """
        # Create a pending friend request from user2 to user3
        friend_request = FriendRequest(
            from_user=test_user_2.id,
            to_user=test_user_3.id,
        )
        await friend_request.insert()
        
        # User1 (test_user) tries to accept - should fail
        response = await async_client.post(
            f"/api/friends/requests/{str(friend_request.id)}/accept",
            headers=auth_headers
        )
        
        assert response.status_code in [400, 403, 404]


class TestDeclineFriendRequest:
    """Test cases for declining friend requests."""

    @pytest.mark.asyncio
    async def test_decline_friend_request_success(
        self, async_client: AsyncClient, test_user, test_user_2,
        auth_headers_user2, test_db
    ):
        """
        TC-FRIEND-006: Từ chối friend request thành công
        """
        # Create a pending friend request from user1 to user2
        friend_request = FriendRequest(
            from_user=test_user.id,
            to_user=test_user_2.id,
        )
        await friend_request.insert()
        
        # User2 declines the request
        response = await async_client.post(
            f"/api/friends/requests/{str(friend_request.id)}/decline",
            headers=auth_headers_user2
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True


class TestGetFriends:
    """Test cases for getting friends list."""

    @pytest.mark.asyncio
    async def test_get_all_friends_success(
        self, async_client: AsyncClient, test_user, auth_headers
    ):
        """
        TC-FRIEND-007: Lấy danh sách bạn bè thành công
        """
        response = await async_client.get(
            "/api/friends/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert isinstance(data.get("data"), list)
