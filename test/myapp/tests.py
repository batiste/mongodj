"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from mongodj.test.myapp.models import Entry, Blog

class SimpleTest(TestCase):
    
    def test_add_blog(self):
        blog1 = Blog(title="blog1")
        blog1.save()
        self.assertEqual(Blog.objects.count(), 1)
        blog2 = Blog(title="blog2")
        blog2.save()
        self.assertEqual(Blog.objects.count(), 2)
        blog2.delete()
        self.assertEqual(Blog.objects.count(), 1)