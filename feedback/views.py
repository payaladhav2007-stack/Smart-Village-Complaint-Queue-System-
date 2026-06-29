from django.shortcuts import render

def feedback_form(request):
    return render(request, 'feedback/feedback_form.html')
