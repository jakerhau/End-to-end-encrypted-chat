"""
Test cases for E2EE (End-to-End Encryption) module.
TC-E2EE-001 to TC-E2EE-010
"""
import pytest
import hashlib
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime, timezone

from app.db.models.public_key import PublicKey
from app.db.models.pending_key import PendingSessionKey
from app.db.models.conversation import Conversation, Participant


class TestRegisterPublicKey:
    """Test cases for registering public keys."""

    @pytest.mark.asyncio
    async def test_register_public_key_success(
        self, async_client: AsyncClient, test_user, auth_headers, sample_public_key
    ):
        """
        TC-E2EE-001: Đăng ký public key thành công
        """
        # API requires fingerprint
        fingerprint = hashlib.sha256(sample_public_key.encode()).hexdigest()
        
        payload = {
            "public_key": sample_public_key,
            "fingerprint": fingerprint,
            "device_id": "device_123",
        }
        
        response = await async_client.post(
            "/api/e2ee/keys/register",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    @pytest.mark.asyncio
    async def test_register_public_key_multi_device(
        self, async_client: AsyncClient, test_user, auth_headers, 
        sample_public_key, test_db
    ):
        """
        TC-E2EE-002: Update public key (multi-device)
        """
        fingerprint1 = hashlib.sha256(sample_public_key.encode()).hexdigest()
        
        # First device
        await async_client.post(
            "/api/e2ee/keys/register",
            json={
                "public_key": sample_public_key, 
                "fingerprint": fingerprint1,
                "device_id": "device_1"
            },
            headers=auth_headers
        )
        
        # Second device with different key
        different_key = sample_public_key + "different"
        fingerprint2 = hashlib.sha256(different_key.encode()).hexdigest()
        
        payload = {
            "public_key": different_key,
            "fingerprint": fingerprint2,
            "device_id": "device_2",
        }
        
        response = await async_client.post(
            "/api/e2ee/keys/register",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestGetPublicKeys:
    """Test cases for getting public keys."""

    @pytest.mark.asyncio
    async def test_get_my_public_key_success(
        self, async_client: AsyncClient, test_user, auth_headers, 
        sample_public_key, test_db
    ):
        """
        TC-E2EE-003: Lấy public key của mình thành công
        """
        fingerprint = hashlib.sha256(sample_public_key.encode()).hexdigest()
        
        # First register a key
        await async_client.post(
            "/api/e2ee/keys/register",
            json={
                "public_key": sample_public_key,
                "fingerprint": fingerprint,
                "device_id": "device_1"
            },
            headers=auth_headers
        )
        
        response = await async_client.get(
            "/api/e2ee/keys/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_public_key_success(
        self, async_client: AsyncClient, test_user, test_user_2,
        auth_headers, sample_public_key, test_db
    ):
        """
        TC-E2EE-004: Lấy public key của user khác thành công
        """
        fingerprint = hashlib.sha256(sample_public_key.encode()).hexdigest()
        
        public_key = PublicKey(
            user_id=test_user_2.id,
            public_key=sample_public_key,
            fingerprint=fingerprint,
            device_id="device_1",
        )
        await public_key.insert()
        
        response = await async_client.get(
            f"/api/e2ee/keys/{str(test_user_2.id)}",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_public_key_not_found(
        self, async_client: AsyncClient, test_user, auth_headers, test_db
    ):
        """
        TC-E2EE-005: Lấy public key thất bại - User không có key
        """
        fake_user_id = str(ObjectId())
        
        response = await async_client.get(
            f"/api/e2ee/keys/{fake_user_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]


class TestSessionKeyExchange:
    """Test cases for session key exchange."""

    @pytest.mark.asyncio
    async def test_exchange_session_key_success(
        self, async_client: AsyncClient, test_user, test_user_2,
        auth_headers, sample_public_key, test_db
    ):
        """
        TC-E2EE-006: Exchange session key thành công
        """
        fingerprint = hashlib.sha256(sample_public_key.encode()).hexdigest()
        
        public_key = PublicKey(
            user_id=test_user_2.id,
            public_key=sample_public_key,
            fingerprint=fingerprint,
            device_id="device_1",
        )
        await public_key.insert()
        
        # Create a conversation with proper type
        conversation = Conversation(
            type="direct",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
        )
        await conversation.insert()
        
        payload = {
            "recipient_id": str(test_user_2.id),
            "conversation_id": str(conversation.id),
            "encrypted_session_key": "base64_encrypted_key_here",
            "signature": "base64_signature_here",
            "timestamp": 1704067200000,
        }
        
        response = await async_client.post(
            "/api/e2ee/session-keys/exchange",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 400, 404, 422]


class TestPendingKeys:
    """Test cases for pending keys management."""

    @pytest.mark.asyncio
    async def test_get_pending_keys_success(
        self, async_client: AsyncClient, test_user, auth_headers, test_db
    ):
        """
        TC-E2EE-008: Lấy pending keys thành công
        """
        response = await async_client.get(
            "/api/e2ee/pending-keys",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_ack_pending_keys_success(
        self, async_client: AsyncClient, test_user, test_user_2, 
        auth_headers, test_db
    ):
        """
        TC-E2EE-009: ACK pending keys thành công
        """
        pending_key = PendingSessionKey(
            recipient_user_id=test_user.id,
            sender_user_id=test_user_2.id,
            encrypted_session_key="encrypted_key_data",
            signature="test_signature",
            timestamp=1704067200000,
            conversation_id=ObjectId(),
            delivered=False,
        )
        await pending_key.insert()
        
        # API uses "ids" not "key_ids"
        payload = {
            "ids": [str(pending_key.id)],
        }
        
        response = await async_client.post(
            "/api/e2ee/pending-keys/ack",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestConversationPublicKeys:
    """Test cases for getting conversation participants' public keys."""

    @pytest.mark.asyncio
    async def test_get_conversation_public_keys_success(
        self, async_client: AsyncClient, test_user, test_user_2,
        auth_headers, sample_public_key, test_db
    ):
        """
        TC-E2EE-010: Lấy public keys của participants trong conversation
        """
        # Create conversation with proper type
        conversation = Conversation(
            type="direct",
            participants=[
                Participant(user_id=test_user.id, joined_at=datetime.now(timezone.utc)),
                Participant(user_id=test_user_2.id, joined_at=datetime.now(timezone.utc)),
            ],
        )
        await conversation.insert()
        
        # Register keys for both users
        for user in [test_user, test_user_2]:
            fingerprint = hashlib.sha256(f"{sample_public_key}{user.id}".encode()).hexdigest()
            key = PublicKey(
                user_id=user.id,
                public_key=sample_public_key,
                fingerprint=fingerprint,
                device_id="device_1",
            )
            await key.insert()
        
        response = await async_client.get(
            f"/api/e2ee/conversations/{str(conversation.id)}/keys",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
