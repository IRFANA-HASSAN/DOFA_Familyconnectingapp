from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        help_text='Phone number with country code'
    )
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    job = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_profile_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class FamilyRelationship(models.Model):
    """Stores directed family relationship requests and links.

    from_user → to_user with a relationship_type. Optional middle_user and
    free-form label can be stored for UI display.
    """

    RELATIONSHIP_CHOICES = [
        ("father", "Father"),
        ("mother", "Mother"),
        ("son", "Son"),
        ("daughter", "Daughter"),
        ("brother", "Brother"),
        ("sister", "Sister"),
        ("husband", "Husband"),
        ("wife", "Wife"),
        ("uncle", "Uncle"),
        ("aunt", "Aunt"),
        ("cousin", "Cousin"),
        ("nephew", "Nephew"),
        ("niece", "Niece"),
        ("friend", "Friend"),
        ("spouse", "Spouse"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_relationships")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_relationships")
    relationship_type = models.CharField(max_length=30)

    # Optional middle person in the chain (shown in the popup UI)
    middle_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="middle_relationships")

    # Optional UI label (e.g., custom text shown in chips)
    relation_label = models.CharField(max_length=60, blank=True)

    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Family Relationship"
        verbose_name_plural = "Family Relationships"
        indexes = [
            models.Index(fields=["from_user", "to_user", "relationship_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.from_user.username} → {self.to_user.username} ({self.relationship_type}, {self.status})"
