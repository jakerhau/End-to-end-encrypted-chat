"""
Test cases for Group Chat module.
TC-GROUP-001 to TC-GROUP-007
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from bson import ObjectId

from app.db.models.conversation import Conversation, Participant, Group
from app.db.models.group_invite import GroupInvite
from app.core.security import create_access_token


class TestAddMembers:
    """Test cases for adding members to a group."""

    @pytest.mark.asyncio
    async def test_add_members_success(
        self, async_client: AsyncClient, test_user, test_user_2, test_user_3,
        auth_headers, test_db
    ):
        """
        TC-GROUP-001: Thêm thành viên vào group thành công
        """
        # Create a group conversation with type="group"
        conversation = Conversation(
            type="group",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
            group=Group(name="Test Group", created_by=test_user.id),
        )
        await conversation.insert()
        
        payload = {
            "member_ids": [str(test_user_3.id)],
        }
        
        response = await async_client.post(
            f"/api/conversations/{str(conversation.id)}/members",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_add_members_not_group(
        self, async_client: AsyncClient, test_user, test_user_2, test_user_3,
        auth_headers, test_db
    ):
        """
        TC-GROUP-002: Thêm thành viên thất bại - Không phải group
        """
        # Create a direct conversation (not a group)
        conversation = Conversation(
            type="direct",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
        )
        await conversation.insert()
        
        payload = {
            "member_ids": [str(test_user_3.id)],
        }
        
        response = await async_client.post(
            f"/api/conversations/{str(conversation.id)}/members",
            json=payload,
            headers=auth_headers
        )
        
        # Should return error
        assert response.status_code in [400, 403]


class TestInviteLink:
    """Test cases for invite link management."""

    @pytest.mark.asyncio
    async def test_create_invite_link_success(
        self, async_client: AsyncClient, test_user, test_user_2,
        auth_headers, test_db
    ):
        """
        TC-GROUP-003: Tạo invite link thành công
        """
        # Create a group conversation
        conversation = Conversation(
            type="group",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
            group=Group(name="Test Group", created_by=test_user.id),
        )
        await conversation.insert()
        
        response = await async_client.post(
            f"/api/conversations/{str(conversation.id)}/invite-link",
            headers=auth_headers,
            params={"expires_days": 7}
        )
        
        assert response.status_code == 200


class TestJoinGroup:
    """Test cases for joining groups via invite code."""

    @pytest.mark.asyncio
    async def test_join_group_via_invite_success(
        self, async_client: AsyncClient, test_user, test_user_2, test_user_3,
        auth_headers, test_db
    ):
        """
        TC-GROUP-004: Join group qua invite code thành công
        """
        # Create a group conversation
        conversation = Conversation(
            type="group",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
            group=Group(name="Test Group", created_by=test_user.id),
        )
        await conversation.insert()
        
        # Create an invite
        invite = GroupInvite(
            conversation_id=conversation.id,
            invite_code="TEST_INVITE_CODE_123",
            created_by=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        await invite.insert()
        
        # User3 joins using the invite code
        user3_headers = {"Authorization": f"Bearer {create_access_token(str(test_user_3.id))}"}
        
        payload = {
            "invite_code": "TEST_INVITE_CODE_123",
        }
        
        response = await async_client.post(
            "/api/conversations/join-group",
            json=payload,
            headers=user3_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_join_group_expired_code(
        self, async_client: AsyncClient, test_user, test_user_2, test_user_3,
        auth_headers, test_db
    ):
        """
        TC-GROUP-005: Join group thất bại - Code hết hạn
        """
        # Create a group conversation
        conversation = Conversation(
            type="group",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
            group=Group(name="Test Group", created_by=test_user.id),
        )
        await conversation.insert()
        
        # Create an expired invite
        invite = GroupInvite(
            conversation_id=conversation.id,
            invite_code="EXPIRED_CODE_456",
            created_by=test_user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired
        )
        await invite.insert()
        
        user3_headers = {"Authorization": f"Bearer {create_access_token(str(test_user_3.id))}"}
        
        payload = {
            "invite_code": "EXPIRED_CODE_456",
        }
        
        response = await async_client.post(
            "/api/conversations/join-group",
            json=payload,
            headers=user3_headers
        )
        
        assert response.status_code in [400, 404, 410]

    @pytest.mark.asyncio
    async def test_join_group_already_member(
        self, async_client: AsyncClient, test_user, test_user_2,
        auth_headers, test_db
    ):
        """
        TC-GROUP-006: Join group - Đã là thành viên
        """
        # Create a group conversation where test_user is already a member
        conversation = Conversation(
            type="group",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
            group=Group(name="Test Group", created_by=test_user.id),
        )
        await conversation.insert()
        
        # Create an invite
        invite = GroupInvite(
            conversation_id=conversation.id,
            invite_code="ALREADY_MEMBER_CODE_789",
            created_by=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        await invite.insert()
        
        # test_user (already a member) tries to join again
        payload = {
            "invite_code": "ALREADY_MEMBER_CODE_789",
        }
        
        response = await async_client.post(
            "/api/conversations/join-group",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True


class TestLeaveGroup:
    """Test cases for leaving a group."""

    @pytest.mark.asyncio
    async def test_leave_group_success(
        self, async_client: AsyncClient, test_user, test_user_2, test_user_3,
        auth_headers_user2, test_db
    ):
        """
        TC-GROUP-007: Rời nhóm thành công
        """
        # Create a group with 3 members (so when one leaves, min_items=2 is satisfied)
        conversation = Conversation(
            type="group",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_3.id, joined_at=datetime.now(timezone.utc)),
            ],
            group=Group(name="Test Group", created_by=test_user.id),
        )
        await conversation.insert()
        
        # User2 leaves the group
        response = await async_client.delete(
            f"/api/conversations/{str(conversation.id)}/leave",
            headers=auth_headers_user2
        )
        
        assert response.status_code == 200

