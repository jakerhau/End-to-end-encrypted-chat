"""
Pytest configuration and fixtures for E2EE Chat Application tests.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock, MagicMock

from app.db.models.user import User
from app.db.models.friend import Friend
from app.db.models.friend_request import FriendRequest
from app.db.models.token import Token
from app.db.models.message import Message
from app.db.models.public_key import PublicKey
from app.db.models.conversation import Conversation, Participant, Group, LastMessage
from app.db.models.pending_key import PendingSessionKey
from app.db.models.group_invite import GroupInvite
from app.core.security import create_access_token
from app.utils.hashing import hash_password


# Test database configuration
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DATABASE_NAME = "test_e2ee_chat"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database connection and initialize Beanie for all models."""
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    db = client[TEST_DATABASE_NAME]
    
    # Initialize Beanie with ALL document models (same as app/db/session.py)
    await init_beanie(
        database=db,
        document_models=[
            User,
            Friend,
            FriendRequest,
            Token,
            Message,
            PublicKey,
            Conversation,
            Participant,
            Group,
            LastMessage,
            PendingSessionKey,
            GroupInvite,
        ]
    )
    
    yield db
    
    # Cleanup: Drop test database after each test
    await client.drop_database(TEST_DATABASE_NAME)
    client.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db):
    """Create an async HTTP client for testing API endpoints."""
    # Import app AFTER test_db is initialized so Beanie is ready
    from app.main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
        display_name="Test User",
    )
    await user.insert()
    return user


@pytest_asyncio.fixture
async def test_user_2(test_db):
    """Create a second test user."""
    user = User(
        username="testuser2",
        email="testuser2@example.com",
        hashed_password=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User2",
        display_name="Test User 2",
    )
    await user.insert()
    return user


@pytest_asyncio.fixture
async def test_user_3(test_db):
    """Create a third test user for group tests."""
    user = User(
        username="testuser3",
        email="testuser3@example.com",
        hashed_password=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User3",
        display_name="Test User 3",
    )
    await user.insert()
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Generate authentication headers for test user."""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_user2(test_user_2):
    """Generate authentication headers for test user 2."""
    token = create_access_token(str(test_user_2.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_public_key():
    """Sample RSA public key for testing (Base64 encoded)."""
    return (
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/"
        "ygWyf8dz0WLsKpDD+x3mXMKLcBpVzWwaXhPJqvKspFntFNrCdFVkWxgP0M5U"
        "ej7LpRJ8Y3nBTG3HeF5rnCM9GkqmWL8mOx4PwGHG7t0o4E7Kz2TKEu+JsFwv"
        "EO7sDGKp3m+Q4VGULnP/tzfqdcdzLLuK1YDjXVR/9NM5TZJxJfCpN3qVh8mB"
        "HaC3QYG5hqK2xHJ3X5lEwzFNh2Bw6dVX0r3TpPVxZS7j0ov0a3m6B0xvM+Qx"
        "nNvK7t2JzS1V9YmJvIaL3G+PSfVKnBkxL0OJmS+mC7YVGxd5DvZVGxF7BxMV"
        "0p3xvBNJVLP3YwZJZoS3ZwIDAQAB"
    )


@pytest.fixture
def sample_session_key():
    """Sample AES-256 session key for testing (Base64 encoded)."""
    return "dGhpcyBpcyBhIDMyIGJ5dGUga2V5ISE="


@pytest.fixture
def sample_encrypted_message():
    """Sample encrypted message for testing."""
    return {
        "ciphertext": "SGVsbG8gV29ybGQh",
        "counter": 1,
    }


@pytest.fixture
def mock_ws_manager():
    """Mock WebSocket connection manager."""
    manager = MagicMock()
    manager.send_to_user = AsyncMock()
    manager.broadcast_to_conversation = AsyncMock()
    return manager
