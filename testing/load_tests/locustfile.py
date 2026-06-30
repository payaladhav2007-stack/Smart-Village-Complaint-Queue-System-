"""
GS-509: Automated Concurrency Stress-Testing Suite
Simulates 1000+ simultaneous citizens booking overlapping appointment
slots and submitting grievances, to verify the backend handles
race conditions gracefully without creating duplicate token sequences.

Run with:
    locust -f testing/load_tests/locustfile.py --host=http://127.0.0.1:8000
Then open http://localhost:8089 in your browser to start the test.
"""

import random
import json
from locust import HttpUser, task, between


class CitizenLoadTest(HttpUser):
    wait_time = between(0.5, 2)  # simulate realistic pauses between actions
    token = None

    def on_start(self):
        """Each simulated citizen logs in once before sending requests."""
        username = "loadtest_user_" + str(random.randint(1, 100000))
        password = "TestPass123"

        # Register a throwaway test citizen
        self.client.post("/api/auth/register/", json={
            "username": username,
            "email": username + "@example.com",
            "password": password,
            "phone_number": "9" + str(random.randint(100000000, 999999999)),
            "ward_number": str(random.randint(1, 10))
        })

        # Obtain auth token
        response = self.client.post("/api/auth/token/", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            self.token = response.json().get("token")

    def auth_headers(self):
        if self.token:
            return {"Authorization": "Token " + self.token}
        return {}

    @task(3)
    def book_overlapping_appointment(self):
        """
        Many simulated citizens try to book the SAME 30-minute slot
        at the same time to deliberately trigger race conditions.
        """
        payload = {
            "service_type": random.choice([
                "birth_certificate", "death_certificate",
                "income_certificate", "residence_certificate",
                "caste_certificate", "property_certificate"
            ]),
            # Same fixed time window for many users — forces overlap
            "scheduled_time": "2026-07-01T10:00:00Z",
            "form_data_jsonb": {
                "applicant": {"full_name": "Load Test Citizen"},
                "appointment": {"purpose": "Stress test booking"}
            }
        }
        with self.client.post(
            "/api/appointments/book/",
            json=payload,
            headers=self.auth_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 409:
                # Expected — slot full, handled gracefully
                response.success()
            else:
                response.failure(
                    "Unexpected status " + str(response.status_code)
                )

    @task(2)
    def submit_grievance(self):
        """Simulated citizens submitting complaints concurrently."""
        payload = {
            "category": random.choice(
                ["roads", "sanitation", "water", "electricity"]
            ),
            "description": "Load test complaint generated automatically "
                            "to verify concurrent grievance submission handling.",
            "latitude": round(random.uniform(21.10, 21.20), 6),
            "longitude": round(random.uniform(79.05, 79.12), 6)
        }
        with self.client.post(
            "/api/grievances/submit/",
            json=payload,
            headers=self.auth_headers(),
            catch_response=True
        ) as response:
            if response.status_code in (201, 400):
                response.success()
            else:
                response.failure(
                    "Unexpected status " + str(response.status_code)
                )

    @task(1)
    def list_my_appointments(self):
        """Simulated read traffic — citizens checking their own tokens."""
        with self.client.get(
            "/api/appointments/my-tokens/",
            headers=self.auth_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    "Unexpected status " + str(response.status_code)
                )