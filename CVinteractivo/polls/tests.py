from cgi import test
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question

class QuestionModelsTest(TestCase):

    def setUp(self):
        self.test_question = Question(question_text="¿Quién es el mejor course Directos de Platzi?")

    def test_was_published_recently_future_questions(self):
        """was_published_recently return False for question whose pub_date is in the future"""
       
        time = timezone.now() + datetime.timedelta(days=30)
        self.test_question.pub_date = time
        self.assertIs(self.test_question.was_published_recently(), False)

    def test_was_published_recently_past_questions(self):
        """was_published_recently return False for question whose pub_date is in past"""
      
        time = timezone.now() - datetime.timedelta(days=15)
        self.test_question.pub_date = time
        self.assertIs(self.test_question.was_published_recently(), False)
    
    def test_was_published_recently_present_questions(self):
        """was_published_recently return False for question whose pub_date is in present"""
      
        time = timezone.now()
        self.test_question.pub_date = time
        self.assertIs(self.test_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    create a question with the given "Question_test", and published the given
    number of days offset to now (negative for question published in the past,
    positive for question that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """If no question exist, an appropiate messege is diplayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """
        Question with a pub_date in the future aren't displayed on the index page.
        """
        create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Question with a pub_date in the past are displayed on the index page.
        """
        question = create_question("Past question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past question are displayed
        """
        past_question = create_question(question_text="Past question", days=-30)
        future_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )

    def test_two_past_question(self):
        """
        The question index page may display multiple questions.
        """
        past_question1 = create_question(question_text="Past question 1", days=-30)
        past_question2 = create_question(question_text="Past question 2", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )

    def test_two_future_question(self):
        """
        The question index page may display multiple questions.
        """
        future_question1 = create_question(question_text="Future question 1", days=30)
        future_question2 = create_question(question_text="Future question 2", days=40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            []
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        return a 404 error not found
        """
        future_question = create_question(question_text="Future question", days=30)
        url = reverse("polls:detail", args=[future_question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displayed the question's text
        """
        past_question = create_question(question_text="past question", days=-30)
        url = reverse("polls:detail", args=[past_question.id])
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)