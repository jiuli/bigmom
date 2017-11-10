import datetime

from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone

from loaf.models import Question


# Create your tests here.
def create_question(question_text, days):
    time = timezone.now - datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text,publish_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('loaf:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No loaf are available.')
        self.assertQuerysetEqual(response.context['question_list'], [])
        
class QuesitonModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(publish_date=time)
        self.assertIs(old_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, seconds=1)
        recent_question = Question(publish_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
        
    def test_was_published_recently_with_future_question(self):
        
        time = timezone.now() + datetime.timedelta(days=30)
        
        print(time)
        future_question = Question(publish_date=time)
        
        self.assertIs(future_question.was_published_recently(), False, '')
        
        