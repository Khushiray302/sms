from django import forms
from django.forms import modelformset_factory

from apps.corecode.models import AcademicSession, AcademicTerm, Subject

from .models import Result


class CreateResults(forms.Form):
    session = forms.ModelChoiceField(queryset=AcademicSession.objects.all())
    term = forms.ModelChoiceField(queryset=AcademicTerm.objects.all())
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple
    )


# EditResults = modelformset_factory(
#     Result, fields=("test_score", "exam_score"), extra=0, can_delete=True
# )

EditResults = modelformset_factory(
    Result,
    fields=(
        "full_pract_score", 
        "full_theory_score", 
        "obt_pract_score", 
        "obt_theory_score"
    ),
    extra=0,
    can_delete=True
)
