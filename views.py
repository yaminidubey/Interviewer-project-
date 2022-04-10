from flask import Blueprint,request,redirect,render_template,jsonify,session
from flask.ext.admin.contrib.mongoengine import ModelView, filters
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.classy import FlaskView, route

from mongoengine import Q
from collections import defaultdict
import datetime
import requests
import hashlib
import json
import time
import sys

from mordor import models

main = Blueprint('main', __name__)

class AppView(FlaskView):
    @route('/register/', methods=['POST'])
    def post(self):
        from mordor import tasks

        try:
            user = models.User.objects.get(email = request.json['email'])
        except models.User.DoesNotExist:
            user = models.User()
            user.email = request.json['email']
        finally:
            user.name = request.json['name']
            user.mobile = request.json['mobile']
            user.URL = request.json['URL']
        

        try:
            try:
                if session['registerCount'] > 10:
                    raise Exception("Attempts exceeded")
                
                session['registerCount'] += 1
            except KeyError:
                session['registerCount'] = 1

            user.save()

            tasks.sendRegisterMail.delay(request.json['email'])

            return jsonify({"status": "Registration Successful", "summary": "Check your email for further instructions."})
        except:
            e = str(sys.exc_info()[1])
            return jsonify({"status": "Registration failed", "summary": "An error occurred. Try again. " + e})


class ProgressView(FlaskView):
    def index(self,userHash):
        try:
            user = models.User.objects.get(id = userHash)
            problems = models.Problem.objects(active = 'Yes')

            return render_template("progress.html", user = user, problems = problems)
        except:
            return 'You haven\'t registered yet.'


    @route('/testProblem/', methods=['POST'])
    def post(self):
        try:
            correctCount = 0
            result = {}

            user = models.User.objects.get(id = request.json['userHash'])
            problem = models.Problem.objects.get(id = request.json['problemHash'])

            url = user.URL + '/' + problem.URL
            data = problem.cases
            output = json.loads(problem.output)
            numberOfTestCases = len(output)

            response = requests.post(url, data = data, headers = {"content-type":"application/json"}, timeout = 4)
            userOutput = json.loads(response)

            for row,cases in enumerate(output):
                verified = True
                for column,value in enumerate(cases):
                    if not(str(userOutput[row][column]) == str(output[row][column])):
                        verified = False
                if verified:
                    correctCount += 1

            if correctCount == numberOfTestCases:
                user.result[problem.name] = True
                result['verified'] = True
            else:
                user.result[problem.name] = False
                result['verified'] = False

            result['casesVerified'] = correctCount
            result['totalCases'] = numberOfTestCases

            if result['verified']:
                user.shortlisted = 'Yes'
                problems = models.Problem.objects(active = 'Yes')
                 
                for index,problem in enumerate(problems):
                    try:
                        if user.result[problem.name] == False:
                            user.shortlisted = 'No'
                    except:
                            user.shortlisted = 'No'
            else:
                user.shortlisted = 'No'

            return jsonify(result)
        except:
            user.shortlisted = 'No'
            return jsonify({'verified' : 'invalid'})
        finally:
            user.attempts = user.attempts + 1
            user.save()


AppView.register(main)
ProgressView.register(main)