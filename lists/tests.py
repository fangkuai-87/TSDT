from django.test import TestCase
from django.urls import resolve
from lists.views import home_page #(1)

class  HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/') #(2)
        self.assertEqual(found.func, home_page) #3
# Create your tests here.
