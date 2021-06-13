import db as db
import json
from bottle import response, request
from mcOption import MCOption
from rubric import Rubric


class Question:
    def __init__(self, id, type, question_text, points, setup=None):
        '''Constructor'''
        self.id = id
        self.type = type
        self.question_text = question_text
        self.points = points
        self.setup = setup

    def jsonable(self):
        '''Returns a dict appropriate for creating JSON representation
          of the instance'''

        id = self.id
        type = self.type
        question_text = self.question_text
        points = self.points
        setup = self.setup

        # add if statements for each types
        if (type == "mc"):

            true_options = Question.getTrueMCOption(id)
            false_options = Question.getFalseMCOption(id)

            return {
                'id': id,
                'type': type,
                'question_text': question_text,
                'points': points,
                'setup': setup,
                'true_options': true_options,
                'false_options': false_options
            }

        if (type == "sql"):

            answer = Question.getAnswer(id)

            return {
                'id': id,
                'type': type,
                'question_text': question_text,
                'points': points,
                'setup': setup,
                'answer': answer
            }

        if (type == "sa"):

            rubrics = Question.getRubrics(id)
            answer = Question.getAnswer(id)

            return {
                'id': id,
                'type': type,
                'question_text': question_text,
                'points': points,
                'setup': setup,
                'answer': answer,
                'rubrics': rubrics
            }

        return {
            'id': id,
            'type': type,
            'question_text': question_text,
            'points': points,
            'setup': setup
        }

    def update(self):
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Question SET type = ?, question_text = ?, points = ?, setup = ? WHERE id = ?",
                           (self.type, self.question_text, self.points, self.setup, self.id))
            conn.commit()

        return Question.find(self.id)

    def updateFromJSON(self, question_data):

        if (self.type != question_data['type']):
            response.status = 400
            raise Exception('Wrong Type :((')

        self.type = question_data['type']
        self.question_text = question_data['question_text']
        self.points = question_data['points']
        self.setup = question_data['setup']

        if (self.type == "sa" or self.type == "sql"):

            answer = question_data['answer']

            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Answer SET answer_text = ? WHERE qid = ?", (answer, self.id))

        self.update()

    def delete(self):

        id = self.id
        type = self.type

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Question WHERE id = ?", (self.id, ))

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM MCOption WHERE qid = ?", (self.id, ))

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Answer WHERE qid = ?", (self.id, ))

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Rubric WHERE qid = ?", (self.id, ))

    @staticmethod
    def createFromJSON(question_data):

        type = question_data["type"]
        question_text = question_data["question_text"]
        points = question_data['points']
        setup = question_data["setup"]

        if (type == "sql" and setup == None):
            response.status = 400
            raise Exception('SQL requires setup')

        if (question_text.isspace() or len(question_text) == 0):
            response.status = 400
            raise Exception('Question text must be filled')

        if (points <= 0):
            response.status = 400
            raise Exception('Points > 0')

        # For SA
        if (type == "sa"):

            if (not "answer" in question_data):
                response.status = 400
                raise Exception('SQL requires setup')

            answer = question_data["answer"]

            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Question (type, question_text, points, setup) VALUES (?, ?, ?, ?)",
                    (type, question_text[0:40], points, setup))
                conn.commit()

            qid = cursor.lastrowid

            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Answer (answer_text, qid) VALUES (?, ?)",
                    (answer, qid))
                conn.commit()

            return Question.find(qid)
        # SA End

        # For SQL
        if (type == "sql"):

            answer = question_data["answer"]

            # create the question
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Question (type, question_text, points, setup) VALUES (?, ?, ?, ?)",
                    (type, question_text, points, setup))
                conn.commit()

            # create the answer
            qid = cursor.lastrowid
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Answer (answer_text, qid) VALUES (?, ?)",
                    (answer, qid))
                conn.commit()

            # return JSON
            return Question.find(qid)

        # SQL End
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Question (type, question_text, points, setup) VALUES (?, ?, ?, ?)",
                (type, question_text, points, setup))
            conn.commit()

        return Question.find(cursor.lastrowid)

    @staticmethod
    def find(qid):

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question WHERE id = ?", (qid,))
            row = cursor.fetchone()

        if row is None:
            raise Exception(f'No such Question with pid: {qid}')

        else:

            qid = row['id']
            type = row['type']
            question_text = row['question_text']
            points = row['points']
            setup = row['setup']

            return Question(qid, type, question_text, points, setup)

    @staticmethod
    def getFalseMCOption(qid):
        '''Returns array of all MC Options that are false from the database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM MCOption Where qid = ? AND is_true = ?", (qid, 0))
            # allFalseMCOptions = [MCOption.find(item['id'])
            allFalseMCOptions = [{"id": item['id'], "is_true": False, "option_text": item['option_text'], "qid": item['qid']}
                                 for item in cursor]

        return allFalseMCOptions

    @staticmethod
    def getTrueMCOption(qid):
        '''Returns array of all MC Options that are false from the database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM MCOption Where qid = ? AND is_true = ?", (qid, 1))
            # allTrueMCOptions = [MCOption.find(item['id'])
            allTrueMCOptions = [{"id": item['id'], "is_true": True, "option_text": item['option_text'], "qid": item['qid']}
                                for item in cursor]

        return allTrueMCOptions

    @staticmethod
    def getAnswer(qid):
        '''Returns array of all MC Options that are false from the database'''
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Answer Where qid = ?", (qid,))
            row = cursor.fetchone()

        if row is None:
            return None
        else:
            return row['answer_text']

    @staticmethod
    def getRubrics(qid):
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Rubric Where qid = ?", (qid,))
            # allRubrics = [Rubric.find(item['id'])
            allRubrics = [{"id": item['id'], "rubric_text": item['rubric_text'], 'points': item['points'], 'qid': item['qid']}
                          for item in cursor]

        return allRubrics

    @staticmethod
    def getQD():

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question Where type = \"mc\"")
            all_MCs = [{"id": item['id'], "question_start": item['question_text'][:40]}
                       for item in cursor]

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question Where type = \"sa\"")
            all_SAs = [{"id": item['id'], "question_start": item['question_text'][:40]}
                       for item in cursor]

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Question Where type = \"sql\"")
            all_SQLs = [{"id": item['id'], "question_start": item['question_text'][:40]}
                        for item in cursor]

        result = {"mc": all_MCs, "sa": all_SAs, "sql": all_SQLs}

        return result


# routes

    # def setupBottleRoutes(app):
    #     @app.get('/question')
    #     def getQuestion():
    #         mc = Question.getMC()
    #         sa = Question.getSA()
    #         sql = Question.getSQL()

    #         # Bottle won't automatically do the right thing for returning an array
    #         # of items as a JSON object so we have to do it ourselves.
    #         # First, set up the response content type
    #         response.content_type = 'application/json'

    #         # Then, use the JSON module to create the JSON representation of the array
    #         return [mc, sa, sql]
