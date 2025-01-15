from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.conf import settings
from .models import Logo

from .forms import (
    AcademicSessionForm,
    AcademicTermForm,
    CurrentSessionForm,
    SiteConfigForm,
    StudentClassForm,
    SubjectForm,
    SubjectClassForm
)
from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    SubjectClass
)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"


class SiteConfigView(LoginRequiredMixin, View):
    """Site Config View"""

    form_class = SiteConfigForm
    template_name = "corecode/siteconfig.html"

    def get(self, request, *args, **kwargs):
        formset = self.form_class(queryset=SiteConfig.objects.all())
        context = {"formset": formset}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        formset = self.form_class(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Configurations successfully updated")
        context = {"formset": formset, "title": "Configuration"}
        return render(request, self.template_name, context)


class SessionListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicSession
    template_name = "corecode/session_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicSessionForm()
        return context


class SessionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("sessions")
    success_message = "New session successfully added"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new session"
        return context


class SessionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    success_url = reverse_lazy("sessions")
    success_message = "Session successfully updated."
    template_name = "corecode/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicSession.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a session to current.")
                return redirect("session-list")
        return super().form_valid(form)


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicSession
    success_url = reverse_lazy("sessions")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The session {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete session as it is set to current")
            return redirect("sessions")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SessionDeleteView, self).delete(request, *args, **kwargs)


class TermListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicTerm
    template_name = "corecode/term_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicTermForm()
        return context


class TermCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("terms")
    success_message = "New term successfully added"


class TermUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    success_url = reverse_lazy("terms")
    success_message = "Term successfully updated."
    template_name = "corecode/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicTerm.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a term to current.")
                return redirect("term")
        return super().form_valid(form)


class TermDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicTerm
    success_url = reverse_lazy("terms")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete term as it is set to current")
            return redirect("terms")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(TermDeleteView, self).delete(request, *args, **kwargs)


class ClassListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = StudentClass
    template_name = "corecode/class_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StudentClassForm()
        return context


class ClassCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("classes")
    success_message = "New class successfully added"


class ClassUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentClass
    fields = ["name"]
    success_url = reverse_lazy("classes")
    success_message = "class successfully updated."
    template_name = "corecode/mgt_form.html"


class ClassDeleteView(LoginRequiredMixin, DeleteView):
    model = StudentClass
    success_url = reverse_lazy("classes")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.name)
        messages.success(self.request, self.success_message.format(obj.name))
        return super(ClassDeleteView, self).delete(request, *args, **kwargs)


class SubjectListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Subject
    template_name = "corecode/subject_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SubjectForm()
        return context


class SubjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("subjects")
    success_message = "New subject successfully added"


class SubjectUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    fields = ["name"]
    success_url = reverse_lazy("subjects")
    success_message = "Subject successfully updated."
    template_name = "corecode/mgt_form.html"


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy("subjects")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The subject {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SubjectDeleteView, self).delete(request, *args, **kwargs)


class CurrentSessionAndTermView(LoginRequiredMixin, View):
    """Current SEssion and Term"""

    form_class = CurrentSessionForm
    template_name = "corecode/current_session.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            initial={
                "current_session": AcademicSession.objects.get(current=True),
                "current_term": AcademicTerm.objects.get(current=True),
            }
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_Class(request.POST)
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            AcademicSession.objects.filter(name=session).update(current=True)
            AcademicSession.objects.exclude(name=session).update(current=False)
            AcademicTerm.objects.filter(name=term).update(current=True)

        return render(request, self.template_name, {"form": form})
    

def assign_subjects(request):
    """View for assigning subjects to classes"""
    class_id = request.GET.get('class_id')  # Get class_id from the URL
    initial_data = {}

    if class_id:
        # Fetch the class based on the class_id and set it as the initial data for the form
        student_class = get_object_or_404(StudentClass, id=class_id)
        initial_data['student_class'] = student_class
    if request.method == 'POST':
        form = SubjectClassForm(request.POST)
        if form.is_valid():
            student_class = form.cleaned_data['student_class']
            subjects = form.cleaned_data['subjects']
            
            # Delete existing relations for the selected class (optional, based on requirements)
            SubjectClass.objects.filter(student_class=student_class).delete()

            # Create new relations between the class and subjects
            for subject in subjects:
                SubjectClass.objects.create(student_class=student_class, subject=subject)

            messages.success(request, f'Subjects have been successfully assigned to {student_class.name}')
            return redirect('classes')

    else:
        form = SubjectClassForm(initial=initial_data)

    return render(request, 'corecode/assign_subjects.html', {'form': form})


# def upload_logo(request):
#     file_url = None
#     if request.method == 'POST' and request.FILES.get('logo'):
#         logo = request.FILES['logo']
#         if logo.content_type.startswith('image/'):  # Validate it's an image
#             new_logo = Logo.objects.create(image=logo, uploaded_by=request.user.username if request.user.is_authenticated else "Anonymous")
#             file_url = new_logo.image.url  # Get the image URL from the model instance
#     return render(request, 'corecode/upload_logo.html', {'file_url': file_url})

from django.shortcuts import render
from .models import Logo
import os

def upload_logo(request):
    file_url = None
    logo_instance = None

    # Check if there is an existing logo for the user or site
    if request.user.is_authenticated:
        logo_instance = Logo.objects.filter(uploaded_by=request.user.username).first()

    if request.method == 'POST':
        if request.FILES.get('logo'):
            logo = request.FILES['logo']
            if logo.content_type.startswith('image/'):  # Validate it's an image
                # If there's an existing logo, delete it before updating
                if logo_instance:
                    # Delete the old logo file from storage
                    if logo_instance.image:
                        logo_instance.image.delete(save=False)  # Delete the old image file
                    logo_instance.delete()  # Delete the old logo instance
                
                # Create a new logo instance
                logo_instance = Logo.objects.create(image=logo, uploaded_by=request.user.username if request.user.is_authenticated else "Anonymous")
                file_url = logo_instance.image.url  # Get the image URL from the model instance

    else:
        if logo_instance:
            file_url = logo_instance.image.url  # Get the existing image URL if available

    return render(request, 'corecode/upload_logo.html', {'file_url': file_url, 'logo_instance': logo_instance})
