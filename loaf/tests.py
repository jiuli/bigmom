import datetime

from django.test import TestCase
from django.utils import timezone

from loaf.models import Question


# Create your tests here.
class QuesitonModelTests(TestCase):
    
    def test_was_published_recently_with_future_question(self):
        
        time = timezone.now() + datetime.timedelta(days=30)
        
        print(time)
        future_question = Question(publish_date=time)
        
        self.assertIs(future_question.was_published_recently(), False, '')
        
        