from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_file():
    with open("tests/test_document.docx", "rb") as file:
        response = client.post("/upload/", files={"file": ("test_document.docx", file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert response.status_code == 200
    assert "text" in response.json()
