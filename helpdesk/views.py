from django.shortcuts import render, redirect
from . import forms
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import models
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import requests
from django.http import JsonResponse
from django.db.models import F

import re

def gemini_response(request, help_id):
    help_obj = get_object_or_404(models.Help, id=help_id)

    prompt_text = f"""
You are an AI support assistant.

Message: "{help_obj.help}"

Return the following:
1. Urgency score between 1 and 10.
2. Category number:
   (5) Technical problem
   (4) Warranty related
   (3) Return related
   (2) Offer related
   (1) Product inquiry
   (0) Other
3. A helpful response for the customer.

Reply like this:

Urgency: <number>
Category: <number>
Reply: <helpful response here>
"""

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyAPYlnVU3g3xwyUKI3XaVXj3h9gqLfAxvA'
    headers = {'Content-Type': 'application/json'}
    data = {
        'contents': [{
            'parts': [{'text': prompt_text}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            print("Full Gemini reply:\n", text)

            # Extract values using regex
            urgency_match = re.search(r'Urgency:\s*(\d+)', text)
            category_match = re.search(r'Category:\s*(\d+)', text)
            reply_match = re.search(r'Reply:\s*(.*)', text, re.DOTALL)

            urgency = int(urgency_match.group(1)) if urgency_match else None
            category = int(category_match.group(1)) if category_match else None
            reply = reply_match.group(1).strip() if reply_match else "We'll get back to you shortly."

            help_obj.urgency_score = urgency
            help_obj.help_type = category
            help_obj.save()

            final_reply = "TRY THIS TILL WE CONTACT YOU !\n" + reply
            return final_reply

        except Exception as e:
            print("Failed to extract structured data:", str(e))
            return 'we will reach you soon'
    else:
        print("Gemini API request failed:", response.status_code)
        return 'we will reach you soon'




def send_the_email(request, help_id):
    help_obj = get_object_or_404(models.Help, id=help_id)
    gem = gemini_response(request, help_id)
    send_mail(
        subject = help_obj.help,
        message = gem,
        from_email='zetanotesbusiness@gmail.com',
        recipient_list=[request.user.email],
        fail_silently=False,
    )



@login_required
def help_view(request):
    if request.method == 'POST':
        form = forms.HelpForm(request.POST, request.FILES)
        if form.is_valid():
            help_obj = form.save(commit=False)
            help_obj.user = request.user
            help_obj.save()
            send_the_email(request, help_obj.id)
            messages.success(request, "check email and try most common isssues !. Our custome care will contact you soon ! ")
            return redirect('dashboard')
            
    else:
        form = forms.HelpForm()
    return render(request, 'helpdesk/help_form.html', {"form" : form})

@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = forms.FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            help_obj = form.save(commit=False)
            help_obj.user = request.user
            help_obj.save()
            messages.success(request, "form submitted sussifully !")
            return redirect('dashboard')
    else:
        form = forms.FeedbackForm()
    return render(request, 'helpdesk/feedback_form.html', {"form" : form})
        
@login_required
def dashboard_view(request):
    user = request.user
    return render(request, 'helpdesk/dashboard.html', {'user' : user})


def show_user_feedback(request):
    feedbacks = models.Feedback.objects.all()
    return render(request, 'helpdesk/user_feedbacks.html', {'feedbacks' : feedbacks})

@login_required
def show_user_help(request):
    user = request.user
    help = models.Help.objects.filter(user=user)
    return render(request, 'helpdesk/user_helps.html', {'helps' : help})


@login_required
def show_help_details(request, helpid):
    help_obj = get_object_or_404(models.Help, id=helpid)
    return render(request, 'helpdesk/show_help_details.html', {'help' : help_obj})


def show_feedback_details(request, feedbackid):
    feedback_obj = get_object_or_404(models.Feedback, id=feedbackid)
    return render(request, 'helpdesk/show_feedback_details.html', {'feedback' : feedback_obj})

@login_required
def delete_help(request, id):
    obj = get_object_or_404(models.Help, id=id, user=request.user)
    obj.delete()
    messages.success(request, 'deletion successfull !')
    return redirect('show_help')


@login_required
def delete_feedback(request, id):
    obj = get_object_or_404(models.Feedback, id=id, user=request.user)
    obj.delete()
    messages.success(request, 'deletion successfull !')
    return redirect('show_feedback')


@login_required
def edit_feedback(request, id):
    obj = get_object_or_404(models.Feedback, id=id, user=request.user)
    if request.method == 'POST':
        form = forms.FeedbackForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'form edited successfully !')
            return redirect('show_feedback_details', id)
    else:
        form = forms.FeedbackForm(instance=obj)
    return render(request, 'helpdesk/feedback_form.html', {'form' : form})


@login_required
def edit_help(request, id):
    obj = get_object_or_404(models.Help, id=id, user=request.user)
    if request.method == 'POST':
        form = forms.HelpForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'form edited successfully !')
            return redirect('show_help_details', id)
    else:
        form = forms.HelpForm(instance=obj)
    return render(request, 'helpdesk/help_form.html', {'form' : form})


@login_required
def reply_view(request):
    user = request.user
    if user.can_reply:
        query = models.Help.objects.filter(reply='no-reply-yet').annotate(
            score = F('help_type') + F('urgency_score')
        ).order_by('-score')

        return render(request, 'helpdesk/company_reply.html', {'query' : query})
    else:
        messages.error(request, 'you have no authority to reply !')


@login_required
def reply(request, id):
    obj = get_object_or_404(models.Help, id=id)
    if request.method == 'POST':
        form = forms.ReplyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['reply']
            obj.reply = data
            obj.save()
            send_mail(
                subject = obj.help,
                message = data,
                from_email='zetanotesbusiness@gmail.com',
                recipient_list=[obj.user.email],
                fail_silently=False,
            )
            return redirect('to_reply')
    else:
        form = forms.ReplyForm()
    return render(request, 'helpdesk/reply.html', {'obj' : obj, 'form' : form})