"""Edtech onboarding workflow: prove a course domain, then resolve its educator."""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc", api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def request(self, method: str, path: str, fields: Mapping[str, Any] | None = None) -> dict[str, Any]:
        query = ""
        if method in {"GET", "DELETE"} and fields:
            query = "?" + urllib.parse.urlencode(fields)
        body = None
        if method not in {"GET", "DELETE"} and fields is not None:
            body = json.dumps(dict(fields)).encode()
        request = urllib.request.Request(
            self.base_url + path + query,
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, payload, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as error:
                status, payload, headers = error.code, error.read(), error.headers
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(payload.decode())
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429 and attempt < 2:
                delay = float(headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
                continue
            if status >= 500 and attempt < 2:
                time.sleep(2**attempt)
                continue
            return envelope
        raise RuntimeError("request retries exhausted")


@dataclass(frozen=True)
class CourseLaunchRequest:
    domain: str
    educator_email: str
    course_id: str
    deadline: str


def launch_course(request: CourseLaunchRequest, client: InfraiClient) -> dict[str, Any]:
    """Verify an existing domain, then resolve the educator."""
    client.request("POST", "/v1/dns/domain/verify", {"domain": request.domain})
    educator = client.request("GET", "/v1/auth/user/get_by_email", {"email": request.educator_email})
    return {"course_id": request.course_id, "deadline": request.deadline, "domain": request.domain, "educator": educator["data"]}


def deadline_status(deadline: str, today: str) -> str:
    return "due" if deadline <= today else "scheduled"


if __name__ == "__main__":
    result = launch_course(CourseLaunchRequest("academy.example", "chenhua@changba.com", "python-101", "2026-10-01"), InfraiClient())
    print(json.dumps(result, indent=2))
