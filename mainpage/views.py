from django.shortcuts import render_to_response

def mainpage(request):
    return render_to_response('mainpage.html')

