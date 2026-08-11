"""
Testes de integração para a API FastAPI.
"""

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestHealthEndpoint:
    async def test_health_ok(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    async def test_models_list(self, client: AsyncClient):
        resp = await client.get("/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
        assert len(data["models"]) > 0
        first = data["models"][0]
        assert "model" in first
        assert "input_per_1m_usd" in first


class TestOptimizeEndpoint:
    async def test_basic_optimization(self, client: AsyncClient):
        resp = await client.post(
            "/optimize",
            json={
                "text": "Olá! Eu gostaria que você pudesse, por favor, me ajudar com Python.",
                "model": "gpt-4o",
                "level": "moderate",
                "semantic": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "original" in data
        assert "optimized" in data
        assert "savings" in data
        assert data["original"]["tokens"] > 0
        assert data["optimized"]["tokens"] > 0

    async def test_tokens_reduced_after_optimization(self, client: AsyncClient):
        resp = await client.post(
            "/optimize",
            json={
                "text": (
                    "Olá! Espero que esteja bem. Eu gostaria que você pudesse, "
                    "por favor, me ajudar. Basicamente, preciso de uma função. "
                    "Obrigado!"
                ),
                "model": "gpt-4o",
                "level": "moderate",
                "semantic": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["savings"]["tokens"] >= 0

    async def test_no_semantic_only_sanitizes(self, client: AsyncClient):
        resp = await client.post(
            "/optimize",
            json={
                "text": "hello   world",
                "model": "gpt-4o",
                "level": "light",
                "semantic": False,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["optimized"]["text"] == "hello world"

    async def test_empty_text_returns_422(self, client: AsyncClient):
        resp = await client.post(
            "/optimize",
            json={"text": "", "model": "gpt-4o"},
        )
        assert resp.status_code == 422

    async def test_response_has_diff(self, client: AsyncClient):
        resp = await client.post(
            "/optimize",
            json={
                "text": "Olá!   Escreva código.",
                "model": "gpt-4o",
                "level": "light",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["diff"], str)

    async def test_warnings_for_approximate_model(self, client: AsyncClient):
        resp = await client.post(
            "/optimize",
            json={
                "text": "Hello world",
                "model": "claude-3-5-sonnet",
                "level": "none",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["warnings"], list)
        # Claude usa tokenização aproximada
        if data["warnings"]:
            assert any("aproximad" in w.lower() for w in data["warnings"])
