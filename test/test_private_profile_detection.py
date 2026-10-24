from types import SimpleNamespace
from unittest.mock import patch

from InstaAddict.core import views
from InstaAddict.core.views import ProfileView

APP_ID = "com.instagram.android"
views.ResourceID = views.resources(APP_ID)
views.configs = SimpleNamespace(args=SimpleNamespace(app_id=APP_ID))


class FakeView:
    def __init__(self, found):
        self._found = found

    def exists(self, *args, **kwargs):
        return self._found


def _device_with(notice_text_found, rid_found):
    calls = []

    def find(**kwargs):
        selector = str(kwargs)
        calls.append(selector)
        if "resourceIdMatches" in kwargs:
            return FakeView(rid_found)
        if "textMatches" in kwargs:
            return FakeView(notice_text_found)
        return FakeView(False)

    return SimpleNamespace(find=find), calls


def test_private_detected_via_resource_id():
    device, _ = _device_with(notice_text_found=False, rid_found=True)
    assert ProfileView(device).isPrivateAccount() is True


def test_private_detected_via_notice_text_when_rid_missing():
    device, _ = _device_with(notice_text_found=True, rid_found=False)
    assert ProfileView(device).isPrivateAccount() is True


def test_public_account_not_flagged_private():
    device, _ = _device_with(notice_text_found=False, rid_found=False)
    assert ProfileView(device).isPrivateAccount() is False
