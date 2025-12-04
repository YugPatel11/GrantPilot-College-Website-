from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .models import Profile, Project , ProjectApplication, IPRApplication, PersonDetails, UtilizationCertificate # Import the new model
from .models import Project, UtilizationRecord
from django.db.models import Sum
from django.contrib import messages

# ------ AUTH VIEWS ------

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.user_type == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('college_dashboard')
    return render(request, 'login.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        user_type = request.POST.get("user_type")

        # Set user_type to 'student' if it's not provided or empty
        if not user_type:
            user_type = "student"

        if password1 != password2:
            return render(request, 'signup.html', {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {"error": "Username already exists."})

        user = User.objects.create_user(username=username, password=password1)

        # Ensure a Profile is created only if one doesn't already exist for the user
        try:
            profile = Profile.objects.get(user=user)
            pass
        except Profile.DoesNotExist:
            Profile.objects.create(user=user, user_type=user_type)


        login(request, user)

        if user_type == "college":
            return redirect("college_dashboard")
        else:
            return redirect("student_dashboard")

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('login')

# ------ STUDENT DASHBOARD ------

@login_required
def student_dashboard(request):
    projects = Project.objects.filter(has_received_grant=True)
    my_projects = ProjectApplication.objects.filter(user=request.user)
    my_iprs = IPRApplication.objects.filter(user=request.user)

    return render(request, 'student/student_dashboard.html', {
        'projects': projects,
        'my_projects': my_projects,
        'my_iprs': my_iprs
    })


def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    application = ProjectApplication.objects.filter(project=project).first()
    return render(request, "student/project_details.html", {
        "project": project,
        "application": application,
    })

@login_required
def personal_project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    application = ProjectApplication.objects.filter(project=project).first()
    return render(request, "student/personal_project_details.html", {
        "project": project,
        "application": application,
    })

@login_required
def apply_for_project(request, project_id):
    project = None
    is_own_project = False

    if project_id != 0:
        project = get_object_or_404(Project, id=project_id)
    else:
        is_own_project = True

    if request.method == "POST":
        email = request.POST.get("email")
        team_size = request.POST.get("team_size")

        leader = PersonDetails.objects.create(
            name=request.POST.get("leader_name"),
            email=request.POST.get("leader_email"),
            enrollment_id=request.POST.get("leader_enrollment"),
            semester=request.POST.get("leader_semester"),
            phone=request.POST.get("leader_phone"),
            school=request.POST.get("leader_school"),
            department=request.POST.get("leader_department"),
        )

        mentor = PersonDetails.objects.create(
            name=request.POST.get("mentor_name"),
            email=request.POST.get("mentor_email"),
            phone=request.POST.get("mentor_phone"),
            school=request.POST.get("mentor_school"),
            department="",
        )

        co_mentor = None
        if request.POST.get("co_mentor_name") and request.POST.get("co_mentor_email"):
            co_mentor = PersonDetails.objects.create(
                name=request.POST.get("co_mentor_name"),
                email=request.POST.get("co_mentor_email"),
                phone="",
                school="",
                department=""
            )

        team_members = []
        for i in ["1", "2", "3", "4"]:
            name = request.POST.get(f"member{i}_name")
            if name:
                member = PersonDetails.objects.create(
                    name=name,
                    email=request.POST.get(f"member{i}_email"),
                    enrollment_id=request.POST.get(f"member{i}_enrollment"),
                    semester=request.POST.get(f"member{i}_semester"),
                    phone=request.POST.get(f"member{i}_phone"),
                    school=request.POST.get(f"member{i}_school"),
                    department=request.POST.get(f"member{i}_department"),
                )
                team_members.append(member)

        app = ProjectApplication.objects.create(
            user=request.user,
            project=project,
            email=email,
            team_size=team_size,
            team_leader=leader,
            mentor=mentor,
            co_mentor=co_mentor,
            status="pending",
        )

        if is_own_project:
            app.project_title = request.POST.get("project_title")
            app.broad_area = request.POST.get("broad_area")
            app.startup_name = request.POST.get("startup_name")
            app.driving_question = request.POST.get("driving_question")
            app.major_problems = request.POST.get("major_problems")
            app.existing_alternatives = request.POST.get("existing_alternatives")
            app.proposed_solution = request.POST.get("proposed_solution")
            app.unique_value_proposition = request.POST.get("unique_value_proposition")
            app.early_adopters = request.POST.get("early_adopters")
            app.sustainability_plan = request.POST.get("sustainability_plan")
            app.timeline = request.POST.get("timeline")
            app.ipr_potential = bool(request.POST.get("ipr_potential"))
            app.financial_consumables = request.POST.get("financial_consumables") or 0
            app.financial_mentoring = request.POST.get("financial_mentoring") or 0
            app.financial_total = request.POST.get("financial_total") or 0

        app.save()
        app.members.set(team_members)

        return redirect("download_ppt")

    return render(request, "student/apply_project.html", {"project": project})

@login_required
def apply_for_ipr(request):
    if request.method == 'POST':
        leader = PersonDetails.objects.create(
            name=request.POST['leader_name'],
            email=request.POST['leader_email'],
            enrollment_id=request.POST['leader_enrollment'],
            semester=request.POST['leader_semester'],
            phone=request.POST['leader_phone'],
            school=request.POST['leader_school'],
            department=request.POST['leader_department']
        )
        mentor = PersonDetails.objects.create(
            name=request.POST['mentor_name'],
            email=request.POST['mentor_email'],
            phone=request.POST['mentor_phone'],
            school=request.POST['mentor_school']
        )
        co_mentor = None
        if request.POST.get('co_mentor_name'):
            co_mentor = PersonDetails.objects.create(
                name=request.POST['co_mentor_name'],
                email=request.POST['co_mentor_email']
            )
        members = []
        for i in range(1, 5):
            if request.POST.get(f'member{i}_name'):
                member = PersonDetails.objects.create(
                    name=request.POST[f'member{i}_name'],
                    email=request.POST[f'member{i}_email'],
                    enrollment_id=request.POST[f'member{i}_enrollment'],
                    semester=request.POST[f'member{i}_semester'],
                    phone=request.POST[f'member{i}_phone'],
                    school=request.POST[f'member{i}_school'],
                    department=request.POST[f'member{i}_department']
                )
                members.append(member)

        app = IPRApplication.objects.create(
            user=request.user,
            invention_title=request.POST['invention_title'],
            patent_description=request.POST['patent_description'],
            num_team_members=request.POST['num_team_members'],
            leader=leader,
            mentor=mentor,
            co_mentor=co_mentor
        )
        app.members.set(members)
        app.save()

        return redirect('student_dashboard')

    return render(request, 'student/apply_ipr.html')

# New views for Utilization Certificates
@login_required
def upload_utilization_certificate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        if 'certificate_image' in request.FILES:
            certificate_image = request.FILES['certificate_image']
            description = request.POST.get('description', '')

            UtilizationCertificate.objects.create(
                project=project,
                uploaded_by=request.user,
                certificate_image=certificate_image,
                description=description
            )
            return redirect('personal_project_details', project_id=project.id)
        else:
            # Handle case where no file is uploaded
            pass # You might want to add a message to the user

    return render(request, 'student/upload_utilization_certificate.html', {'project': project})

@login_required
def view_utilization_certificates(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    certificates = UtilizationCertificate.objects.filter(project=project).order_by('-uploaded_at')
    return render(request, 'utilization_certificates.html', {
        'project': project,
        'certificates': certificates
    })

# ------ COLLEGE DASHBOARD ------

@login_required
def college_dashboard(request):
    try:
        if request.user.profile.user_type == 'student':
            return redirect('unauthorized')
    except Profile.DoesNotExist:
        return redirect('unauthorized')

    projects = Project.objects.filter(has_received_grant=True)
    
    # Get all utilization certificates for college view
    all_utilization_certificates = UtilizationCertificate.objects.all().order_by('-uploaded_at')

    # Calculate the total grant amount by summing from the projects queryset
    total_approved_grant_amount = projects.aggregate(total_amount=Sum('approved_grant_amount'))['total_amount']

    # Calculate the total requested grant amount from all project applications using the 'financial_total' field
    total_requested_grant_amount = ProjectApplication.objects.aggregate(total_requested=Sum('financial_total'))['total_requested']

    # New Logic: Count projects based on their status
    total_applied_projects = ProjectApplication.objects.count()
    # Corrected status filters to use lowercase values
    total_approved_projects = ProjectApplication.objects.filter(status='approved').count()
    total_rejected_projects = ProjectApplication.objects.filter(status='rejected').count()

    # Handle the case where no grants or projects have been submitted yet
    if total_approved_grant_amount is None:
        total_approved_grant_amount = 0
    if total_requested_grant_amount is None:
        total_requested_grant_amount = 0

    return render(request, 'college/college_dashboard.html', {
        'projects': projects,
        'all_utilization_certificates': all_utilization_certificates,
        'total_approved_grant_amount': total_approved_grant_amount,
        'total_requested_grant_amount': total_requested_grant_amount,
        'total_applied_projects': total_applied_projects,
        'total_approved_projects': total_approved_projects,
        'total_rejected_projects': total_rejected_projects,
    
    })

@login_required
def student_requests(request):
    project_requests = ProjectApplication.objects.filter(status='pending')
    ipr_requests = IPRApplication.objects.filter(status='pending')
    return render(request, 'college/student_requests.html', {
        'project_requests': project_requests,
        'ipr_requests': ipr_requests
    })

@login_required
def approve_request(request, app_type, app_id):
    if app_type == 'project':
        app = get_object_or_404(ProjectApplication, id=app_id)
    else:
        app = get_object_or_404(IPRApplication, id=app_id)

    if request.method == 'POST':
        action = request.POST['action']
        grant_amount = request.POST.get('grant_amount')

        if action in ['approve', 'approve_modification']:
            app.status = 'approved' if action == 'approve' else 'approved_modification'

            if grant_amount and app_type == 'project':
                app.approved_grant_amount = grant_amount

                if app.project:
                    app.project.has_received_grant = True
                    app.project.approved_grant_amount = grant_amount
                    app.project.save()
                else:
                    new_project = Project.objects.create(
                        title=app.project_title,
                        broad_area=app.broad_area,
                        startup_name=app.startup_name,
                        driving_question=app.driving_question,
                        major_problems=app.major_problems,
                        existing_alternatives=app.existing_alternatives,
                        proposed_solution=app.proposed_solution,
                        unique_value_proposition=app.unique_value_proposition,
                        early_adopters=app.early_adopters,
                        sustainability_plan=app.sustainability_plan,
                        timeline=app.timeline,
                        ipr_potential=app.ipr_potential,
                        financial_consumables=app.financial_consumables,
                        financial_mentoring=app.financial_mentoring,
                        financial_total=grant_amount,
                        has_received_grant=True,
                        approved_grant_amount=grant_amount,
                    )
                    app.project = new_project

        elif action == 'reject':
            app.status = 'rejected'

        app.save()
        return redirect('student_requests')

    return render(request, 'college/approve_request.html', {'app': app, 'type': app_type})

@login_required
def add_project(request):
    if request.method == 'POST':
        project = Project.objects.create(
            title=request.POST['title'],
            broad_area=request.POST['broad_area'],
            startup_name=request.POST['startup_name'],
            driving_question=request.POST['driving_question'],
            major_problems=request.POST['major_problems'],
            existing_alternatives=request.POST['existing_alternatives'],
            proposed_solution=request.POST['proposed_solution'],
            unique_value_proposition=request.POST['unique_value_proposition'],
            early_adopters=request.POST['early_adopters'],
            sustainability_plan=request.POST['sustainability_plan'],
            timeline=request.POST['timeline'],
            ipr_potential=('ipr_potential' in request.POST),
            has_received_grant=('has_received_grant' in request.POST),
            approved_grant_amount=request.POST.get('approved_grant_amount', 0) or 0
        )

        team_leader = TeamLeader.objects.create(
            name=request.POST['leader_name'],
            email=request.POST['leader_email'],
            enrollment_id=request.POST['leader_enrollment_id'],
            semester=request.POST['leader_semester'],
            phone=request.POST['leader_phone'],
            school=request.POST['leader_school'],
            department=request.POST['leader_department']
        )

        mentor = Mentor.objects.create(
            name=request.POST['mentor_name'],
            email=request.POST['mentor_email'],
            phone=request.POST['mentor_phone'],
            school=request.POST['mentor_school']
        )

        co_mentor = None
        if request.POST.get('co_mentor_name') and request.POST.get('co_mentor_email'):
            co_mentor = CoMentor.objects.create(
                name=request.POST['co_mentor_name'],
                email=request.POST['co_mentor_email']
            )

        application = Application.objects.create(
            project=project,
            team_leader=team_leader,
            mentor=mentor,
            co_mentor=co_mentor
        )

        for i in range(1, 5):
            member_name = request.POST.get(f'member_name_{i}')
            if member_name:
                Member.objects.create(
                    application=application,
                    name=member_name,
                    email=request.POST.get(f'member_email_{i}', ''),
                    enrollment_id=request.POST.get(f'member_enrollment_{i}', ''),
                    semester=request.POST.get(f'member_semester_{i}', ''),
                    phone=request.POST.get(f'member_phone_{i}', ''),
                    school=request.POST.get(f'member_school_{i}', ''),
                    department=request.POST.get(f'member_department_{i}', '')
                )

        return redirect('college_dashboard')
    
    return render(request, 'college/add_project.html')

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    application = ProjectApplication.objects.filter(project=project).first()

    if request.method == 'POST':
        # Update Project fields
        project.title = request.POST.get('title', project.title)
        project.broad_area = request.POST.get('broad_area', project.broad_area)
        project.startup_name = request.POST.get('startup_name', project.startup_name)
        project.driving_question = request.POST.get('driving_question', project.driving_question)
        project.major_problems = request.POST.get('major_problems', project.major_problems)
        project.existing_alternatives = request.POST.get('existing_alternatives', project.existing_alternatives)
        project.proposed_solution = request.POST.get('proposed_solution', project.proposed_solution)
        project.unique_value_proposition = request.POST.get('unique_value_proposition', project.unique_value_proposition)
        project.early_adopters = request.POST.get('early_adopters', project.early_adopters)
        project.sustainability_plan = request.POST.get('sustainability_plan', project.sustainability_plan)
        project.timeline = request.POST.get('timeline', project.timeline)
        project.ipr_potential = 'ipr_potential' in request.POST
        project.has_received_grant = 'has_received_grant' in request.POST
        
        # Handle numerical fields, ensuring they default to 0 if empty or invalid
        project.approved_grant_amount = float(request.POST.get('approved_grant_amount') or 0)
        project.financial_consumables = float(request.POST.get('financial_consumables') or 0)
        project.financial_mentoring = float(request.POST.get('financial_mentoring') or 0)
        project.financial_total = float(request.POST.get('financial_total') or 0)

        # Handle file uploads
        if 'group_photo' in request.FILES:
            project.group_photo = request.FILES['group_photo']
        # If the user clears the existing photo without uploading a new one, you might want to handle that too.
        # For example, if you have a hidden field or a specific checkbox for "clear photo".
        # For now, if no new file is provided, the existing one will remain unless explicitly set to None.
        elif request.POST.get('clear_group_photo_checkbox'): # Example of a "clear" checkbox
            project.group_photo = None # Or clear the file if it's already there and not replaced

        if 'product_photo' in request.FILES:
            project.product_photo = request.FILES['product_photo']
        elif request.POST.get('clear_product_photo_checkbox'): # Example
            project.product_photo = None

        project.save()

        # Update Mentor, Co-Mentor, Leader if application exists
        if application:
            leader = application.team_leader
            leader.name = request.POST.get('leader_name', leader.name)
            leader.email = request.POST.get('leader_email', leader.email)
            leader.enrollment_id = request.POST.get('leader_enrollment_id', leader.enrollment_id)
            leader.semester = request.POST.get('leader_semester', leader.semester)
            leader.phone = request.POST.get('leader_phone', leader.phone)
            leader.school = request.POST.get('leader_school', leader.school)
            leader.department = request.POST.get('leader_department', leader.department)
            leader.save()

            mentor = application.mentor
            mentor.name = request.POST.get('mentor_name', mentor.name)
            mentor.email = request.POST.get('mentor_email', mentor.email)
            mentor.phone = request.POST.get('mentor_phone', mentor.phone)
            mentor.school = request.POST.get('mentor_school', mentor.school)
            mentor.save()

            if application.co_mentor:
                co_mentor = application.co_mentor
                co_mentor.name = request.POST.get('co_mentor_name', co_mentor.name)
                co_mentor.email = request.POST.get('co_mentor_email', co_mentor.email)
                co_mentor.save()

            # Update Members (loop through existing ones)
            members = application.members.all()
            for i, member in enumerate(members, start=1):
                member.name = request.POST.get(f'member_name_{i}', member.name)
                member.email = request.POST.get(f'member_email_{i}', member.email)
                member.enrollment_id = request.POST.get(f'member_enrollment_{i}', member.enrollment_id)
                member.semester = request.POST.get(f'member_semester_{i}', member.semester)
                member.phone = request.POST.get(f'member_phone_{i}', member.phone)
                member.school = request.POST.get(f'member_school_{i}', member.school)
                member.department = request.POST.get(f'member_department_{i}', member.department)
                member.save()

        # Assuming 'college_dashboard' is the name of your URL pattern for the dashboard
        return redirect('college_dashboard')

    return render(request, 'college/edit_project.html', {
        'project': project,
        'application': application,
    })

@login_required
def delete_project(request, project_id):
    """
    This view 'deletes' a project by changing its status to 'rejected'
    and reducing the approved grant amount.
    """
    try:
        # Get the Project instance and its application
        project = get_object_or_404(Project, id=project_id)
        project_application = ProjectApplication.objects.get(project=project)
        
        # Update the status of the ProjectApplication
        project_application.status = 'rejected'
        project_application.save()
        
        # Reduce the approved grant amount and set has_received_grant to False
        project.approved_grant_amount = 0
        project.has_received_grant = False
        project.save()

    except ProjectApplication.DoesNotExist:
        # Handle cases where the application might not exist
        pass

    # Redirect the user back to the college dashboard
    return redirect('college_dashboard')

# ------ OTHER TEMP VIEWS ------

def Forgot_Password(request):
    return render(request, 'Forgot_Password.html')


def unauthorized_view(request):
    return render(request, 'college/unauthorized.html')


def index(request):
    projects = Project.objects.filter(has_received_grant=True)
   

    return render(request, 'index.html', {
        'projects': projects,
    })

def update_group_photo(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST" and request.FILES.get("group_photo"):
        project.group_photo = request.FILES["group_photo"]
        project.save()
        messages.success(request, "Group photo updated successfully!")
    return redirect("personal_project_details", project_id=project.id)


def update_product_photo(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST" and request.FILES.get("product_photo"):
        project.product_photo = request.FILES["product_photo"]
        project.save()
        messages.success(request, "Product photo updated successfully!")
    return redirect("personal_project_details", project_id=project.id)


@login_required
def download_ppt(request):
    return render(request, 'student/Download_presentation.html')


def save_utilization(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        item = request.POST.get('item')
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        bill = request.FILES.get('bill_of_utilization')

        if item and date and amount and bill:
            UtilizationRecord.objects.create(
                project=project,
                item=item,
                date=date,
                amount=amount,
                bill_of_utilization=bill
            )
        return redirect('personal_project_details', project_id=project_id)

    return redirect('personal_project_details', project_id=project_id) 


@login_required
def approve_ipr_request(request, app_type, app_id):
    if app_type == 'project':
        app = get_object_or_404(ProjectApplication, id=app_id)
    else:
        app = get_object_or_404(IPRApplication, id=app_id)

    if request.method == 'POST':
        action = request.POST['action']
        grant_amount = request.POST.get('grant_amount')

        if action in ['approve', 'approve_modification']:
            app.status = 'approved' if action == 'approve' else 'approved_modification'

            if grant_amount and app_type == 'project':
                app.approved_grant_amount = grant_amount

                if app.project:
                    app.project.has_received_grant = True
                    app.project.approved_grant_amount = grant_amount
                    app.project.save()
                else:
                    new_project = Project.objects.create(
                        title=app.project_title,
                        broad_area=app.broad_area,
                        startup_name=app.startup_name,
                        driving_question=app.driving_question,
                        major_problems=app.major_problems,
                        existing_alternatives=app.existing_alternatives,
                        proposed_solution=app.proposed_solution,
                        unique_value_proposition=app.unique_value_proposition,
                        early_adopters=app.early_adopters,
                        sustainability_plan=app.sustainability_plan,
                        timeline=app.timeline,
                        ipr_potential=app.ipr_potential,
                        financial_consumables=app.financial_consumables,
                        financial_mentoring=app.financial_mentoring,
                        financial_total=grant_amount,
                        has_received_grant=True,
                        approved_grant_amount=grant_amount,
                    )
                    app.project = new_project

        elif action == 'reject':
            app.status = 'rejected'

        app.save()
        return redirect('student_requests')

    return render(request, 'college/approve_request_ipr.html', {'app': app, 'type': app_type})