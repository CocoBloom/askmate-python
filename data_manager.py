import connection
from psycopg2.extras import RealDictCursor
from datetime import datetime
import util


@connection.connection_handler
def get_main_list(cursor, count):
    cursor.execute("""SELECT * FROM question
                      ORDER BY submission_time DESC
                      LIMIT %(count)s;""",
                   {'count': count})
    main_list = cursor.fetchall()
    return main_list


@connection.connection_handler
def get_question_id(cursor: RealDictCursor, answer_id):
    print("anser:id",answer_id)
    query = """
        SELECT *
        FROM answer
        WHERE id=%(id)s;"""
    cursor.execute(query, {'id': answer_id})
    row = cursor.fetchone()
    return row


@connection.connection_handler
def get_id_from_comment(cursor: RealDictCursor, comment_id):
    query = """
        SELECT *
        FROM comment
        WHERE id=%(id)s;"""
    cursor.execute(query, {'id': comment_id})
    row = cursor.fetchone()
    return row


@connection.connection_handler
def delete_answer_by_id(cursor, answer_id):
    cursor.execute("""DELETE FROM comment
                          WHERE answer_id=%(id)s;""",
                   {'id': answer_id})
    cursor.execute("""DELETE FROM answer
                          WHERE id=%(id)s;""",
                   {'id': answer_id})


@connection.connection_handler
def get_display_list(cursor: RealDictCursor, mode='submission_time', direction='DESC') -> list:
    cursor.execute(f"""
    SELECT * 
    FROM question
    ORDER BY {mode} {direction}""")
    return cursor.fetchall()


@connection.connection_handler
def write_to_questions(cursor, dictionary):
    query = """INSERT INTO question VALUES (%(id_value)s, %(submission_time_value)s, %(view_number_value)s, 
                        %(vote_number_value)s, %(title_value)s, %(message_value)s, %(image_value)s);"""
    cursor.execute(query, {'id_value': dictionary['id'], 'submission_time_value': dictionary['submission_time'],
                           'view_number_value': dictionary['view_number'],
                           'vote_number_value': dictionary['vote_number'], 'title_value': dictionary['title'],
                           'message_value': dictionary['message'], 'image_value': dictionary['image']})


def create_new_question():
    new_question = {
        'id': util.get_new_question_id(),
        'submission_time': datetime.now().replace(microsecond=0),
        'view_number': 0,
        'vote_number': 0
    }
    return new_question


@connection.connection_handler
def get_display_question(cursor: RealDictCursor, question_id) -> list:
    cursor.execute(f"""
    SELECT *
    FROM question
    WHERE id = {question_id}
    """)
    return cursor.fetchone()


@connection.connection_handler
def get_display_answers(cursor, which_id, question_id) -> list:
    cursor.execute(f"""
    SELECT *
    FROM answer
    WHERE {which_id} = {question_id}
    ORDER BY submission_time
    """)
    return cursor.fetchall()


@connection.connection_handler
def get_display_comment(cursor, comment_id) -> list:
    cursor.execute(f"""
    SELECT *
    FROM comment
    WHERE id = {comment_id}
    """)
    return cursor.fetchone()


@connection.connection_handler
def delete_question(cursor: RealDictCursor, question_id):
    cursor.execute("""DELETE FROM comment
                         WHERE question_id=%(id)s;""",
                   {'id': question_id})
    cursor.execute("""DELETE FROM question_tag
                    WHERE question_id=%(id)s;""",
                   {'id': question_id})
    cursor.execute("""SELECT id FROM answer
                          WHERE question_id=%(id)s;""",
                   {'id': question_id})
    answer_ids = cursor.fetchall()
    for answer_id in answer_ids:
        delete_answer_by_id(answer_id['id'])
    cursor.execute("""DELETE FROM question WHERE id=%(id)s;""", {'id': question_id})


@connection.connection_handler
def update_question(cursor: RealDictCursor, id, new_title, new_message, image) -> list:
    cursor.execute("""
    UPDATE question
    SET title = %(new_title)s, message = %(new_message)s, image = %(image)s
    WHERE id = %(id)s;""",
                   {"new_title": new_title, "new_message": new_message, "image": image, "id": id})


@connection.connection_handler
def update_answer(cursor: RealDictCursor, id, new_message, image) -> list:
    cursor.execute("""
    UPDATE answer
    SET  message = %(new_message)s, image = %(image)s
    WHERE id = %(id)s;""",
                   {"new_message": new_message, "image": image, "id": id})


@connection.connection_handler
def update_comment(cursor: RealDictCursor, id, new_message) -> list:
    cursor.execute("""
    UPDATE comment
    SET  message = %(new_message)s, submission_time = %(sub_time)s,
    edited_count = CASE
        WHEN edited_count IS NULL THEN  1 
        ELSE edited_count+1
        END
    WHERE id = %(id)s;""",
                   {"new_message": new_message, "sub_time": datetime.now().replace(microsecond=0), "id": id})


@connection.connection_handler
def update_view_number(cursor, id) -> list:
    cursor.execute(f"""
    UPDATE question
    SET view_number = view_number+1
    WHERE id = {id};""")


@connection.connection_handler
def vote_up_question(cursor: RealDictCursor, id) -> list:
    cursor.execute(f"""
    UPDATE question
    SET vote_number = vote_number+1
    WHERE id = {id};
    """)


@connection.connection_handler
def vote_down_question(cursor: RealDictCursor, id) -> list:
    cursor.execute(f"""
    UPDATE question
    SET vote_number = vote_number-1
    WHERE id = {id};
    """)


@connection.connection_handler
def vote_up_answer(cursor: RealDictCursor, id) -> list:
    cursor.execute(f"""
    UPDATE answer
    SET vote_number = vote_number+1
    WHERE id = {id};
    """)


@connection.connection_handler
def vote_down_answer(cursor: RealDictCursor, id) -> list:
    cursor.execute(f"""
    UPDATE answer
    SET vote_number = vote_number-1
    WHERE id = {id};
    """)


@connection.connection_handler
def get_question_id_by_answer_id(cursor: RealDictCursor, answer_id) -> list:
    cursor.execute(f"""
    SELECT question_id
    FROM answer
    WHERE id = {answer_id}
    """)
    return cursor.fetchone()


@connection.connection_handler
def write_to_answers(cursor, dictionary):
    query = """INSERT INTO answer VALUES (%(id_value)s, %(submission_time_value)s, %(vote_number_value)s, 
                    %(question_id_value)s, %(message_value)s, %(image_value)s);"""
    cursor.execute(query, {'id_value': dictionary['id'], 'submission_time_value': dictionary['submission_time'],
                           'vote_number_value': dictionary['vote_number'],
                           'question_id_value': dictionary['question_id'], 'message_value': dictionary['message'],
                           'image_value': dictionary['image']})


def create_new_answer(answer, question_id, image):
    new_answer = {
        "id": util.get_new_answer_id(),
        "submission_time": datetime.now().replace(microsecond=0),
        "vote_number": 0,
        "question_id": question_id,
        "message": answer,
        "image": image
    }
    write_to_answers(new_answer)


@connection.connection_handler
def get_comments(cursor, question_id):
    query = """SELECT * FROM comment ORDER BY submission_time"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def comment_to_answer(cursor, new_comment):
    query = """INSERT INTO comment VALUES
               (%(id)s, NULL, %(answer_id)s, %(answer_comment)s, %(submission_time)s );"""

    cursor.execute(query, {'id': new_comment['id'],

                           'answer_id': new_comment['answer_id'],
                           'answer_comment': new_comment['answer_comment'],
                           'submission_time': new_comment['submission_time']})


def create_new_comment(answer_comment, answer_id, question_id):
    new_comment = {
        'id': util.get_new_comment_id(),
        "submission_time": datetime.now().replace(microsecond=0),
        "answer_comment": answer_comment,
        "answer_id": answer_id
    }
    comment_to_answer(new_comment)


@connection.connection_handler
def delete_comment(cursor, comment_id):
    print(comment_id)
    query = """DELETE FROM comment WHERE id=%(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})


@connection.connection_handler
def comment_to_question(cursor, new_comment):
    query = """INSERT INTO comment VALUES
               (%(id)s, %(question_id)s, NULL, %(question_comment)s, %(submission_time)s );"""

    cursor.execute(query, {'id':new_comment['id'],
                           'question_id': new_comment['question_id'],
                           'question_comment': new_comment['question_comment'],
                           'submission_time': new_comment['submission_time'] })


def create_question_comment(question_comment, question_id):
    new_comment = {
        'id': util.get_new_comment_id(),
        "submission_time": datetime.now().replace(microsecond=0),
        "question_id": question_id,
        "question_comment": question_comment,
    }
    comment_to_question(new_comment)
    print(new_comment)

@connection.connection_handler
def get_tags(cursor):
    query = """SELECT name FROM tag"""
    cursor.execute(query)
    row=cursor.fetchall()
    print("ezek a tagaim2,",row)
    return row


@connection.connection_handler
def get_id_from_tag(cursor,tag_name):
    query="""SELECT id FROM tag
            WHERE name=%(tag_name)s"""
    cursor.execute(query,{'tag_name':tag_name})
    row  =cursor.fetchone()
    return row['id']


@connection.connection_handler
def add_new_tag(cursor,question_id,tag_id):
    query="""INSERT INTO question_tag VALUES (%(question_id)s, %(tag_id)s)"""
    cursor.execute(query,{'question_id':question_id,'tag_id':tag_id})


@connection.connection_handler
def get_tags_of_question(cursor):
    query="""SELECT * FROM tag JOIN question_tag ON tag.id=question_tag.tag_id"""
    cursor.execute(query)
    all = cursor.fetchall()
    return all


@connection.connection_handler
def search_for_question(cursor, search_text):
    cursor.execute(f"""
    SELECT DISTINCT question.*, answer.message AS answer_message
    FROM question   
    LEFT JOIN answer      
    ON question.id = answer.question_id AND answer.message LIKE '%{search_text}%'
    WHERE question.title LIKE '%{search_text}%' OR question.message LIKE '%{search_text}%'
            OR answer.message LIKE '%{search_text}%'
    ORDER BY question.submission_time""")
    return cursor.fetchall()


@connection.connection_handler
def delete_tags(cursor,question_id,tag_id,):
    query="""DELETE FROM question_tag WHERE tag_id=%(tag_id)s and question_id=%(question_id)s"""
    cursor.execute(query,{'tag_id':tag_id, 'question_id':question_id})


@connection.connection_handler
def create_new_tag(cursor,new_tag):
    tags=get_tags()
    tag_names=[]
    for tag in tags:
        tag_names.append(tag['name'])
    if new_tag not in tag_names:
        id=util.get_new_tag_id()
        query= """INSERT INTO tag VALUES ( %(id)s, %(name)s )"""
        cursor.execute(query, {'id':id,'name':new_tag})
        return "true"
    else:
        return "None"

@connection.connection_handler
def get_usernames(cursor,user_name):
    query="""SELECT user_name FROM users"""
    cursor.execute(query)
    user_names= cursor.fetchall()
    print("usernevek",user_names)
    print(user_name)
    for user in user_names:
        if user['user_name'] == user_name:
            return False
    return True


@connection.connection_handler
def new_registration(cursor,user_name, password):
    hashed_password = util.hash_password(password=password)
    registration_date = datetime.now().replace(microsecond=0)
    reg_id = util.get_new_registration_id()
    user_id = util.get_new_user_id()
    query = """INSERT INTO users VALUES (%(user_id)s, %(username)s, 0, 0, 0, 0);
                INSERT INTO registration VALUES (%(reg_id)s, %(username)s, %(hashed_psw)s, %(reg_date)s);
                """
    cursor.execute(query, {'reg_id':reg_id, 'username':user_name, 'hashed_psw':hashed_password, 'user_id':user_id, 'reg_date':registration_date})


@connection.connection_handler
def get_users(cursor):
    query = """SELECT * FROM users"""
    cursor.execute(query)
    users = cursor.fetchall()
    print(users)
    return users