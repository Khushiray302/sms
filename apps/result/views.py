from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, View

from apps.students.models import Student

from .forms import CreateResults, EditResults
from .models import Result
from apps.corecode.models import Subject, StudentClass, Logo 

from apps.students.models import Student
from django.db.models import Q
from django.http import JsonResponse
from math import ceil
@login_required
# def create_result(request):
#     students = Student.objects.all()
#     if request.method == "POST":

#         # after visiting the second page
#         if "finish" in request.POST:
#             form = CreateResults(request.POST)
#             if form.is_valid():
#                 subjects = form.cleaned_data["subjects"]
#                 session = form.cleaned_data["session"]
#                 term = form.cleaned_data["term"]
#                 students = request.POST["students"]
#                 results = []
#                 for student in students.split(","):
#                     stu = Student.objects.get(pk=student)
#                     if stu.current_class:
#                         for subject in subjects:
#                             check = Result.objects.filter(
#                                 session=session,
#                                 term=term,
#                                 current_class=stu.current_class,
#                                 subject=subject,
#                                 student=stu,
#                             ).first()
#                             if not check:
#                                 results.append(
#                                     Result(
#                                         session=session,
#                                         term=term,
#                                         current_class=stu.current_class,
#                                         subject=subject,
#                                         student=stu,
#                                     )
#                                 )

#                 Result.objects.bulk_create(results)
#                 return redirect("edit-results")

#         # after choosing students
#         id_list = request.POST.getlist("students")
#         if id_list:
#             form = CreateResults(
#                 initial={
#                     "session": request.current_session,
#                     "term": request.current_term,
#                 }
#             )
#             studentlist = ",".join(id_list)
#             return render(
#                 request,
#                 "result/create_result_page2.html",
#                 {"students": studentlist, "form": form, "count": len(id_list)},
#             )
#         else:
#             messages.warning(request, "You didnt select any student.")
#     return render(request, "result/create_result.html", {"students": students})

# def create_result(request):
#     if request.method == 'POST':
#         # Retrieve selected student IDs as a list of strings
#         selected_students = request.POST.getlist('students')
        
#         if not selected_students:
#             # Handle case where no students are selected
#             return render(request, 'result/create_result.html', {
#                 'students': Student.objects.all(),
#                 'error': 'No students were selected.',
#             })

#         # Convert student IDs to integers
#         selected_students = [int(student_id) for student_id in selected_students]

#         # Retrieve current classes for the selected students
#         current_classes = Student.objects.filter(id__in=selected_students).values_list('current_class', flat=True).distinct()

#         if len(current_classes) > 1:
#             # Handle case where students belong to different classes
#             return render(request, 'result/create_result.html', {
#                 'students': Student.objects.all(),
#                 'error': 'Selected students must belong to the same class.',
#             })

#         if not current_classes:
#             # Handle case where no class is found
#             return render(request, 'result/create_result.html', {
#                 'students': Student.objects.all(),
#                 'error': 'No class found for the selected students.',
#             })

#         # Retrieve the current class as an integer
#         current_class = current_classes[0]

#         # Retrieve subjects for the current class
#         subjects = Subject.objects.filter(subjectclass__student_class_id=current_class)

#         # Pass data to the second page
#         return render(
#             request,
#             'result/create_result_page2.html',
#             {
#                 'students': selected_students,
#                 'current_class': StudentClass.objects.get(id=current_class),
#                 'form': CreateResults(),
#                 'subjects': subjects,
#             },
#         )

#     # Fetch students for the first page
#     students = Student.objects.all()
#     return render(request, 'result/create_result.html', {'students': students})


def create_result(request):
    students = Student.objects.all()
    # Get the selected class name from the GET parameter, or None if not provided
    selected_class_id = request.GET.get("class", None)
    
    # Filter students based on the selected class name
    if selected_class_id:
        students = Student.objects.filter(current_class_id=selected_class_id)
    else:
        students = Student.objects.all()

    # Get all available classes for the dropdown
    classes = StudentClass.objects.all()


    if request.method == "POST":
        # After visiting the second page
        if "finish" in request.POST:
            form = CreateResults(request.POST)
            if form.is_valid():
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                student_ids = request.POST.get("students", "")  # Get students as a comma-separated string

                # Convert student IDs to a list
                student_ids = [int(student_id) for student_id in student_ids.split(",") if student_id.strip()]

                results = []
                for student_id in student_ids:
                    try:
                        stu = Student.objects.get(pk=student_id)
                        if stu.current_class:
                            for subject in subjects:
                                check = Result.objects.filter(
                                    session=session,
                                    term=term,
                                    current_class=stu.current_class,
                                    subject=subject,
                                    student=stu,
                                ).first()
                                if not check:
                                    results.append(
                                        Result(
                                            session=session,
                                            term=term,
                                            current_class=stu.current_class,
                                            subject=subject,
                                            student=stu,
                                        )
                                    )
                    except Student.DoesNotExist:
                        continue

                # Bulk create results
                if results:
                    Result.objects.bulk_create(results)
                return redirect("edit-results")

        # After choosing students
        id_list = request.POST.getlist("students")  # Get selected students as a list
        if id_list:
            # Fetch the `current_class` of the selected students
            selected_students = Student.objects.filter(id__in=id_list)
            print("selected student...",selected_students)
            # Get the distinct current classes (and also convert to a set to ensure uniqueness)
            current_classes = set(selected_students.values_list("current_class", flat=True))
            
            print("current classes......", current_classes)  # For debugging, this should show a set with unique class ids
            
            if len(current_classes) > 1:
                # Handle case where students belong to different classes
                messages.error(request, "Selected students must belong to the same class.")
                return render(request, "result/create_result.html", {"students": students})

            if not current_classes:
                # Handle case where no class is found for students
                messages.error(request, "No class found for the selected students.")
                return render(request, "result/create_result.html", {"students": students})

            # Fetch subjects for the `current_class`
            current_class_id = current_classes.pop()  # Extract the class ID from the set
            print("current_class_id......",current_class_id)   
            subjects = Subject.objects.filter(subjectclass__student_class_id=current_class_id)
            
            # Store `current_class_id` in the session
            request.session["current_class_id"] = current_class_id

            # Pass data to the second page
            studentlist = ",".join(id_list)
            form = CreateResults(
                initial={
                    "session": request.current_session,
                    "term": request.current_term,
                    "subjects":subjects,
                }
                
            )
            return render(
                request,
                "result/create_result_page2.html",
                {
                    "students": studentlist,
                    "current_class": StudentClass.objects.get(id=current_class_id),
                    "form": form,
                    "subjects": subjects,
                    "count": len(id_list),
                },
            )
        else:
            # Handle case where no students are selected
            messages.warning(request, "You didn't select any students.")
    
    return render(request, "result/create_result.html", {"students": students,"classes": classes,"selected_class_id": selected_class_id})

# @login_required
# def edit_results(request):
#      # Retrieve `current_class_id` from the session
#     current_class_id = request.session.get("current_class_id")

#     # if not current_class_id:
#     #     messages.error(request, "No class selected for editing results.")
#     #     return redirect("create-result")

#     if request.method == "POST":
#         form = EditResults(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Results successfully updated")
#             return redirect("edit-results")
#     else:
#         results = Result.objects.filter(
#             session=request.current_session, term=request.current_term,current_class_id=current_class_id
#         )
#         form = EditResults(queryset=results)
#     return render(request, "result/edit_results.html", {"formset": form})


@login_required
def edit_results(request):
    # Retrieve `current_class_id` from the session
    current_class_id = request.session.get("current_class_id")

    # Remove the `current_class_id` from the session
    if current_class_id:
        del request.session["current_class_id"]
        request.session.modified = True 
    # Base filter parameters
    filter_params = {
        "session": request.current_session,
        "term": request.current_term,
    }

    # Add class filter only if `current_class_id` exists
    if current_class_id:
        filter_params["current_class_id"] = current_class_id
    # else:
    #     messages.warning(request, "No class selected. Displaying results for all classes.")

    # Fetch filtered results based on filter_params
    results = Result.objects.filter(**filter_params).order_by("current_class__name")

    if request.method == "POST":
        formset = EditResults(request.POST, queryset=results)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Results successfully updated.")
            return redirect("view-results")
    else:
        formset = EditResults(queryset=results)

    return render(request, "result/edit_results.html", {"formset": formset})


# class ResultListView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         results = Result.objects.filter(
#             session=request.current_session, term=request.current_term
#         )
#         bulk = {}

#         for result in results:
#             test_total = 0
#             exam_total = 0
#             subjects = []
#             for subject in results:
#                 if subject.student == result.student:
#                     subjects.append(subject)
#                     test_total += subject.test_score
#                     exam_total += subject.exam_score

#             bulk[result.student.id] = {
#                 "student": result.student,
#                 "subjects": subjects,
#                 "test_total": test_total,
#                 "exam_total": exam_total,
#                 "total_total": test_total + exam_total,
#             }

#         context = {"results": bulk}
#         return render(request, "result/all_results.html", context)





from django.shortcuts import render
from django.views import View
from .models import Result, StudentClass

def calculate_grade(obtained, full):
    """Utility function to calculate grade dynamically."""
    if full > 0:
        return round((obtained * 4) / full, 2)  # Formula: (Obtained * 4) / Full
    return 0  # Avoid division by zero


# class ResultListView(View):
#     def get(self, request, *args, **kwargs):
#         # Filter results based on selected class
#         class_id = request.GET.get("class_id")  # Get class_id from query parameter
#         results = Result.objects.select_related('student', 'subject', 'current_class')

#         if class_id:
#             results = results.filter(current_class_id=class_id)

#         # Fetch all available classes for the dropdown
#         all_classes = StudentClass.objects.all()

#         # Dictionary to store results grouped by students
#         student_results = {}

#         for result in results:
#             student_id = result.student.id

#             # Initialize the student's data if not already initialized
#             if student_id not in student_results:
#                 student_results[student_id] = {
#                     "student": result.student,
#                     "subjects": [],
#                     "total_obt_pract_score": 0,
#                     "total_obt_theory_score": 0,
#                     "total_full_pract_score": 0,
#                     "total_full_theory_score": 0,
#                 }

#             # Calculate grades dynamically
#             pract_grade = calculate_grade(result.obt_pract_score, result.full_pract_score)
#             theory_grade = calculate_grade(result.obt_theory_score, result.full_theory_score)
#             total_obtained_score = result.obt_pract_score + result.obt_theory_score
#             total_full_score = result.full_pract_score + result.full_theory_score
#             total_grade = calculate_grade(total_obtained_score, total_full_score)

#             # Append subject-specific grades
#             student_results[student_id]["subjects"].append({
#                 "subject": result.subject.name,
#                 "obt_pract_score": result.obt_pract_score,
#                 "obt_theory_score": result.obt_theory_score,
#                 "full_pract_score": result.full_pract_score,
#                 "full_theory_score": result.full_theory_score,
#                 "pract_grade": pract_grade,
#                 "theory_grade": theory_grade,
#                 "total_grade": total_grade,
#             })

#             # Accumulate total scores
#             student_results[student_id]["total_obt_pract_score"] += result.obt_pract_score
#             student_results[student_id]["total_obt_theory_score"] += result.obt_theory_score
#             student_results[student_id]["total_full_pract_score"] += result.full_pract_score
#             student_results[student_id]["total_full_theory_score"] += result.full_theory_score

#         # Calculate final grade for each student
#         for student_id, data in student_results.items():
#             total_obtained = data["total_obt_pract_score"] + data["total_obt_theory_score"]
#             total_full = data["total_full_pract_score"] + data["total_full_theory_score"]
#             data["final_grade"] = calculate_grade(total_obtained, total_full)

#         # Pass results and available classes to the template
#         context = {
#             "results": student_results,
#             "all_classes": all_classes,
#             "selected_class_id": int(class_id) if class_id else None,
#         }
#         return render(request, "result/all_results.html", context)

class ResultListView(View):
    def get(self, request, *args, **kwargs):
        # Get search query parameter if exists
        search_query = request.GET.get("search", "")
        
        # Filter results based on selected class and student name
        class_id = request.GET.get("class_id")  # Get class_id from query parameter
        results = Result.objects.select_related('student', 'subject', 'current_class')

        
        
        if class_id:  
            try:
                results = results.filter(current_class_id=class_id)  # Ensure class_id is an integer
            except ValueError:
                results = results.none()  # Return no results for invalid class_id
        if search_query:
            results = results.filter(
                Q(student__surname__icontains=search_query) |
                Q(student__firstname__icontains=search_query) |
                Q(student__other_name__icontains=search_query)
            )  # Case-insensitive search

        # Fetch all available classes for the dropdown
        all_classes = StudentClass.objects.all()

        # Dictionary to store results grouped by students
        student_results = {}

        for result in results:
            student_id = result.student.id

            # Initialize the student's data if not already initialized
            if student_id not in student_results:
                student_results[student_id] = {
                    "student": result.student,
                    "subjects": [],
                    "total_obt_pract_score": 0,
                    "total_obt_theory_score": 0,
                    "total_full_pract_score": 0,
                    "total_full_theory_score": 0,
                    "is_absent": False,
                }
            
            
            # Calculate grades dynamically
            pract_grade = calculate_grade(result.obt_pract_score, result.full_pract_score)
            theory_grade = calculate_grade(result.obt_theory_score, result.full_theory_score)
            
            if theory_grade == 0.00:
                student_results[student_id]["is_absent"] = True
                
            total_obtained_score = result.obt_pract_score + result.obt_theory_score
            total_full_score = result.full_pract_score + result.full_theory_score
            total_grade = calculate_grade(total_obtained_score, total_full_score)

            
            # Append subject-specific grades
            student_results[student_id]["subjects"].append({
                "subject": result.subject.name,
                "obt_pract_score": result.obt_pract_score,
                "obt_theory_score": result.obt_theory_score,
                "full_pract_score": result.full_pract_score,
                "full_theory_score": result.full_theory_score,
                "pract_grade": pract_grade,
                "theory_grade": theory_grade,
                "total_grade": total_grade,
            })

            # Accumulate total scores
            student_results[student_id]["total_obt_pract_score"] += result.obt_pract_score
            student_results[student_id]["total_obt_theory_score"] += result.obt_theory_score
            student_results[student_id]["total_full_pract_score"] += result.full_pract_score
            student_results[student_id]["total_full_theory_score"] += result.full_theory_score

        # Calculate final grade for each student
        for student_id, data in student_results.items():
            if data["is_absent"]:
                
                data["final_grade"] = "0.00"
                
            else:
                total_obtained = data["total_obt_pract_score"] + data["total_obt_theory_score"]
                total_full = data["total_full_pract_score"] + data["total_full_theory_score"]
                data["final_grade"] = calculate_grade(total_obtained, total_full)

        # Pass results and available classes to the template
        context = {
            "results": student_results,
            "all_classes": all_classes,
            "selected_class_id": int(class_id) if class_id else "",
            "search": search_query,  # Pass search query to template
        }
        return render(request, "result/all_results.html", context)


class PrintResultView(View):
    def get(self, request, *args, **kwargs):
        # Get query parameters
        class_id = request.GET.get("class_id")
        search_query = request.GET.get("search")
        
        # Fetch results filtered by class and search query
        results = Result.objects.select_related('student', 'subject', 'current_class')
        if class_id and class_id.isdigit():  # Check if class_id is a valid number
            results = results.filter(current_class_id=class_id)
        else:
            results = results.all()
        if search_query:
            results = results.filter(
                Q(student__surname__icontains=search_query) |
                Q(student__firstname__icontains=search_query) |
                Q(student__other_name__icontains=search_query)
            )
        
        # Dictionary to store student results
        student_results = {}
        for result in results:
            student_id = result.student.id
            if student_id not in student_results:
                student_results[student_id] = {
                    "student": result.student,
                    "subjects": [],
                    "total_obt_pract_score": 0,
                    "total_obt_theory_score": 0,
                    "total_full_pract_score": 0,
                    "total_full_theory_score": 0,
                    "is_absent": False,  # Track if the student is absent
                }

            # Append subject details with grades
            obtained_practical = result.obt_pract_score or 0
            obtained_theory = result.obt_theory_score or 0
            full_practical = result.full_pract_score or 0
            full_theory = result.full_theory_score or 0

            if obtained_theory == 0:
                student_results[student_id]["is_absent"] = True
            
            total_obtained = obtained_practical + obtained_theory
            total_full = full_practical + full_theory

            subject_data = {
                "subject": result.subject.name,
                "obt_pract_score": obtained_practical,
                "obt_theory_score": obtained_theory,
                "full_pract_score": full_practical,
                "full_theory_score": full_theory,
                "pract_grade": self.convert_to_grade(obtained_practical, full_practical),
                "theory_grade": self.convert_to_grade(obtained_theory, full_theory),
                "total_grade": self.convert_to_grade(total_obtained, total_full),
                "total_gpa" : self.calculate_gpa(total_obtained, total_full),
                
            }
            student_results[student_id]["subjects"].append(subject_data)

            # Accumulate totals
            student_results[student_id]["total_obt_pract_score"] += obtained_practical
            student_results[student_id]["total_obt_theory_score"] += obtained_theory
            student_results[student_id]["total_full_pract_score"] += full_practical
            student_results[student_id]["total_full_theory_score"] += full_theory

        for student_id, data in student_results.items():
            total_obtained = data["total_obt_pract_score"] + data["total_obt_theory_score"]
            total_full = data["total_full_pract_score"] + data["total_full_theory_score"]
            
            if data["is_absent"]:
                data["remark"] = "ABSENT"
                data["final_grade"] = "0.00"
                data["f_grade"] = "NG"
            else:
                data["final_grade"] = calculate_grade(total_obtained, total_full)
                data["f_grade"] = self.convert_to_grade(total_obtained, total_full)
                data["remark"]= self.get_remark(total_obtained, total_full)
        logo_instance = Logo.objects.filter(uploaded_by=request.user.username).first()
    
    # Pass the logo instance or its image URL to the template
        logo_url = logo_instance.image.url if logo_instance else None
        context = {
            "results": student_results,
            'logo_url': logo_url,
        }

        return render(request, "result/print_results.html", context)

    def convert_to_grade(self, obtained_score, full_score):
        """Convert scores to grades based on percentage."""
        if full_score == 0:  # Avoid division by zero
            return "N/A"
        percentage = (obtained_score / full_score) * 100
        if percentage > 90:
            return "A+"
        elif percentage > 80:
            return "A"
        elif percentage > 70:
            return "B+"
        elif percentage > 60:
            return "B"
        elif percentage > 50:
            return "C+"
        elif percentage > 40:
            return "C"
        elif percentage > 35:
            return "D"
        elif percentage == 0:
            return "AB"
        else:
            return "NG"

    def calculate_gpa(self, obtained_score, full_score):
        """Calculate GPA based on scores."""
        if full_score == 0:  # Avoid division by zero
            return 0.0     
        percentage = (obtained_score / full_score) * 100
        if percentage > 90:
            return 4.0
        elif percentage > 80:
            return 3.6
        elif percentage > 70:
            return 3.2
        elif percentage > 60:
            return 2.8
        elif percentage > 50:
            return 2.4
        elif percentage > 40:
            return 2.0
        elif percentage > 35:
            return 1.6
        else:
            return 0.0

    def round_up_gpa(self, gpa):
        """Round GPA up to one decimal place."""
        return ceil(gpa * 10) / 10

    def get_remark(self, obtained_score, full_score):
        if full_score == 0:  # Avoid division by zero
            return ""
        percentage = (obtained_score / full_score) * 100
        if percentage > 90:
            return "Outstanding"
        elif percentage > 80:
            return "Excellent"
        elif percentage > 70:
            return "Very Good"
        elif percentage > 60:
            return "Satisfactory"
        elif percentage > 50:
            return "Pass"
        elif percentage > 40:
            return "Below Average"
        elif percentage > 35:
            return "Poor"
        else:
            return "Fail"
# class PrintResultView(View):
#     def get(self, request, *args, **kwargs):
#         # Fetch all results grouped by student
#         results = Result.objects.filter(session=request.current_session, term=request.current_term)

#         # Dictionary to store student results
#         student_results = {}
#         for result in results:
#             student_id = result.student.id

#             # Initialize student data if not already present
#             if student_id not in student_results:
#                 student_results[student_id] = {
#                     "student": result.student,
#                     "subjects": [],
#                     "total_obt_pract_score": 0,
#                     "total_obt_theory_score": 0,
#                     "total_full_pract_score": 25,
#                     "total_full_theory_score": 75,
#                 }

#             # Append subject details with grades
#             obtained_practical = result.obt_pract_score or 0
#             obtained_theory = result.obt_theory_score or 0
#             full_practical = result.full_pract_score or 25
#             full_theory = result.full_theory_score or 75

#             total_obtained = obtained_practical + obtained_theory
#             total_full = full_practical + full_theory

#             subject_data = {
#                 "subject": result.subject.name,
#                 "obt_pract_score": obtained_practical,
#                 "obt_theory_score": obtained_theory,
#                 "full_pract_score": full_practical,
#                 "full_theory_score": full_theory,
#                 "pract_grade": self.convert_to_grade(obtained_practical, full_practical),
#                 "theory_grade": self.convert_to_grade(obtained_theory, full_theory),
#                 "total_grade": self.convert_to_grade(total_obtained, total_full),
#             }
#             student_results[student_id]["subjects"].append(subject_data)

#             # Accumulate totals
#             student_results[student_id]["total_obt_pract_score"] += obtained_practical
#             student_results[student_id]["total_obt_theory_score"] += obtained_theory
#             student_results[student_id]["total_full_pract_score"] += full_practical
#             student_results[student_id]["total_full_theory_score"] += full_theory
            
            
#         for student_id, data in student_results.items():
#             total_obtained = data["total_obt_pract_score"] + data["total_obt_theory_score"]
#             total_full = data["total_full_pract_score"] + data["total_full_theory_score"]
#             data["final_grade"] = calculate_grade(total_obtained, total_full)    
#         # Pass results to the template
#         context = {
#             "results": student_results
#         }
#         return render(request, "result/print_results.html", context)

#     def convert_to_grade(self, obtained_score, full_score):
#         """Convert scores to grades based on percentage."""
#         if full_score == 0:  # Avoid division by zero
#             return "N/A"
#         percentage = (obtained_score / full_score) * 100
#         if percentage >= 90:
#             return "A+"
#         elif percentage >= 80:
#             return "A"
#         elif percentage >= 70:
#             return "B+"
#         elif percentage >= 60:
#             return "B"
#         elif percentage >= 50:
#             return "C+"
#         elif percentage >= 40:
#             return "C"
#         elif percentage >= 35:
#             return "D"
#         elif percentage == 0:
#             return "AB"
#         else:
#             return "NG"