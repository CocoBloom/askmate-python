import connection
import os
import bcrypt

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


@connection.connection_handler
def get_new_user_id(cursor):
    query = """SELECT MAX(id) FROM users;"""
    cursor.execute(query)
    new_id = cursor.fetchall()[0]['max'] + 1
    return new_id


@connection.connection_handler
def get_new_registration_id(cursor):
    query = """SELECT MAX(id) FROM registration;"""
    cursor.execute(query)
    new_id = cursor.fetchall()[0]['max'] + 1
    return new_id


def hash_password(password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes_password)
