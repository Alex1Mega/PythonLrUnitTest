import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData
from apif import app, get_engine
from db import time_interval

test_engine = create_engine("sqlite:///test.db")
time_interval.metadata.create_all(test_engine)
app.dependency_overrides[get_engine] = lambda: test_engine

class APITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create(self):
        res = self.client.post("/intervals", json={"total_seconds": 3661})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["total_seconds"], 3661)

if __name__ == "__main__":
    unittest.main()