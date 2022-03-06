from fastapi.templating import Jinja2Templates
from fastapi import status
from fastapi.responses import RedirectResponse
from repository import admin, hod, attendence, teacher
from database import database, models
from collections import defaultdict

templates = Jinja2Templates('templates/html_files')



class AdminTemplates():

    def admin_login_page(request, verify = 'none'):
        return templates.TemplateResponse('admin_login.html', 
                context={'request': request, 'title': 'Admin Login', 'verify': verify})

    def login_success(request):
        courses_with_department = defaultdict(lambda: [])
        db = database.SessionLocal()
        hods = admin.get_all(db, template=True)
        dep = admin.get_all_departments(db, template=True)
        course = admin.get_all_course(db, template=True)

        for i in course: courses_with_department[i.Department].append(i.Course_name_alias)
        db.close()
        return templates.TemplateResponse('adminPortal.html', 
                    context={'request': request, 'title': 'Admin Portal',
                            'hods': hods, 'dep': dep, 'course': course, 
                            'cw': courses_with_department})

    def login_success_redirect():
        return RedirectResponse(url = '/admin/details', status_code=status.HTTP_302_FOUND)


    def login_error_redirect():
        return RedirectResponse(url='/admin/login', status_code=status.HTTP_302_FOUND)

    def details(request, db):
        courses_with_department = defaultdict(lambda: [])
        hods = admin.get_all(db, template=True)
        dep = admin.get_all_departments(db, template=True)
        course = admin.get_all_course(db, template=True)

        for i in course: courses_with_department[i.Department].append(i.Course_name_alias)
        tmp = templates.TemplateResponse("adminDetails.html",
                    context={'request': request, 'title': "Details",
                             'hods': hods, 'dep': dep,
                             'cw': courses_with_department})
        
        return tmp

    def hod(request, db):
        dep = admin.get_all_departments(db, template=True)
        tmp = templates.TemplateResponse("adminHod.html",
                    context={"request": request, "title": "Hod",
                             "dep": dep})
        return tmp
    
    def department(request, db):
        course = admin.get_all_course(db, template=True)
        dep = admin.get_all_departments(db, template=True)
        tmp = templates.TemplateResponse("adminDepartment.html",
                    context={'request': request, 'title': 'Department',
                             "dep": dep, "course": course})
        return tmp

    def credential(request):
        tmp = templates.TemplateResponse("adminCredential.html",
                    context={'request': request, 'title': 'Credential'})

        return tmp


    def unverified(request):
        db = database.SessionLocal()
        hod = db.query(models.PendingVerificationImage).filter(models.PendingVerificationImage.hod_or_teacher == 'H')
        teacher = db.query(models.PendingVerificationImage).filter(models.PendingVerificationImage.hod_or_teacher == 'T')
        db.close()

        tmp = templates.TemplateResponse("adminUnverified.html",
                    context={'request': request, 'title': 'Unverified Users', 
                        'hods': hod, 'teachers': teacher})
        return tmp

    def teachers_list(request, db):
        teachers = db.query(models.Teachers).all()
        list_empty = False if teachers else True

        tmp = templates.TemplateResponse("adminTeachersView.html",
                            context={'request': request, 'title': 'Collage Teachers',
                                        'teachers': teachers, 'list_empty': list_empty})
        return tmp


class OthersTemplates():
    
    def verify(request, id):
        db = database.SessionLocal()
        user = db.query(models.PendingVerificationImage).filter(models.PendingVerificationImage.id == id).first()
        db.close()
        tmp = templates.TemplateResponse("verify_page.html", 
            context={'request': request, 'valid': user, 'user': user})

        return tmp

    def login_page(request, verify=False, message = 'Login Page'):
        tmp = templates.TemplateResponse('login.html',
                context={'request': request,
                         'verify': verify,
                         'message': message})
        return tmp

    def login_redirect_page(request, who):
        if who == 'hod':
            return RedirectResponse(url = '/hod/workspace', status_code=status.HTTP_302_FOUND)
        else:
            return RedirectResponse(url = '/teacher/workspace', status_code=status.HTTP_302_FOUND)

    def login_error_redirect():
        return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

class HodTemplates():

    def workspace(request, user, db):
        classes = sorted(teacher.get_hour_detail(db, user.user_name), key = lambda x: x.hour)
        tmp = templates.TemplateResponse("hodWorkspace.html",
                        context={"request": request, 
                             "title": "Workspace",
                             "user": user.name, 
                             "free_day": False if len(classes) >= 1 else True,
                             "classes": classes})
        return tmp

    def timetable(request, user, db):
        # db = database.SessionLocal()
        courses = db.query(models.Courses).filter(models.Courses.Department == user.department)
        # courses = admin.get_all_course(db)
        teachers = hod.get_full_teacher_details(db)
        hods = admin.get_all(db, template=True)
        # depart = db.query(models.)
        # depart = admin.get_all_departments(db)
        # db.close()
        return templates.TemplateResponse('timeTable.html', 
                context={'request': request, 'title': 'Time Table', 
                        'courses': courses, 'teachers': teachers, 
                        'hods': hods, 'department': user.department})

    def appoint_teacher(request, user):
        db = database.SessionLocal()
        teachers = hod.get_techer_details(db, user, template=True)
        # depart = admin.get_all_departments(db, template=True)
        db.close()
        tmp = templates.TemplateResponse("appointTeacher.html",
                context={'request': request, "title": "Appoint Teachers", 
                         "teachers": teachers, "depart": user.department})
        return tmp


    def addStudents(request, user, db):
        courses = db.query(models.Courses).filter(models.Courses.Department == user.department)

        tmp = templates.TemplateResponse("addStudent.html",
                context={"request": request, "title": "Add Students",
                         "course": courses, "who": True})
        return tmp

    def search_students(request, user, db):
        students = db.query(models.Students).all()
        list_empty = False if len(students) else True
        tmp = templates.TemplateResponse("hodSearchStudents.html",
                context={"request": request, "title": "Search Students",
                        "list_empty": list_empty,
                        "students": students
                        })
        return tmp

    def uoc_notification(request):
        notifications = hod.uoc.get_notifications()
        return templates.TemplateResponse("uocNotification.html",
                context={"request": request, "title": "Notifications", "notfy": notifications})
    
    def exam_notification(request):
        notifications = hod.uoc.get_exam_notifications()
        res = templates.TemplateResponse("uocExamTimetable.html",
                context={"request": request, "title": "Exam Notifications", "notfy": notifications})
        return res
    
    def attendenceDataView(request, user):
        db = database.SessionLocal()
        courses = db.query(models.Courses).filter(models.Courses.Department == user.department)
        # courses = admin.get_all_course(db)
        db.close()
        tmp = templates.TemplateResponse("attendenceDataView.html",
                context={"request": request, "title": "Attendence Data",
                        "course": courses})
        return tmp

    def students(request, user, db):
        courses = db.query(models.Courses).filter(models.Courses.Department == user.department)
        # courses = admin.get_all_course(db)
        tmp = templates.TemplateResponse("hodStudents.html",
                context={"request": request, "title": "Student Info",
                        "course": courses})
        return tmp

    def takeAttendence(request):
        db = database.SessionLocal()
        courses = admin.get_all_course(db)
        db.close()
        tmp = templates.TemplateResponse("takeAttendence.html",
                context={"request": request, "title": "Students Attendence",
                         "who":"hod", "course": courses})

        return tmp

    def show_attendence_data(request, data):
        column, values = attendence.show_attendence_data(request=data)
        data_in = len(values) >= 1
        tmp = templates.TemplateResponse("showAttendenceData.html",
                    context={"request": request, "title": "Attendence Sheet",
                                "column": column, "values": values, 
                                "data": data, "data_in": data_in})

        return tmp

    def show_student_details(request, course, year):
        db = database.SessionLocal()
        details = hod.get_student_details(db, course, year, template=True)
        db.close()
        tmp = templates.TemplateResponse("studentDetails.html",
                    context={"request": request, "title": "Attendence Sheet",
                                "details": details, "course": course, "year": year})

        return tmp

    def show_most_absentees(request, data):
        most_absentee, there_is, working_days = attendence.most_absentee(request=data, open_daily=True)
        tmp = templates.get_template("__mostabsentee.html")
        tmp = tmp.render(request = request, mostabsentee = most_absentee, 
                         there_is=there_is, working_days = working_days)
        return tmp


    def show_report(request, data):
        final_report = attendence.attendence_analysing(request=data, open_daily=True).values
        tmp = templates.get_template("__attendencereport.html")
        tmp = tmp.render(request = request, final_report = final_report)
        return tmp
    
    def latest_notfications(request, which_notification):
        if which_notification == 'exam':
            data = hod.uoc.get_latest_exam_notifications()
        else:
            data = hod.uoc.get_latest_notifications()
        tmp = templates.get_template("__latestNotifications.html")
        tmp = tmp.render(request = request, notify = data)
        return tmp
    
    def message(request):
        tmp = templates.TemplateResponse("message.html",
                        context={"request": request, "title": "Message"})
        return tmp

    def get_full_messages(request, db, user):
        data = hod.get_full_message(db = db, user = user)
        is_data_there = len(data) >= 1
        tmp = templates.get_template("__message.html")
        tmp = tmp.render(request = request, data = data, is_data_there = is_data_there)
        return tmp

    def profile(request, user):
        scode = user.user_name[-4:]
        tmp = templates.TemplateResponse("hodProfile.html",
                    context={'request': request, "title": 'Profile',
                         'user': user, 'scode': scode})
        return tmp

    def myclasses(request, db, user):
        data = teacher.my_timetable(db, user.user_name)
        tmp = templates.TemplateResponse("teacherTimetable.html",
                            context={"request": request, "title": "My Classes",
                                "data": data, "head": True})
        return tmp

class TeacherTemplates():
    
    def workspace(request, db, user):
        classes = sorted(teacher.get_hour_detail(db, user.username), key = lambda x: x.hour)
        free_day = False if len(classes) >= 1 else True
        tmp = templates.TemplateResponse("teacherWorkspace.html",
                        context={"request": request, "title": "Workspace",
                                 "free_day": free_day, "classes": classes,
                                 "user": user.name})
        return tmp 

    def students(request, db, user = None):
        courses = db.query(models.Courses).filter(models.Courses.Department == user.department)
        tmp = templates.TemplateResponse("teacherStudentDeatils.html",
                                        context={"request": request, 
                                        "title": "Student",
                                        "course": courses,})
        return tmp

    
    def show_student_details(request, course, year, db):
        details = hod.get_student_details(db, course, year, template=True)
        tmp = templates.TemplateResponse("_teacherStudentDetails.html",
                    context={"request": request, "title": "Attendence Sheet",
                                "details": details, "course": course, "year": year})

        return tmp

    def message(request, db, user):
        tmp = templates.TemplateResponse("teacherMessageViews.html",
                        context={"request": request, "title": "Messages"})
        return tmp
    
    def get_messages(request, db, new_five, user):
        data = teacher.get_messages(user, db, new_five)
        is_data_there = len(data) >= 1
        tmp = templates.get_template("__message.html")
        tmp = tmp.render(request = request, data = data, is_data_there = is_data_there)
        return tmp

    def timetable(request, db, user):
        data = teacher.my_timetable(db, user.username)
        tmp = templates.TemplateResponse("teacherTimetable.html",
                            context={"request": request, "title": "My Classes",
                                "data": data, "head": False})
        return tmp

    def takeAttendence(request):
        db = database.SessionLocal()
        courses = admin.get_all_course(db)
        db.close()
        tmp = templates.TemplateResponse("takeAttendence.html",
                context={"request": request, "title": "Students Attendence",
                         "who":"teacher", "course": courses})

        return tmp

    def addStudents(request, user, db):
        courses = db.query(models.Courses).filter(models.Courses.Department == user.department)

        tmp = templates.TemplateResponse("addStudent.html",
                context={"request": request, "title": "Add Students",
                         "course": courses, "who": False})
        return tmp

    def profile(request, user):
        scode = user.username[-4:]
        tmp = templates.TemplateResponse("teacherProfile.html",
                    context={'request': request, "title": 'Profile',
                         'user': user, 'scode': scode})
        return tmp