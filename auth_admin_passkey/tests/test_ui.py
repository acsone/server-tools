# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from urllib import urlencode
from lxml import html

from odoo.tests import common


@common.post_install(True)
class TestUI(common.HttpCase):

    def setUp(self):
        super(TestUI, self).setUp()
        self.url_open('/web/session/logout')
        with self.registry.cursor() as test_cursor:
            env = self.env(test_cursor)

            self.passkey_user = env['res.users'].create({
                'name': 'passkey',
                'login': 'passkey',
                'email': 'passkey',
                'password': 'passkey'
            })

    def html_doc(self, url='/web/login', data=None, timeout=10):
        """Get an HTML LXML document."""
        if data:
            data = bytes(urlencode(data))
        return html.fromstring(self.url_open(url, data, timeout).read())

    def csrf_token(self):
        """Get a valid CSRF token."""
        doc = self.html_doc()
        return doc.xpath("//input[@name='csrf_token']")[0].get("value")

    def test_01_normal_login_admin_succeed(self):
        # Our admin user wants to go to backoffice part of Odoo
        doc = self.url_open('/web/')

        # He notices that his redirected to login page as not authenticated
        self.assertIn('/web/login', doc.geturl())

        # He needs to enters his credentials and submit the form
        data = {
            'login': 'admin',
            'password': 'admin',
            'csrf_token': self.csrf_token()
        }
        self.html_doc(data=data)

        # He notices that his redirected to backoffice
        doc = self.url_open('/web/')
        self.assertNotIn('/web/login', doc.geturl())

    def test_02_normal_login_admin_fail(self):
        # Our admin user wants to go to backoffice part of Odoo
        doc = self.url_open('/web/')

        # He notices that he's redirected to login page as not authenticated
        self.assertIn('/web/login', doc.geturl())

        # He needs to enter his credentials and submit the form
        data = {
            'login': 'admin',
            'password': 'password',
            'csrf_token': self.csrf_token()
        }
        self.html_doc(data=data)

        # He mistyped his password so he's redirected to login page again
        doc = self.url_open('/web/')
        self.assertIn('/web/login', doc.geturl())

    def test_03_normal_login_passkey_succeed(self):
        # Our passkey user wants to go to backoffice part of Odoo
        doc = self.url_open('/web/')

        # He notices that he's redirected to login page as not authenticated
        self.assertIn('/web/login', doc.geturl())

        # He needs to enter his credentials and submit the form
        data = {
            'login': self.passkey_user.login,
            'password': self.passkey_user.login,
            'csrf_token': self.csrf_token()
        }
        self.html_doc(data=data)

        # He notices that his redirected to backoffice
        doc = self.url_open('/web/')
        self.assertNotIn('/web/login', doc.geturl())

    def test_04_normal_login_passkey_fail(self):
        # Our passkey user wants to go to backoffice part of Odoo
        doc = self.url_open('/web/')

        # He notices that he's redirected to login page as not authenticated
        self.assertIn('/web/login', doc.geturl())

        # He needs to enter his credentials and submit the form
        data = {
            'login': self.passkey_user.login,
            'password': 'password',
            'csrf_token': self.csrf_token()
        }
        self.html_doc('/web/login', data=data)

        # He mistyped his password so he's redirected to login page again
        doc = self.url_open('/web/')
        self.assertIn('/web/login', doc.geturl())

    def test_05_passkey_login_with_admin_password_succeed(self):
        # Our admin user wants to login as passkey user
        doc = self.url_open('/web/')

        # He notices that his redirected to login page as not authenticated
        self.assertIn('/web/login', doc.geturl())

        # He needs to enters its password with passkey user's login
        data = {
            'login': self.passkey_user.login,
            'password': 'admin',
            'csrf_token': self.csrf_token()
        }
        self.html_doc('/web/login', data=data)

        # He notices that his redirected to backoffice
        doc = self.url_open('/web/')
        self.assertNotIn('/web/login', doc.geturl())

    def test_06_passkey_login_with_same_password_as_admin(self):
        self.passkey_user.password = 'admin'

        # Our passkey user wants to go to backoffice part of Odoo
        doc = self.url_open('/web/')

        # He notices that his redirected to login page as not authenticated
        self.assertIn('/web/login', doc.geturl())

        # He needs to enters his credentials and submit the form
        data = {
            'login': self.passkey_user.login,
            'password': 'admin',
            'csrf_token': self.csrf_token()
        }
        self.html_doc('/web/login', data=data)

        # He notices that his redirected to backoffice
        doc = self.url_open('/web/')
        self.assertNotIn('/web/login', doc.geturl())
