from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# organization part has been started 

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin','Admin'),
        ('manager', 'Manager'),
        ('employee','Employee')
    )

# role choices should be a booloen field 

# multi managers are allowed
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    full_name=models.CharField(max_length=100)
    email= models.EmailField(unique=True)
    contact=models.CharField(max_length=15)
    role= models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.full_name} ({self.role})'
    

    def is_profile_admin(self):
        return self.role== 'admin'
    
    def is_manager(self):
        return self.role =='manager'
    
    def is_employee(self):
        return self.role == 'employee'

# organization model one user can be have in  multiple organization 

class Organization(models.Model):
    ORGANIZATION_CHOICES = (
        ('techsnap', 'Techsnap'),
        ('datasnap', 'Datasnap'),
        ('moviesnap', 'Moviesnap'),
    )
    organization_name = models.CharField(max_length=100, choices=ORGANIZATION_CHOICES, unique=True)
    # One admin per organization
    admin = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='organization_admin'
    )  
     # One manager per organization
    manager = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='organization_manager'
    ) 
    employees = models.ManyToManyField(
        Profile, related_name='organization_employees', blank=True
    )  # Employees in the organization

    def __str__(self):
        return self.organization_name
    

# organization name when it is created
# one text value -- no.of_employees   
# is created 
