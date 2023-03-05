from django.shortcuts import render, get_object_or_404
from django.http      import HttpResponse, HttpResponseRedirect, Http404
from django.urls      import reverse
from django.views     import generic
from django.utils     import timezone
from django.db.models import F


from .models          import Question, Choice


class IndexView(generic.ListView):
    template_name       = 'Kurochka_Polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Возвращает последние пять опубликованных опросов (Исключая те, что установлены к публикации в будущем)
        """
        return Question.objects.filter(publish_date__lte = timezone.now()).order_by('-publish_date')[:5]


class DetailView(generic.DetailView):
    model         = Question
    template_name = "Kurochka_Polls/detail.html"

    def get_queryset(self):
        """
        Исключаем опросы, которые ещё не были опубликованы
        :return:
        """
        return Question.objects.filter(publish_date__lte = timezone.now())


class ResultsView(generic.DetailView):
    model         = Question
    template_name = "Kurochka_Polls/results.html"

    def get_queryset(self):
        """
        Исключаем опросы, которые ещё не были опубликованы
        :return:
        """
        return Question.objects.filter(publish_date__lte = timezone.now())


def vote(request, question_id):
    question = get_object_or_404(Question, pk = question_id)

    try:
        selected_choice = question.choice_set.get(pk = request.POST['choice'])

    except (KeyError, Choice.DoesNotExist):
        return render(request, 'Kurochka_Polls/detail.html', { 'question'      : question,
                                                               'error_message' : "Вы не выбрали ни одного варианта!" })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('Kurochka_Polls:results', args = (question.id, ) ))



# def index(request):
#     latest_question_list = Question.objects.order_by('-publish_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'Kurochka_Polls/index.html', context)
#
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk = question_id)
#     return render(request, 'Kurochka_Polls/detail.html', {'question': question})
#
# def results(request, question_id):
#     question = get_object_or_404(Question, pk = question_id)
#     return render(request, 'Kurochka_Polls/results.html', {'question': question})
#
# def vote(request, question_id):
#     question = get_object_or_404(Question, pk = question_id)
#
#     try:
#         selected_choice = question.choice_set.get(pk = request.POST['choice'])
#
#     except (KeyError, Choice.DoesNotExist):
#         render(request, 'Kurochka_Polls/index.html', {'question'     : question,
#                                                       'error_message': "Вы не выбрали ни одного варианта"})
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         return HttpResponseRedirect(reverse('Kurochka_Polls:results', args = (question.id,)))
pass