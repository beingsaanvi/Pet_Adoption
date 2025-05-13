from django.db import models

class Pet(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    adopted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name