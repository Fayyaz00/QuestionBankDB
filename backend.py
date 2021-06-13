from bottle import Bottle, run, response, request
import json
import db
from mcOption import MCOption
from rubric import Rubric
from setup import Setup
from question import Question

app = Bottle()

MCOption.setupBottleRoutes(app)
Rubric.setupBottleRoutes(app)
Setup.setupBottleRoutes(app)

# implement last
# Question.setupBottleRoutes(app)

# Start the backend


@app.get('/question')
def getQuestion():

    result = Question.getQD()

    # Bottle won't automatically do the right thing for returning an array
    # of items as a JSON object so we have to do it ourselves.
    # First, set up the response content type
    response.content_type = 'application/json'

    # Then, use the JSON module to create the JSON representation of the array
    # return [mc, sa, sql]
    return json.dumps(result)


@app.get('/catz')
def getCatz():

    return "catz"


@app.get('/question/<qid>')
def getQuestionInstance(qid):
    try:
        question = Question.find(qid)
    except Exception:
        response.status = 404
        return "Project not found"

    qid = question.id
    type = question.type
    question_text = question.question_text
    points = question.points
    setup = question.setup

    if (type == "sql" and setup == None):
        response.status = 400
        return "SQL requires a setup"

    return question.jsonable()


@app.post('/question')
def postQuestion():

    try:
        question = Question.createFromJSON(request.json)
    except Exception:
        return "Wrong Format"

    return question.jsonable()


@app.put('/question/<qid>')
def updateQuestionInstance(qid):

    try:
        question = Question.find(qid)

    except Exception:
        response.status = 404
        return "Question not found"

    try:
        question.updateFromJSON(request.json)
    except Exception:
        response.status = 400
        return "Wrong type :(("

    return question.jsonable()


@app.delete('/question/<qid>')
def deleteQuestionInstance(qid):

    try:
        question = Question.find(qid)
    except Exception:
        response.status = 404
        return "Question to delete does not exist"

    question.delete()

    response.content_type = 'application/json'
    return json.dumps(True)


run(app, host='localhost', port=8080, debug=True)
