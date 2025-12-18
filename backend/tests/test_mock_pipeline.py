from fastapi.testclient import TestClient
from PIL import Image
from io import BytesIO

from backend.main import app


def test_mock_analysis_pipeline(monkeypatch, tmp_path):
    # Force mock mode
    monkeypatch.setenv("USE_MOCK_OPENAI", "true")

    client = TestClient(app)

    # Build a real PNG to exercise DocumentProcessor without hitting OpenAI
    img = Image.new("RGB", (2, 2), color=(255, 0, 0))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()
    files = {
        "accident_report": ("report.png", png_bytes, "image/png"),
    }

    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["status"] == "success"
    assert body["analysis"]["case_summary"].startswith("Mock")
