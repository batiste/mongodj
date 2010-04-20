"""
Test suite for mangodj.
"""

from django.test import TestCase
from testproj.myapp.models import Entry, Blog
import datetime

class SimpleTest(TestCase):
    
    def test_add_and_delete_blog(self):
        blog1 = Blog(title="blog1")
        blog1.save()
        self.assertEqual(Blog.objects.count(), 1)
        blog2 = Blog(title="blog2")
        self.assertEqual(blog2.pk, None)
        blog2.save()
        self.assertNotEqual(blog2.pk, None)
        self.assertEqual(Blog.objects.count(), 2)
        blog2.delete()
        self.assertEqual(Blog.objects.count(), 1)
        blog1.delete()
        self.assertEqual(Blog.objects.count(), 0)

    def test_simple_get(self):
        blog1 = Blog(title="blog1")
        blog1.save()
        blog2 = Blog(title="blog2")
        blog2.save()
        self.assertEqual(Blog.objects.count(), 2)
        self.assertEqual(
            Blog.objects.get(title="blog2"),
            blog2
        )
        self.assertEqual(
            Blog.objects.get(title="blog1"),
            blog1
        )

    def test_simple_filter(self):
        blog1 = Blog(title="same title")
        blog1.save()
        blog2 = Blog(title="same title")
        blog2.save()
        blog3 = Blog(title="another title")
        blog3.save()
        self.assertEqual(Blog.objects.count(), 3)
        self.assertEqual(Blog.objects.get(pk=blog1.pk), blog1)
        self.assertEqual(
            Blog.objects.filter(title="same title").count(),
            2
        )
        self.assertEqual(
            Blog.objects.filter(title="same title", pk=blog1.pk).count(),
            1
        )

    def test_change_model(self):
        blog1 = Blog(title="blog 1")
        blog1.save()
        self.assertEqual(Blog.objects.count(), 1)
        blog1.title = "new title"
        blog1.save()
        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(blog1.title, Blog.objects.all()[0].title)

    def test_dates_ordering(self):
        now = datetime.datetime.now()
        before = now - datetime.timedelta(days=1)
        
        entry1 = Entry(title="entry 1", date_published=now)
        entry1.save()

        entry2 = Entry(title="entry 2", date_published=before)
        entry2.save()
    
        self.assertEqual(
            list(Entry.objects.order_by('-date_published')),
            [entry1, entry2]
        )

        self.assertEqual(
            list(Entry.objects.order_by('date_published')),
            [entry2, entry1]
        )


    def test_dates_less_and_more_than(self):
        now = datetime.datetime.now()
        before = now + datetime.timedelta(days=1)
        after = now - datetime.timedelta(days=1)
        
        entry1 = Entry(title="entry 1", date_published=now)
        entry1.save()

        entry2 = Entry(title="entry 2", date_published=before)
        entry2.save()

        entry3 = Entry(title="entry 3", date_published=after)
        entry3.save()

        self.assertEqual(
            list(Entry.objects.filter(date_published=now)),
            [entry1]
        )
        self.assertEqual(
            list(Entry.objects.filter(date_published__lt=now)),
            [entry3]
        )
        self.assertEqual(
            list(Entry.objects.filter(date_published__gt=now)),
            [entry2]
        )

    def test_simple_foreign_keys(self):
        now = datetime.datetime.now()

        blog1 = Blog(title="Blog")
        blog1.save()
        entry1 = Entry(title="entry 1", blog=blog1)
        entry1.save()
        entry2 = Entry(title="entry 2", blog=blog1)
        entry2.save()
        self.assertEqual(Entry.objects.count(), 2)

        for entry in Entry.objects.all():
            self.assertEqual(
                blog1,
                entry.blog
            )
