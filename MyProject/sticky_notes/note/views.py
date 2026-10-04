# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from .forms import NoteForm


def note_list(request):
    """
    View to display a list of all notes.
    :param request: HTTP request object.
    :return: Rendered template with a list of notes.
    """
    notes = Note.objects.all()
    # Creating a context dictionary to pass data
    context = {
        "notes": notes,
        "page_title": "List of Notes",
    }
    return render(request, "note/note_list.html", context)


def note_detail(request, pk):
    """
    View to display details of a specific note.
    :param request: HTTP request object.
    :param pk: Primary key of the note.
    :return: Rendered template with details of the specified note.
    """
    note = get_object_or_404(Note, pk=pk)
    return render(request, "note/note_detail.html", {"note": note})


def note_form(request):
    """
    View to create a new note.
    :param request: HTTP request object.
    :return: Rendered template for creating a new note.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm()

    return render(request, "note/note_form.html", {"form": form})


def note_update(request, pk):
    """
    View to update an existing note.
    :param request: HTTP request object.
    :param pk: Primary key of the note to be updated.
    :return: Rendered template for updating the specified note.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm(instance=note)

    return render(request, "note/note_form.html", {"form": form})


def note_confirm_delete(request, pk):
    """
    View to confirm deletion of an existing note.
    :param request: HTTP request object.
    :param pk: Primary key of the note to be deleted.
    :return: Confirmation page on GET; deletes the note and redirects
             to the list on POST.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("note_list")
    return render(request, "note/note_confirm_delete.html", {"note": note})
