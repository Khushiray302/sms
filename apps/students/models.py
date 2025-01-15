from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.corecode.models import StudentClass


class Student(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )

    registration_number = models.CharField(max_length=200, unique=True, blank=True)
    
    firstname = models.CharField(max_length=200)
    other_name = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200)
    roll_no = models.IntegerField(blank=True, null=True, default=0)
    attendance = models.IntegerField(blank=True, null=True, default=0)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    # current_class = models.ForeignKey(
    #     StudentClass, on_delete=models.SET_NULL, blank=True, null=True
    # )
    current_class = models.ForeignKey(StudentClass,on_delete=models.SET_NULL,related_name='students',null=True, blank=True
    )
    date_of_admission = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    parent_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )

    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")

    class Meta:
        ordering = ["firstname", "other_name", "surname"]

    def __str__(self):
        return f"{self.firstname} {self.other_name} {self.surname}  ({self.registration_number})"
    
    def save(self, *args, **kwargs):
    # Generate a unique registration number if not provided
        if not self.registration_number:
            last_student = Student.objects.order_by("id").last()
            next_id = 1 if not last_student else int(last_student.registration_number) + 1
            self.registration_number = f"{next_id:03d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})


class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")
