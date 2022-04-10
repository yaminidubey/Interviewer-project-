from mordor import db
import datetime

class User(db.Document):
	email = db.EmailField(required = True, unique = True)
	name = db.StringField(required = True, max_length = 50)
	mobile = db.StringField(required = True, min_length = 10, max_length = 10)
	URL = db.URLField(required = True)
	attempts = db.IntField(default = 0)
	result = db.DictField()
	shortlisted = db.StringField(choices = ['Yes','No'], default = 'No')

class Problem(db.Document):
	name = db.StringField(required = True, unique = True)
	URL = db.StringField(required = True, unique = True)
	cases = db.StringField()
	output = db.StringField()
	active = db.StringField(choices = ['Yes','No'], default = 'Yes')