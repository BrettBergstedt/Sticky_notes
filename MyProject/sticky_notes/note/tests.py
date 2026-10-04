from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from . import views
from .forms import NoteForm
from .models import Author, Note


# ---------------------------------------------------------------- models
class NoteModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="test-author")
        self.note = Note.objects.create(
            title="Test Note",
            content="This is a test note.",
            author=self.author,
        )

    def test_note_has_title(self):
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, "Test Note")

    def test_note_has_content(self):
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.content, "This is a test note.")

    def test_str_returns_the_title(self):
        self.assertEqual(str(self.note), "Test Note")

    def test_created_at_is_set_automatically(self):
        self.assertIsNotNone(self.note.created_at)

    def test_updated_at_changes_when_note_is_saved(self):
        # Pretend the note was last updated yesterday, then save it again
        yesterday = timezone.now() - timedelta(days=1)
        Note.objects.filter(pk=self.note.pk).update(updated_at=yesterday)
        note = Note.objects.get(pk=self.note.pk)
        note.title = "Changed"
        note.save()
        self.assertGreater(note.updated_at, yesterday)

    def test_author_is_optional(self):
        note = Note.objects.create(title="No author", content="Anonymous")
        self.assertIsNone(note.author)

    def test_deleting_the_author_deletes_their_notes(self):
        self.author.delete()
        self.assertEqual(Note.objects.count(), 0)


class AuthorModelTest(TestCase):
    def test_str_returns_the_name(self):
        author = Author.objects.create(name="Test Author")
        self.assertEqual(str(author), "Test Author")


# ----------------------------------------------------------------- forms
class NoteFormTest(TestCase):
    def test_form_has_the_expected_fields(self):
        self.assertEqual(
            list(NoteForm().fields), ["title", "content", "author"]
        )

    def test_form_is_valid_with_title_and_content(self):
        form = NoteForm(data={"title": "Milk", "content": "2 litres"})
        self.assertTrue(form.is_valid())

    def test_form_requires_a_title(self):
        form = NoteForm(data={"title": "", "content": "2 litres"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_requires_content(self):
        form = NoteForm(data={"title": "Milk", "content": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_form_rejects_a_title_longer_than_255_characters(self):
        form = NoteForm(data={"title": "x" * 256, "content": "Too long"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_accepts_a_title_of_exactly_255_characters(self):
        form = NoteForm(data={"title": "x" * 255, "content": "Just right"})
        self.assertTrue(form.is_valid())

    def test_form_save_creates_a_note(self):
        form = NoteForm(data={"title": "Milk", "content": "2 litres"})
        form.save()
        self.assertEqual(Note.objects.get().title, "Milk")


# ------------------------------------------------------------- list view
class NoteListViewTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="test-author")
        self.note = Note.objects.create(
            title="Test Note",
            content="This is a test note.",
            author=self.author,
        )

    def test_note_list_view(self):
        response = self.client.get(reverse("note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Note")

    def test_list_uses_the_right_templates(self):
        response = self.client.get(reverse("note_list"))
        self.assertTemplateUsed(response, "note/note_list.html")
        self.assertTemplateUsed(response, "base.html")

    def test_list_shows_every_note(self):
        Note.objects.create(title="Second Note", content="More text")
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "Test Note")
        self.assertContains(response, "Second Note")

    def test_list_shows_a_message_when_there_are_no_notes(self):
        Note.objects.all().delete()
        response = self.client.get(reverse("note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No notes yet.")

    def test_list_links_to_view_edit_and_delete(self):
        response = self.client.get(reverse("note_list"))
        for name in ["note_detail", "note_update", "note_delete"]:
            url = reverse(name, args=[self.note.id])
            self.assertContains(response, 'href="%s"' % url)

    def test_list_shortens_long_content(self):
        words = " ".join("word%d" % n for n in range(1, 41))
        Note.objects.create(title="Long", content=words)
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "word30")
        self.assertNotContains(response, "word31")

    def test_page_links_to_the_stylesheet(self):
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "/static/note/styles.css")
        self.assertIsNotNone(finders.find("note/styles.css"))


# ----------------------------------------------------------- detail view
class NoteDetailViewTest(TestCase):
    def setUp(self):
        self.note = Note.objects.create(
            title="Test Note", content="This is a test note."
        )

    def test_note_detail_view(self):
        response = self.client.get(reverse("note_detail", args=[self.note.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Note")
        self.assertContains(response, "This is a test note.")

    def test_detail_uses_the_right_template(self):
        response = self.client.get(reverse("note_detail", args=[self.note.id]))
        self.assertTemplateUsed(response, "note/note_detail.html")

    def test_detail_shows_created_and_updated_times(self):
        response = self.client.get(reverse("note_detail", args=[self.note.id]))
        self.assertContains(response, "Created:")
        self.assertContains(response, "Updated:")

    def test_detail_of_a_missing_note_gives_404(self):
        response = self.client.get(reverse("note_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


# ----------------------------------------------------------- create view
class NoteCreateViewTest(TestCase):
    def test_create_page_shows_an_empty_form(self):
        response = self.client.get(reverse("note_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "note/note_form.html")
        self.assertContains(response, "New note")

    def test_valid_post_creates_a_note_and_redirects_to_the_list(self):
        response = self.client.post(
            reverse("note_create"),
            {"title": "Buy milk", "content": "2 litres"},
        )
        self.assertRedirects(response, reverse("note_list"))
        note = Note.objects.get()
        self.assertEqual(note.title, "Buy milk")
        self.assertEqual(note.content, "2 litres")

    def test_new_note_can_be_given_an_author(self):
        author = User.objects.create_user(username="test-author")
        self.client.post(
            reverse("note_create"),
            {"title": "Buy milk", "content": "2 litres", "author": author.id},
        )
        self.assertEqual(Note.objects.get().author, author)

    def test_post_without_a_title_saves_nothing(self):
        response = self.client.post(
            reverse("note_create"), {"title": "", "content": "2 litres"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 0)

    def test_invalid_post_shows_the_form_with_an_error(self):
        response = self.client.post(
            reverse("note_create"), {"title": "", "content": "2 litres"}
        )
        self.assertFormError(
            response.context["form"], "title", "This field is required."
        )


# ----------------------------------------------------------- update view
class NoteUpdateViewTest(TestCase):
    def setUp(self):
        self.note = Note.objects.create(
            title="Original title", content="Original content"
        )
        self.url = reverse("note_update", args=[self.note.id])

    def test_edit_page_is_filled_with_the_current_values(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "note/note_form.html")
        self.assertContains(response, "Edit note")
        self.assertContains(response, 'value="Original title"')
        self.assertContains(response, "Original content")

    def test_valid_post_updates_the_note_and_redirects_to_the_list(self):
        response = self.client.post(
            self.url, {"title": "New title", "content": "New content"}
        )
        self.assertRedirects(response, reverse("note_list"))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "New title")
        self.assertEqual(self.note.content, "New content")

    def test_editing_does_not_create_a_second_note(self):
        self.client.post(self.url, {"title": "New", "content": "New"})
        self.assertEqual(Note.objects.count(), 1)

    def test_invalid_post_leaves_the_note_unchanged(self):
        response = self.client.post(
            self.url, {"title": "", "content": "New content"}
        )
        self.assertEqual(response.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Original title")
        self.assertEqual(self.note.content, "Original content")

    def test_editing_a_missing_note_gives_404(self):
        url = reverse("note_update", args=[9999])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, {}).status_code, 404)


# ----------------------------------------------------------- delete view
class NoteDeleteViewTest(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title="Delete me", content="Bye bye")
        self.url = reverse("note_delete", args=[self.note.id])

    def test_confirmation_page_asks_before_deleting(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "note/note_confirm_delete.html")
        self.assertContains(response, "Delete me")

    def test_just_opening_the_page_does_not_delete_the_note(self):
        self.client.get(self.url)
        self.assertEqual(Note.objects.count(), 1)

    def test_post_deletes_the_note_and_redirects_to_the_list(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("note_list"))
        self.assertEqual(Note.objects.count(), 0)

    def test_only_the_chosen_note_is_deleted(self):
        keep = Note.objects.create(title="Keep me", content="Stay")
        self.client.post(self.url)
        self.assertEqual(Note.objects.get(), keep)

    def test_deleting_a_missing_note_gives_404(self):
        url = reverse("note_delete", args=[9999])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)


# ------------------------------------------------------------------ urls
class NoteUrlTest(TestCase):
    def test_url_names_give_the_expected_paths(self):
        self.assertEqual(reverse("note_list"), "/")
        self.assertEqual(reverse("note_create"), "/note/new/")
        self.assertEqual(reverse("note_detail", args=[1]), "/note/1/")
        self.assertEqual(reverse("note_update", args=[1]), "/note/1/edit/")
        self.assertEqual(reverse("note_delete", args=[1]), "/note/1/delete/")

    def test_each_url_is_handled_by_the_right_view(self):
        self.assertEqual(resolve("/").func, views.note_list)
        self.assertEqual(resolve("/note/new/").func, views.note_form)
        self.assertEqual(resolve("/note/1/").func, views.note_detail)
        self.assertEqual(resolve("/note/1/edit/").func, views.note_update)
        self.assertEqual(
            resolve("/note/1/delete/").func, views.note_confirm_delete
        )


# ----------------------------------------------------------------- admin
class NoteAdminTest(TestCase):
    def test_note_and_author_are_registered_in_the_admin(self):
        self.assertTrue(admin.site.is_registered(Note))
        self.assertTrue(admin.site.is_registered(Author))

    def test_visitor_who_is_not_logged_in_is_sent_to_the_login_page(self):
        response = self.client.get(reverse("admin:note_note_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_superuser_can_open_the_notes_page(self):
        User.objects.create_superuser("boss", "boss@example.com", "pw12345!")
        self.client.login(username="boss", password="pw12345!")
        response = self.client.get(reverse("admin:note_note_changelist"))
        self.assertEqual(response.status_code, 200)
