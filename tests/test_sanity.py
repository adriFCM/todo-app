# tests/test_sanity.py
import pytest
from django.urls import reverse
"""
Sanity / smoke test (app-level)

Purpose:
- Quick end-to-end check that touches real app code:
  * URL reversing works (named route exists)
  * View executes without errors
  * Templates render
  * Test database is available
- Useful as a lightweight guard during CI: it catches common regressions
  (renamed routes, broken imports, template errors) early.

Why @pytest.mark.django_db?
- Plain pytest tests block DB access by default.
- Marking with django_db (or using the 'db' fixture) explicitly enables the test DB.
"""

@pytest.mark.django_db
def test_task_list_url_resolves(client):
    resp = client.get(reverse("task_list"))
    assert resp.status_code == 200
