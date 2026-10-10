import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import HTTPException
from fastapi.testclient import TestClient

import main
from gift_service import GiftService

CHAT = "\n".join([
    "分析対象: Bob",
    "2026/06/16 09:12\tAlice\tAre you free this weekend?",
    "2026/06/16 09:13\tBob\tI want to visit a coffee roaster.",
])


def fake_gift_service():
    service = MagicMock()
    service.generate_recommendations = AsyncMock(return_value={"ok": True})
    return service


class RequestValidationTests(unittest.TestCase):
    def setUp(self):
        main.limiter.reset()
        self.client = TestClient(main.app)

    def test_reddit_id_must_look_like_a_username(self):
        for bad_id in ["ab", "a" * 21, "../etc/passwd", "name?x=1", "a b c"]:
            response = self.client.get("/analyze", params={"reddit_id": bad_id})
            self.assertEqual(response.status_code, 422, bad_id)

    def test_budget_must_be_in_range(self):
        response = self.client.get("/analyze", params={"reddit_id": "valid_user", "min_budget": -1})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/analyze-line", json={"chat_content": CHAT, "max_budget": 10**12})
        self.assertEqual(response.status_code, 422)

    def test_chat_content_length_is_limited(self):
        max_length = main.ChatAnalysisRequest.model_fields["chat_content"].metadata[0].max_length
        response = self.client.post("/analyze-line", json={"chat_content": "x" * (max_length + 1)})
        self.assertEqual(response.status_code, 422)

    def test_oversized_body_is_rejected_before_parsing(self):
        body = main.MAX_REQUEST_BODY_BYTES + 1
        response = self.client.post(
            "/analyze-line", content=b"x" * body, headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 413)

    def test_oversized_chunked_body_without_content_length_is_rejected(self):
        def chunks():
            for _ in range(main.MAX_REQUEST_BODY_BYTES // 100_000 + 2):
                yield b"x" * 100_000

        response = self.client.post(
            "/analyze-line", content=chunks(), headers={"Content-Type": "application/json"}
        )
        self.assertNotIn("content-length", response.request.headers)
        self.assertEqual(response.status_code, 413)

    def test_additional_info_length_is_limited(self):
        response = self.client.post(
            "/analyze-line", json={"chat_content": CHAT, "additional_info": "x" * 1001}
        )
        self.assertEqual(response.status_code, 422)


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        main.limiter.reset()
        self.client = TestClient(main.app)

    def test_analysis_endpoint_is_rate_limited_per_client(self):
        with patch.object(main, "get_gift_service", fake_gift_service):
            statuses = [
                self.client.post("/analyze-line", json={"chat_content": CHAT}).status_code
                for _ in range(6)
            ]
        self.assertEqual(statuses[:5], [200] * 5)
        self.assertEqual(statuses[5], 429)

    def test_different_clients_have_separate_limits(self):
        with patch.object(main, "get_gift_service", fake_gift_service):
            for _ in range(5):
                self.client.post("/analyze-line", json={"chat_content": CHAT},
                                 headers={"X-Forwarded-For": "203.0.113.1"})
            other = self.client.post("/analyze-line", json={"chat_content": CHAT},
                                     headers={"X-Forwarded-For": "203.0.113.2"})
        self.assertEqual(other.status_code, 200)

    def test_spoofed_forwarded_for_prefix_does_not_bypass_limit(self):
        with patch.object(main, "get_gift_service", fake_gift_service):
            statuses = [
                self.client.post(
                    "/analyze-line", json={"chat_content": CHAT},
                    headers={"X-Forwarded-For": f"10.0.0.{i}, 198.51.100.7"},
                ).status_code
                for i in range(6)
            ]
        self.assertEqual(statuses[5], 429)

    def test_health_is_not_rate_limited(self):
        for _ in range(20):
            self.assertEqual(self.client.get("/health").status_code, 200)


class CorsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    def preflight(self, origin):
        return self.client.options(
            "/analyze-line",
            headers={"Origin": origin, "Access-Control-Request-Method": "POST",
                     "Access-Control-Request-Headers": "content-type"},
        )

    def test_unknown_origin_is_not_allowed(self):
        response = self.preflight("https://evil.example")
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_known_origin_is_allowed_without_credentials(self):
        response = self.preflight("http://localhost:3000")
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3000")
        self.assertNotIn("access-control-allow-credentials", response.headers)

    def test_root_does_not_expose_configuration(self):
        self.assertEqual(set(self.client.get("/").json()), {"message"})


class ClientIpTests(unittest.TestCase):
    def request(self, forwarded_for=None, host="127.0.0.1"):
        req = MagicMock()
        req.headers = {"x-forwarded-for": forwarded_for} if forwarded_for else {}
        req.client.host = host
        return req

    def test_uses_socket_address_without_header(self):
        self.assertEqual(main.get_client_ip(self.request()), "127.0.0.1")

    def test_uses_entry_added_by_trusted_proxy(self):
        self.assertEqual(main.get_client_ip(self.request("1.1.1.1, 2.2.2.2")), "2.2.2.2")

    def test_hops_zero_ignores_header(self):
        with patch.dict(os.environ, {"TRUSTED_PROXY_HOPS": "0"}):
            self.assertEqual(main.get_client_ip(self.request("1.1.1.1")), "127.0.0.1")


class GeminiCallTests(unittest.IsolatedAsyncioTestCase):
    def make_service(self, **env):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", **env}), \
                patch("gift_service.genai"):
            return GiftService()

    async def test_gemini_call_times_out(self):
        service = self.make_service(GEMINI_REQUEST_TIMEOUT="0.05")

        async def hang(_prompt):
            await asyncio.sleep(5)

        service.model.generate_content_async = hang
        with self.assertRaises(asyncio.TimeoutError):
            await service._generate("hello")

    async def test_gemini_timeout_is_reported_as_504(self):
        service = self.make_service(GEMINI_REQUEST_TIMEOUT="0.05")

        async def hang(_prompt):
            await asyncio.sleep(5)

        service.model.generate_content_async = hang
        with self.assertRaises(HTTPException) as caught:
            await service.generate_recommendations("posts", "someone", {})
        self.assertEqual(caught.exception.status_code, 504)

    async def test_gemini_call_does_not_block_event_loop(self):
        service = self.make_service()

        async def slow(_prompt):
            await asyncio.sleep(0.2)
            return "done"

        service.model.generate_content_async = slow
        ticks = 0

        async def ticker():
            nonlocal ticks
            while True:
                await asyncio.sleep(0.01)
                ticks += 1

        task = asyncio.create_task(ticker())
        self.assertEqual(await service._generate("hello"), "done")
        task.cancel()
        self.assertGreater(ticks, 5)

    async def test_concurrent_requests_are_serialized_by_rate_limit(self):
        service = self.make_service()
        sleeps = []

        async def fake_sleep(seconds):
            sleeps.append(seconds)

        with patch("gift_service.asyncio.sleep", fake_sleep):
            await asyncio.gather(*(service._check_rate_limits() for _ in range(3)))
        self.assertEqual(service.daily_request_count, 3)
        self.assertEqual(len(sleeps), 2)


if __name__ == "__main__":
    unittest.main()
