from django.db import models
from users.models import CustomUser

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    p_img = models.ImageField(blank=True, null=True)
    price = models.IntegerField()
    p_rating_count = models.IntegerField(default=0)
    rating_count_user = models.IntegerField(default=0)

    def get_rating(self):
        return self.p_rating_count//self.rating_count_user if self.rating_count_user != 0 else 0
    
    def __str__(self):
        return self.name

class Feedback(models.Model):
    rating_choices = (
        (5, 'excellent'),
        (4, 'best'),
        (3, 'good'),
        (2, 'satisfactory'),
        (1, 'not-satisfactory'),
        (0, 'not-sure'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feedback = models.TextField(max_length=1000)
    rating = models.IntegerField(default=0, choices=rating_choices)
    reply = models.TextField(max_length=2000, null=True, blank=True, default="no-reply-yet")

    def __str__(self):
        return self.feedback
    

class Help(models.Model):
    help_choices = (
        (5, 'techinical problem'),
        (4, 'warrenty related'),
        (3, 'return releted'),
        (2, 'offer releted'),
        (1, 'product inquiery'),
        (0, 'other'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    help = models.TextField(max_length=1000)
    p_img = models.ImageField(blank=True, null=True)
    reply = models.TextField(max_length=2000, null=True, blank=True, default="no-reply-yet")

    urgency_score = models.IntegerField(default=0, null=True, blank=True)
    help_type = models.IntegerField(default=0, choices=help_choices, blank=True, null=True)

    def __str__(self):
        return str(self.help_type)