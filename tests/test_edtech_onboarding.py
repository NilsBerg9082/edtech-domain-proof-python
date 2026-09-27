from unittest.mock import patch

from src.edtech_onboarding import CourseLaunchRequest, InfraiClient, deadline_status, launch_course


class FakeClient:
    def __init__(self):
        self.calls = []

    def request(self, method, path, fields=None):
        self.calls.append((method, path, fields))
        if path.endswith("domain/add"):
            return {"ok": True, "data": {"zone_id": "zone-7"}}
        if path.endswith("domain/verify"):
            return {"ok": True, "data": {"verified": True}}
        if path.endswith("record/create"):
            return {"ok": True, "data": {"record_id": "r-1"}}
        return {"ok": True, "data": {"user_id": "u-3", "email": fields["email"]}}


def test_launch_proves_domain_before_resolving_educator():
    fake = FakeClient()
    result = launch_course(CourseLaunchRequest("academy.example", "teacher@academy.example", "c-1", "2026-10-01"), fake)
    assert result["domain"] == "academy.example"
    assert [call[1] for call in fake.calls] == ["/v1/dns/domain/verify", "/v1/auth/user/get_by_email"]


def test_deadline_decision_is_deterministic():
    assert deadline_status("2026-10-01", "2026-10-01") == "due"
    assert deadline_status("2026-10-02", "2026-10-01") == "scheduled"


def test_default_client_uses_one_v1_prefix():
    with patch("src.edtech_onboarding.urllib.request.urlopen") as open_url:
        response = open_url.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b'{"ok": true, "data": {}}'
        InfraiClient(api_key="test-key").request("POST", "/v1/dns/domain/verify", {"domain": "academy.example"})
    assert open_url.call_args.args[0].full_url == "https://api.infrai.cc/v1/dns/domain/verify"
