"""Регресс на IG 447: content-desc поста переехал из media_group во вложенный
row_feed_photo_imageview / carousel_image (см. RESEARCH-2026-09-18-ig447.md).

Запуск: PYTHONPATH=. .venv/bin/python test/test_like_media_container.py
"""

from types import SimpleNamespace

from InstaAddict.core import views

views.ResourceID = views.resources("com.instagram.android")


class FakeView:
    """Минимальная замена DeviceFacade.View."""

    def __init__(self, desc=None, exists=True, children=None):
        self.desc = desc
        self._exists = exists
        self.children = children or {}
        self.child_queries = []

    def exists(self, *_):
        return self._exists

    def get_desc(self):
        return self.desc

    def child(self, **kwargs):
        self.child_queries.append(kwargs)
        pattern = kwargs.get("resourceIdMatches", "")
        for key, view in self.children.items():
            if key in pattern:
                return view
        return FakeView(exists=False)


def _view_with(media):
    obj = views.PostsViewList.__new__(views.PostsViewList)
    obj.device = SimpleNamespace(find=lambda **kw: media)
    return obj


def test_desc_taken_from_inner_photo_view():
    inner = FakeView(desc="Photo by Dusty Pilgrim, 2 likes, 1 comment")
    media = FakeView(desc=None, children={"row_feed_photo_imageview": inner})
    container, desc = _view_with(media)._get_media_container()
    assert container is media, container
    assert desc == "Photo by Dusty Pilgrim, 2 likes, 1 comment", desc


def test_desc_taken_from_inner_carousel_image():
    inner = FakeView(desc="Photo 1 of 4 by Some Account, 2,280 likes")
    media = FakeView(desc=None, children={"carousel_image": inner})
    _, desc = _view_with(media)._get_media_container()
    assert desc == "Photo 1 of 4 by Some Account, 2,280 likes", desc


def test_own_desc_wins_and_child_not_queried():
    media = FakeView(desc="Video by Someone, 5 likes")
    _, desc = _view_with(media)._get_media_container()
    assert desc == "Video by Someone, 5 likes", desc
    assert media.child_queries == [], media.child_queries


def test_missing_container_returns_none():
    media = FakeView(desc=None, exists=False)
    container, desc = _view_with(media)._get_media_container()
    assert container is media, container
    assert desc is None, desc


def test_empty_everywhere_returns_none():
    inner = FakeView(desc="")
    media = FakeView(desc="", children={"row_feed_photo_imageview": inner})
    _, desc = _view_with(media)._get_media_container()
    assert desc is None, desc


def main():
    test_desc_taken_from_inner_photo_view()
    test_desc_taken_from_inner_carousel_image()
    test_own_desc_wins_and_child_not_queried()
    test_missing_container_returns_none()
    test_empty_everywhere_returns_none()
    print("OK")


if __name__ == "__main__":
    main()
