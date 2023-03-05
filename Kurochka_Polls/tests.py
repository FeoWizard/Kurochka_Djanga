import datetime

from django.test  import TestCase
from django.utils import timezone
from django.urls  import reverse
from .models      import Question


class QuestionModelTests(TestCase):


    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose publish_date is in the future.
        """
        time            = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(publish_date = time)
        self.assertIs(future_question.was_published_recently(), False)


    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose publish_date is older than 1 day.
        """
        time            = timezone.now() - datetime.timedelta(days = 1, seconds = 1)
        old_question    = Question(publish_date = time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose publish_date is within the last day.
        """
        time            = timezone.now() - datetime.timedelta(hours = 23, minutes = 59, seconds = 59)
        recent_question = Question(publish_date = time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Создаёт опрос с заданным текстом и устанавливая дату побликации как оффсет от текущей даты в "days"

    now() + days
    now() - days

    :param question_text:
    :param days:
    :return:
    """
    publish_date = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text = question_text, publish_date = publish_date)


class QuestionIndexViewTests(TestCase):


    def test_no_questions(self):
        """
        Если опросов нет - должно выводиться соответсвующее сообщение
        """
        response = self.client.get(reverse('Kurochka_Polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Нет доступных опросов.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_past_question(self):
        """
        Опросы с publish_date в прошедшем времени - должны отображаться на индексной странице.
        """
        question = create_question(question_text = "Прошедший опрос", days = -30)
        response = self.client.get(reverse('Kurochka_Polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [ question ])


    def test_future_question(self):
        """
        Опросы с publish_date в будущем времени - НЕ ДОЛЖНЫ показываться на индексной странице
        """
        future_question = create_question(question_text = "Будущий опрос", days = 30)
        response        = self.client.get(reverse('Kurochka_Polls:index'))
        self.assertContains(response, "Нет доступных опросов.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_future_question_and_past_question(self):
        """
        Если есть запросы и с прошедшем и с будущем временами публикации - проверяем, что отображается только прошедшие.
        """
        past_question   = create_question(question_text = "Прошедший опрос", days = -30)
        future_question = create_question(question_text = "Будущий опрос",   days = 30)
        response        = self.client.get(reverse('Kurochka_Polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [ past_question ])


    def test_two_past_questions(self):
        """
        Опросник должен быть способен отображать несколько опросов с прошедшим publish_date
        """
        past_question_1 = create_question(question_text = "Первый прошедший опрос", days = -30)
        past_question_2 = create_question(question_text = "Второй прошедший опрос", days = -15)
        response        = self.client.get(reverse('Kurochka_Polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [ past_question_2, past_question_1 ])


class QuestionDetailViewTests(TestCase):


    def test_future_question(self):
        """
        Вьюха с детальной инфой об опросе должна выдавать 404 на "будущие" опросы
        """
        future_question = create_question(question_text = "Будущий опрос", days = 5)
        url             = reverse('Kurochka_Polls:detail', args = (future_question.id, ))
        response        = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        """
        Вьюха с детальной инфой об опросе должна выдавать корректную инфу "прошедшего" опроса
        """
        past_question = create_question(question_text = "Прошедший опрос", days = -5)
        url           = reverse('Kurochka_Polls:detail', args = (past_question.id, ))
        response      = self.client.get(url)
        self.assertContains(response, past_question.question_text)



class QuestionResultsViewTests(TestCase):


    def test_future_question(self):
        """
        Вьюха с результатами опроса должна выдавать 404 на "будущие" опросы
        """
        future_question = create_question(question_text = "Будущий опрос", days = 5)
        url             = reverse('Kurochka_Polls:results', args = (future_question.id, ))
        response        = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        """
        Вьюха с результатами опроса должна выдавать корректную инфу "прошедшего" опроса
        """
        past_question = create_question(question_text = "Прошедший опрос", days = -5)
        url           = reverse('Kurochka_Polls:results', args = (past_question.id, ))
        response      = self.client.get(url)
        self.assertContains(response, past_question.question_text)