from django.db import models

from apps.corecode.models import (
    AcademicSession,
    AcademicTerm,
    StudentClass,
    Subject,
)
from apps.students.models import Student

from .utils import score_grade


# Create your models here.
# class Result(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
#     term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
#     current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     test_score = models.IntegerField(default=0)
#     exam_score = models.IntegerField(default=0)

#     class Meta:
#         ordering = ["subject"]

#     def __str__(self):
#         return f"{self.student} {self.session} {self.term} {self.subject}"

#     def total_score(self):
#         return self.test_score + self.exam_score

#     def grade(self):
#         return score_grade(self.total_score())
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    full_pract_score = models.IntegerField(default=0)  # Full mark for practical
    full_theory_score = models.IntegerField(default=0)  # Full mark for theory
    obt_pract_score = models.IntegerField(default=0)  # Obtained mark for practical
    obt_theory_score = models.IntegerField(default=0)  # Obtained mark for theory
    
    class Meta:
        ordering = ["subject"]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.current_class}"