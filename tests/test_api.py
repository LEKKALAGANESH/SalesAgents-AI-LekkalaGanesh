import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app


class RetellAdapterTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.secret = "test-retell-secret"

    def test_health_is_public(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_retell_endpoint_is_disabled_without_secret(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post("/retell/lap-qualification", json={"facts": {}})
        self.assertEqual(response.status_code, 503)

    def test_retell_endpoint_rejects_bad_secret(self):
        with patch.dict(os.environ, {"RETELL_WEBHOOK_SECRET": self.secret}):
            response = self.client.post(
                "/retell/lap-qualification",
                headers={"Authorization": "Bearer wrong-secret"},
                json={"session_id": "api-test-unauthorized", "customer_verified": True, "facts": {}},
            )
        self.assertEqual(response.status_code, 401)

    def test_retell_endpoint_qualifies_eligible_customer(self):
        payload = {
            "args": {
                "session_id": "api-test-eligible",
                "customer_verified": True,
                "facts": {
                    "property_type": "residential",
                    "ownership_status": "joint",
                    "documents_available": True,
                    "loan_amount": 5_000_000,
                    "occupation": "salaried",
                    "income_mode": "bank",
                    "market_value": 10_000_000,
                    "tenure_years": 10,
                },
            }
        }
        with patch.dict(os.environ, {"RETELL_WEBHOOK_SECRET": self.secret}):
            response = self.client.post(
                "/retell/lap-qualification",
                headers={"Authorization": f"Bearer {self.secret}"},
                json=payload,
            )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["terminal_outcome"], "QUALIFIED_FOR_EXPERT_FOLLOWUP")
        self.assertTrue(result["qualified"])
        self.assertEqual(result["action"], "QUALIFIED_HANDOFF_AND_END")
        self.assertEqual(result["missing_fields"], [])

    def test_retell_endpoint_routes_transfer_case(self):
        payload = {
            "session_id": "api-test-transfer",
            "customer_verified": True,
            "existing_property_loan": True,
            "facts": {},
        }
        with patch.dict(os.environ, {"RETELL_WEBHOOK_SECRET": self.secret}):
            response = self.client.post(
                "/retell/lap-qualification",
                headers={"X-Retell-Webhook-Secret": self.secret},
                json=payload,
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["terminal_outcome"], "TRANSFER_SPECIALIST_FOLLOWUP")

    def test_retell_endpoint_rejects_unknown_fact_fields(self):
        payload = {
            "session_id": "api-test-invalid",
            "customer_verified": True,
            "facts": {"property_type": "residential", "made_up_policy": True},
        }
        with patch.dict(os.environ, {"RETELL_WEBHOOK_SECRET": self.secret}):
            response = self.client.post(
                "/retell/lap-qualification",
                headers={"Authorization": f"Bearer {self.secret}"},
                json=payload,
            )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
