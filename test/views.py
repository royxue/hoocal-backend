from django.shortcuts import render_to_response


def show_html(request, template_name):
    return render_to_response(template_name)