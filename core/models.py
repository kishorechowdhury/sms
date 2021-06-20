from enum import unique
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

STATUS = (
    ('i', 'Initialized'),
    ('w', 'Working'),
    ('c', 'Complete'),
)
# Create your models here.
# class Technology(models.Model):
#     """Model representing a Technology (e.g. Python, Angular etc.)"""
#     name = models.CharField(max_length=50,
#                             help_text="Enter technologies (e.g. Python, Angular etc.)")

#     def __str__(self):
#         """String for representing the Model object (in Admin site etc.)"""
#         return self.name


class Project(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField('Start Date')
    end_date = models.DateField('End Date')
    
    status = models.CharField(max_length=1, choices=STATUS, default='i', help_text='Current Status')
    short_desc = models.CharField('Short Description', max_length=255, help_text='Short Description')
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('core:dashboard')
    

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # def __str__(self) -> str:
    #     return f'Member of - {self.project.name}'

    class Meta:
        verbose_name_plural = 'Project Members'
        constraints = [
            models.UniqueConstraint(name='unique_member', fields=['project', 'user'])
        ]

    def get_absolute_url(self):
        return reverse('core:projectmember-create')

class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular ticket across whole system')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=1, choices=STATUS, default='i', help_text='Current Status')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    details = models.CharField(max_length=255)
    date_i = models.DateField('Date Initialized', auto_now=True)
    date_w = models.DateTimeField('Date Working', null=True, blank=True)
    date_c = models.DateTimeField('Date Complete', null=True, blank=True)

    class Meta:
        permissions = (('can_mark_working', 'Set ticket as working'),('can_mark_complete', 'Set ticket as complete'),)

    def get_absolute_url(self):
        return reverse('core:ticket-create')


class UserActivity(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ticket = models.ForeignKey(Ticket, null=True, on_delete=models.SET_NULL)
    action_date = models.DateTimeField('Datetime', auto_now=True)
    action = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'User Activities'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    designation = models.CharField(max_length=50, null=True, blank=True, default='Employee')
    SEX_CHOICE = (
        ('m', 'Male'),
        ('f', 'Female'),
    )
    sex = models.CharField('Gender', max_length=1, choices=SEX_CHOICE, default='m')