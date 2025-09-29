from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('college', 'College'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


# ----- PROJECT MODELS -----

class Project(models.Model):
    title = models.CharField(max_length=255, default="Untitled Project")
    broad_area = models.CharField(max_length=100, default="General")
    startup_name = models.CharField(max_length=255, blank=True)
    driving_question = models.TextField(default="No driving question provided.")
    major_problems = models.TextField(default="No major problems provided.")
    existing_alternatives = models.TextField(default="No existing alternatives provided.")
    proposed_solution = models.TextField(default="No proposed solution provided.")
    unique_value_proposition = models.TextField(default="No unique value proposition provided.")
    early_adopters = models.TextField(default="No early adopters specified.")
    sustainability_plan = models.TextField(default="No sustainability plan provided.")
    timeline = models.TextField(default="No timeline specified.")
    ipr_potential = models.BooleanField(default=False)
    financial_consumables = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    financial_mentoring = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    financial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    has_received_grant = models.BooleanField(default=False)
    approved_grant_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # New fields for photos
    group_photo = models.ImageField(upload_to='project_photos/group/', null=True, blank=True)
    product_photo = models.ImageField(upload_to='project_photos/product/', null=True, blank=True)

    def __str__(self):
        return self.title


# ----- TEAM MODELS -----

class PersonDetails(models.Model):
    name = models.CharField(max_length=255, default="Unnamed Person")
    email = models.EmailField(default="noemail@example.com")
    enrollment_id = models.CharField(max_length=100, blank=True, default="")
    semester = models.CharField(max_length=50, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    school = models.CharField(max_length=255, blank=True, default="")
    department = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name

class ProjectApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    team_size = models.IntegerField()
    team_leader = models.OneToOneField(PersonDetails, related_name='leader', on_delete=models.CASCADE)
    mentor = models.OneToOneField(PersonDetails, related_name='mentor', on_delete=models.CASCADE)
    co_mentor = models.OneToOneField(PersonDetails, related_name='co_mentor', on_delete=models.SET_NULL, null=True, blank=True)
    members = models.ManyToManyField(PersonDetails, related_name='members')
    status = models.CharField(max_length=50, default='pending')

    # Additional project fields for own projects
    project_title = models.CharField(max_length=255, null=True, blank=True)
    broad_area = models.CharField(max_length=255, null=True, blank=True)
    startup_name = models.CharField(max_length=255, null=True, blank=True)
    driving_question = models.TextField(null=True, blank=True)
    major_problems = models.TextField(null=True, blank=True)
    existing_alternatives = models.TextField(null=True, blank=True)
    proposed_solution = models.TextField(null=True, blank=True)
    unique_value_proposition = models.TextField(null=True, blank=True)
    early_adopters = models.TextField(null=True, blank=True)
    sustainability_plan = models.TextField(null=True, blank=True)
    timeline = models.TextField(null=True, blank=True)
    ipr_potential = models.BooleanField(default=False)
    financial_consumables = models.IntegerField(null=True, blank=True)
    financial_mentoring = models.IntegerField(null=True, blank=True)
    financial_total = models.IntegerField(null=True, blank=True)
    approved_grant_amount = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.project:
            return f"Application by {self.user.username} for {self.project.title}"
        else:
            return f"Application by {self.user.username} for Own Startup"


class IPRApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('approved_modification', 'Approved with Modification'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invention_title = models.CharField(max_length=255, default="Untitled Invention")
    patent_description = models.TextField(default="No patent description provided.")
    num_team_members = models.IntegerField(default=1)
    leader = models.OneToOneField(PersonDetails, on_delete=models.CASCADE, related_name='ipr_leader')
    mentor = models.OneToOneField(PersonDetails, on_delete=models.CASCADE, related_name='ipr_mentor')
    co_mentor = models.OneToOneField(PersonDetails, on_delete=models.CASCADE, related_name='ipr_co_mentor', null=True, blank=True)
    members = models.ManyToManyField(PersonDetails, related_name='ipr_team_members', blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"IPR Application by {self.user.username} - {self.invention_title}"

class UtilizationCertificate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='utilization_certificates')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    certificate_image = models.ImageField(upload_to='utilization_certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Certificate for {self.project.title} by {self.uploaded_by.username}"
    
class UtilizationRecord(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='utilization_records')
    item = models.CharField(max_length=255)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_of_utilization = models.FileField(upload_to='bills/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} for Project {self.project.title}"