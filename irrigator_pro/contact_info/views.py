from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView

from contact_info.forms import Contact_InfoForm
from contact_info.models import Contact_Info

@login_required
def edit_contact_info(request):
    cinfo, created = Contact_Info.objects.get_or_create(user=request.user)
    form = Contact_InfoForm(request.POST or None, instance=cinfo)
    if form.is_valid():
        form.save()
        return redirect('/')
    else:
        return render(request, "form.html", {'form': form})

class Contact_InfoDetailView(DetailView):
    template_name = "detail.html"

    def get_object(self):
        obj = Contact_Info.objects.get(user = self.request.user)
        return obj
