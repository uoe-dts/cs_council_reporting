from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CommentForm
from issues.models import Issue

@login_required
def add_comment(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.author = request.user
            comment.save()
    return redirect('issue_detail', pk=issue.id)