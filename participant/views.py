from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required
def view_participant(request):
    return render(request, 'participant/index.html')
