from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "pages/about.html"


class RulesView(TemplateView):
    template_name = "pages/rules.html"


def registration(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(
        request,
        "registration/registration_form.html",
        {"form": form},
    )


def page_404(request, exception):
    return render(request, "pages/404.html", status=404)


def page_500(request):
    return render(request, "pages/500.html", status=500)


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)
