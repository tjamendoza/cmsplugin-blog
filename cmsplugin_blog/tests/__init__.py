import datetime
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from cmsplugin_blog.models import Entry
from cmsplugin_blog.test.testcases import BaseBlogTestCase

class BlogTestCase(BaseBlogTestCase):
    
    def test_01_apphook_added(self):
        self.assertEquals(reverse('en:blog_archive_index'), '/en/test-page-1/')
        self.assertEquals(reverse('de:blog_archive_index'), '/de/test-page-1/')
        
    def test_02_title_absolute_url(self):
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        self.assertEquals(title.get_absolute_url(), '/en/test-page-1/%s/entry-title/' % published_at.strftime('%Y/%m/%d'))
        
    def test_03_admin_add(self):
        
        superuser = User(username="super", is_staff=True, is_active=True, 
            is_superuser=True)
        superuser.set_password("super")
        superuser.save()
        
        self.client.login(username='super', password='super')
        
        add_url = reverse('admin:cmsplugin_blog_entry_add')
        
        # edit english
        response = self.client.get(add_url, {'language': 'en'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'value="English" type="button" disabled' )
        
        # edit german
        response = self.client.get(add_url, {'language': 'de'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'value="German" type="button" disabled')
        
    def test_04_admin_change(self):
        
        superuser = User(username="super", is_staff=True, is_active=True, 
            is_superuser=True)
        superuser.set_password("super")
        superuser.save()
        
        self.client.login(username='super', password='super')
        
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de')
        
        edit_url = reverse('admin:cmsplugin_blog_entry_change', args=(str(entry.pk)))
        
        # edit english
        response = self.client.get(edit_url, {'language': 'en'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'value="English" type="button" disabled' )

        
        # edit german
        response = self.client.get(edit_url, {'language': 'de'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'value="German" type="button" disabled' )

    def test_05_admin_add_post(self):
        
        superuser = User(username="super", is_staff=True, is_active=True, 
            is_superuser=True)
        superuser.set_password("super")
        superuser.save()
        
        self.client.login(username='super', password='super')
        
        add_url = reverse('admin:cmsplugin_blog_entry_add')
        
        # add english
        response = self.client.post(add_url, {'language': 'en', 'title': 'english', 'slug': 'english',
            'pub_date_0': '2011-01-16', 'pub_date_1': '09:09:09'})
        # self.assertEquals(response.content, '')

        self.assertEquals(response.status_code, 302)
        
        edit_url = reverse('admin:cmsplugin_blog_entry_change', args=(1,))

        # add german
        response = self.client.post(edit_url, {'language': 'de', 'title': 'german', 'slug': 'german',
            'pub_date_0': '2011-01-16', 'pub_date_1': '09:09:09'})
        self.assertEquals(response.status_code, 302)
        
        entry = Entry.objects.get(pk=1)
        self.assertEquals([title.title for title in entry.entrytitle_set.all()], ['english', 'german'])
        
        
class BlogRSSTestCase(BaseBlogTestCase):
    
    def test_01_posts_one_language(self):
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        response = self.client.get(reverse('en:blog_rss'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'in English')
        
    def test_02_posts_all_languages(self):
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        response = self.client.get(reverse('en:blog_rss_any'))
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'in English')
        
    def test_03_posts_by_author_single_language(self):
        user = User.objects.all()[0]
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        response = self.client.get(reverse('en:blog_rss_author', kwargs={'author': user.username}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'in English')  
        
    def test_04_posts_by_author_all_languages(self):
        user = User.objects.all()[0]
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        response = self.client.get(reverse('en:blog_rss_any_author', kwargs={'author': user.username}))
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'in English')
        
class ViewsTestCase(BaseBlogTestCase):
    
    def test_01_generics(self):
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-24)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        response = self.client.get(reverse('en:blog_archive_index'))
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('en:blog_archive_year', kwargs={'year': published_at.strftime('%Y')}))
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('en:blog_archive_month',
            kwargs={
                'year': published_at.strftime('%Y'),
                'month': published_at.strftime('%m')
            }))
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('en:blog_archive_day',
            kwargs={
                'year': published_at.strftime('%Y'),
                'month': published_at.strftime('%m'),
                'day': published_at.strftime('%d')
            }))
        self.assertEquals(response.status_code, 200)
        '''
        response = self.client.get(reverse('en:blog_detail',
            kwargs={
                'year': published_at.strftime('%Y'),
                'month': published_at.strftime('%m'),
                'day': published_at.strftime('%d'),
                'slug': title.slug
            }))
        self.assertEquals(response.status_code, 200)
        '''
             
class SitemapsTestCase(BaseBlogTestCase):
    
    def test_01_sitemaps(self):
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        response = self.client.get('/sitemap.xml')
        self.assertEquals(response.status_code, 200)