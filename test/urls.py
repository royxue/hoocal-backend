from django.conf.urls import patterns,url


urlpatterns = patterns('test.views',
    url(r'(?P<template_name>\w+.html)$', 'show_html')
)