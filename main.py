#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import jinja2
import time
from google.appengine.api import users
from google.appengine.ext import ndb


# ---- These are all the global variables used in this file. ----
# env has all the files in the directory 'html'
env = jinja2.Environment(loader=jinja2.FileSystemLoader('html'))
# login_url is the url made for logging into a Google account
login_url = ""
# logout_url is the url made for logging out of the application
logout_url = ""

# ---- This code sets up the components of the application.----
# Each user of the application is a Writer
class Writer(ndb.Model):
    name = ndb.StringProperty()

# Each journal Entry has a title, date, content, and whether or not it's a favorite.
class Entry(ndb.Model):
    title = ndb.StringProperty()
    date = ndb.DateProperty()
    content = ndb.StringProperty()
    favorite = ndb.BooleanProperty()
    # This entry belongs to this user/writer.
    writer_key = ndb.KeyProperty(Writer)


# ---- This code renders the html files and sets up the handlers. ----
# Renders the home page
class Home(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('home.html')
        self.response.write(template.render())

# Renders the login page
class Login(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # If the user is logged into Google
        if user:
            # Take them to the dashboard.
            writer = Writer.get_by_id(user.user_id())
            # When the user signs out, take them to the home page.
            logout_url = '<a href="%s"> sign out </a>' % users.create_logout_url('/')
            writer = Writer.get_by_id(user.user_id())
            if writer:
                self.redirect('/dashboard')
            else:
                self.redirect('/registration')
        else:
            # After the user logins, take them to the dashboard.
            login_url = '<a href="%s"> sign in </a>' % users.create_login_url('/dashboard')
            template = env.get_template('login.html')
            self.response.write(template.render())
            self.response.write(login_url)

class Registration(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('registration.html')
        self.response.write(template.render())

# Renders the dashboard page
class Dashboard(webapp2.RequestHandler):
    def get(self):
        # Who is the current writer?
        user = users.get_current_user()
        writer = Writer.get_by_id(user.user_id())

        # Find all the Entries that belong to the current writer.
        all_entries = Entry.query(Entry.writer_key == writer.key)
        # Limit to the first 9 recent entries!!!! (fetch_page be able to show more)
        first_nine_entries = all_entries.order(-Entry.date).fetch(9)

        # Render the dashboard template
        template = env.get_template('dashboard.html')
        # Template variables to use and display in dashboard.html
        entries = {"display_entries" : first_nine_entries}
        self.response.write(template.render(entries))
        self.response.write(logout_url)

    # This method is called from the registration page.
    # Need to be in dashboard because this is where the user will
    # be taken after they register.
    def post(self):
        user = users.get_current_user()
        if not user:
            # You shouldn't be able to get here without being logged in
            self.error(500)
            return
        writer = Writer(
            name= self.request.get('name'),
            id=user.user_id()
            )
        writer.put()
        self.get()

# # Renders the favorites page
class Favorites(webapp2.RequestHandler):
    def get(self):
        # Who is the current writer?
        user = users.get_current_user()
        writer = Writer.get_by_id(user.user_id())

        # Find all the Entries that belong to the current writer.
        favorite_entries = Entry.query(Entry.writer_key == writer.key, Entry.favorite == True)
        # Limit to the first 20 recent entries!!!! (fetch_page be able to show more)
        first_nine_entries = all_entries.order(-Entry.date).fetch(20)
        template = env.get_template('favorites.html')
        self.response.write(template.render())

class NewEntry(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('new_entry.html')
        self.response.write(template.render())
    def post(self):
        self.redirect('/dashboard')
#
# class DisplayEntry(webapp2.RequestHandler):

# Renders the monthly collections page
class Collections(webapp2.RequestHandler):
    def get(self):
        template = env.get_template('collections.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/login', Login),
    ('/registration', Registration),
    ('/dashboard', Dashboard),
    ('/collections', Collections),
    ('/favorites', Favorites),
    ('/new_entry', NewEntry)
    # ('/entry', DisplayEntry) # how to make these entry urls unique?
], debug=True)
