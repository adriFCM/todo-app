from django.test import TestCase, Client
from django.urls import reverse
from .models import Task
from .forms import TaskForm


class TaskModelTests(TestCase):
    def test_defaults_and_str(self):
        t = Task.objects.create(title="Test task", description="")
        self.assertFalse(t.completed)
        self.assertEqual(t.priority, Task.Priority.LOW)   # default from model
        self.assertIsNone(t.due_date)                     # optional
        self.assertEqual(str(t), "Test task")


class TaskFormTests(TestCase):
    def test_due_date_optional_is_valid(self):
        form = TaskForm(data={
            "title": "No date",
            "description": "",
            "due_date": "",                 # blank allowed
            "priority": Task.Priority.LOW,
        })
        self.assertTrue(form.is_valid())

    def test_reject_wrong_date_format(self):
        # Wrong format (YYYY-MM-DD) should be invalid because form expects DD/MM/YYYY
        form = TaskForm(data={
            "title": "Bad date format",
            "description": "",
            "due_date": "2025-10-05",
            "priority": Task.Priority.LOW,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)

    def test_reject_impossible_date(self):
        # 31 Feb is invalid even if format looks right
        form = TaskForm(data={
            "title": "Impossible date",
            "description": "",
            "due_date": "31/02/2025",
            "priority": Task.Priority.LOW,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)


class TaskViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.t1 = Task.objects.create(title="Alpha", description="", priority=Task.Priority.LOW)
        self.t2 = Task.objects.create(title="Bravo done", description="", completed=True, priority=Task.Priority.HIGH)

    # ----- list -----
    def test_list_page_loads(self):
        resp = self.client.get(reverse("task_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alpha")
        self.assertContains(resp, "Bravo done")

    def test_list_search_and_filters(self):
        # search
        resp = self.client.get(reverse("task_list"), {"q": "Alpha"})
        self.assertContains(resp, "Alpha")
        self.assertNotContains(resp, "Bravo done")
        # status=open
        resp = self.client.get(reverse("task_list"), {"status": "open"})
        self.assertContains(resp, "Alpha")
        self.assertNotContains(resp, "Bravo done")
        # status=done
        resp = self.client.get(reverse("task_list"), {"status": "done"})
        self.assertNotContains(resp, "Alpha")
        self.assertContains(resp, "Bravo done")
        # priority filter
        resp = self.client.get(reverse("task_list"), {"priority": "HIGH"})
        self.assertNotContains(resp, "Alpha")
        self.assertContains(resp, "Bravo done")

    def test_sort_whitelist_does_not_crash(self):
        # Unknown sort should gracefully fall back (200 OK)
        resp = self.client.get(reverse("task_list"), {"sort": "__bad__"})
        self.assertEqual(resp.status_code, 200)

    # ----- create -----
    def test_create_get_and_post_valid(self):
        url = reverse("task_create")
        self.assertEqual(self.client.get(url).status_code, 200)
        count_before = Task.objects.count()
        resp = self.client.post(url, {
            "title": "Created via POST",
            "description": "ok",
            "due_date": "",                         # optional
            "priority": Task.Priority.MED,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Task.objects.count(), count_before + 1)

    def test_create_post_invalid_date_shows_errors(self):
        url = reverse("task_create")
        count_before = Task.objects.count()
        resp = self.client.post(url, {
            "title": "Bad date",
            "description": "",
            "due_date": "2025-10-05",               # wrong format for the form
            "priority": Task.Priority.LOW,
        })
        self.assertEqual(resp.status_code, 200)     # re-render form with errors
        self.assertEqual(Task.objects.count(), count_before)
        self.assertContains(resp, "Invalid date format")  # from forms.py error_messages

    # ----- update -----
    def test_update_changes_title(self):
        url = reverse("task_update", args=[self.t1.pk])
        resp = self.client.post(url, {
            "title": "Alpha edited",
            "description": "",
            "due_date": "",
            "priority": Task.Priority.LOW,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.t1.refresh_from_db()
        self.assertEqual(self.t1.title, "Alpha edited")
