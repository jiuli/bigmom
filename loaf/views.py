from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls.base import reverse
from django.views import generic

from loaf.models import Question, Choice


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'loaf/index.html'
    context_object_name = 'question_list'
    
    def get_queryset(self):
        return Question.objects.order_by('-publish_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'loaf/detail.html'

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'loaf/results.html'
    
    
def index(request):
    question_list = Question.objects.order_by('-publish_date')[:5]
    output = ','.join([q.question_text for q in question_list])
    
    template = loader.get_template('loaf/index.html') #找到页面
    context = {'question_list': question_list} #输出数据
    
    return HttpResponse(template.render(context, request))
    # return render(request, 'polls/index.html', context) #这样写更�?�?
    
def detail(request, question_id):
    '''
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("问题不存在")
    '''
    ''' 下面一句替代上面所有 '''
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'loaf/detail.html', {'question':question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    return render(request, 'loaf/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'loaf/detail.html', {'question': question,
                                                    'error_message':'您没有�?�择�?'})
    else:
        selected_choice.votes += 1
        selected_choice.save()
    ''' 成功提交，必须跳转是一个好的web发实
                        跳转到详情页，防止重复提交
                        使用reverse()避免 hardcode a url
    '''
    return HttpResponseRedirect(reverse('loaf:results', args=(question_id,)))
