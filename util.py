import connection
import os

@connection.connection_handler
def get_new_question_id(cursor):
    query = """SELECT MAX(id) from question;"""
    cursor.execute(query)
    new_id = cursor.fetchall()[0]['max'] + 1
    return new_id

@connection.connection_handler
def get_new_answer_id(cursor):
    query = """SELECT MAX(id) from answer;"""
    cursor.execute(query)
    new_id = cursor.fetchall()[0]['max'] + 1
    return new_id

@connection.connection_handler
def get_new_comment_id(cursor):
    query = """SELECT MAX(id) from comment;"""
    cursor.execute(query)
    new_id = cursor.fetchall()[0]['max'] + 1
    return new_id

def get_image_name(file):
    filename = file.filename
    if filename != '':
        filename = os.path.join('static/', filename)
        file.save(filename)
        image = filename
    else:
        image = ''
    return image

@connection.connection_handler
def get_new_tag_id(cursor):
    query = """SELECT MAX(id) from tag;"""
    cursor.execute(query)
    new_id = cursor.fetchall()[0]['max'] + 1
    return new_id