from flask import Flask, request, render_template, redirect, session, url_for
from functools import wraps
import data_manager
import os
import util
from tkinter import *
from tkinter import messagebox

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def inject_variables(page_if_false):
    def authenticate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'question_id' not in kwargs:
                try:
                    question_id = (data_manager.get_question_id(kwargs['answer_id']))['question_id']
                except:
                    question_id = None
            else:
                question_id = kwargs['question_id']
            if 'username' not in session:
                window = Tk()
                window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
                window.withdraw()
                if messagebox.askokcancel("Warning", "You need to login first", icon="error") == True:
                    page = 'login'
                else:
                    page = page_if_false
                window.deiconify()
                window.destroy()
                window.quit()
                return redirect(url_for(page, question_id=question_id))
            return func(*args, **kwargs)

        return wrapper

    return authenticate


@app.route("/")
def display_main_list():
    list_of_questions = data_manager.get_main_list(5)
    return render_template("mainlist.html", list_of_questions=list_of_questions)


@app.route('/list')
def display_list():
    mode = request.args.get('order_by')
    direction = request.args.get('order_direction')
    if mode:
        list_of_questions = data_manager.get_display_list(mode=mode, direction=direction)
    else:
        list_of_questions = data_manager.get_display_list()
    return render_template("list.html", list_of_questions=list_of_questions)


@app.route("/question/<int:question_id>")
def question_page(question_id):
    question_details = data_manager.get_display_question(question_id)
    answers = data_manager.get_display_answers('question_id', question_id)
    comments = data_manager.get_comments(question_id)
    tags = data_manager.get_tags_of_question()
    user_of_question = data_manager.get_user_name_by_question_id(question_id)['user_name']
    return render_template("question.html", question_id=question_id, question=question_details, answers=answers,
                           comments=comments, user_of_question=user_of_question, tags=tags)


@app.route('/add-question', methods=["GET", "POST"])
@inject_variables('display_list')
def add_question():
    if request.method == "POST":
        dictionary_of_questions = data_manager.create_new_question()
        file = request.files['questionimage']
        image = util.get_image_name(file)
        user_id = data_manager.get_user_id_by_username(session['username'])
        dictionary_of_questions.update(
            {'user_id': user_id, 'title': request.form.get('questiontitle'),
             'message': request.form.get('questionbody'), 'image': image})
        data_manager.write_to_questions(dictionary_of_questions)
        data_manager.more_user_details(user_id=user_id)
        return redirect('/list')
    else:
        return render_template('ask_questions.html')


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
@inject_variables('question_page')
def delete_question(question_id):
    if request.method == 'POST':
        image = data_manager.get_display_question(question_id)['image']
        if os.path.exists(image):
            os.remove(image)
        data_manager.delete_question(question_id)
    return redirect('/list')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
@inject_variables('question_page')
def edit_question(question_id):
    question_details = data_manager.get_display_question(question_id)
    if request.method == 'GET':
        return render_template("edit_question_new.html", question=question_details)
    else:
        new_title = request.form['edittitle']
        new_message = request.form['editbody']
        file = request.files['editimage']
        filename = file.filename
        if filename != '':
            filename = os.path.join('static/', filename)
            file.save(filename)
            image = filename
        else:
            image = question_details['image']
        data_manager.update_question(question_id, new_title, new_message, image)
    return redirect('/question/' + question_id)


@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
@inject_variables('display_list')
def edit_answer(answer_id):
    answer_details = data_manager.get_display_answers('id', answer_id)
    if request.method == 'GET':
        return render_template("edit_answer.html", answer=answer_details)
    else:
        new_message = request.form['editbody']
        file = request.files['editimage']
        filename = file.filename
        if filename != '':
            filename = os.path.join('static/', filename)
            file.save(filename)
            image = filename
        else:
            image = answer_details[0]['image']
        data_manager.update_answer(answer_id, new_message, image)
        question_id = str(answer_details[0]['question_id'])
        return redirect('/question/' + question_id)


@app.route('/comment/<comment_id>/edit', methods=["GET", "POST"])
@inject_variables('display_list')
def edit_comment(comment_id):
    comment_details = data_manager.get_display_comment(comment_id)
    answer_id = data_manager.get_id_from_comment(comment_id=comment_id)['answer_id']
    print(comment_details['question_id'])
    question_id = comment_details['question_id'] if comment_details['question_id'] is not None else (data_manager.get_question_id(answer_id))['question_id']
    print("question_id")
    print(question_id)
    comment_details['question_id'] = question_id
    if request.method == 'GET':
        print("comment details")
        print(comment_details)
        return render_template("edit_comment.html", comment=comment_details)
    else:
        new_message = request.form['editbody']
        data_manager.update_comment(comment_id, new_message)
        return redirect('/question/' + str(question_id))


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
@inject_variables('question_page')
def add_new_answer(question_id):
    if request.method == "POST":
        new_answer = request.form["answer"]
        user_id = data_manager.get_user_id_by_username(session['username'])
        file = request.files['img']
        image = util.get_image_name(file)
        data_manager.create_new_answer(new_answer, question_id, image, user_id)
        data_manager.more_user_details(user_id=user_id)
        return redirect("/question/" + question_id)
    else:
        return render_template("new_answer.html", question_id=question_id)


@app.route('/answer/<answer_id>/delete')
@inject_variables('display_list')
def delete_answer(answer_id):
    question_id = data_manager.get_question_id(answer_id)['question_id']
    image = data_manager.get_display_answers('question_id', question_id)[0]['image']
    if os.path.exists(image):
        os.remove(image)
    data_manager.delete_answer_by_id(answer_id)
    return redirect('/question/' + str(question_id))


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
@inject_variables('question_page')
def add_comment_to_answer(answer_id):
    if request.method == 'POST':
        question_id = (data_manager.get_question_id(answer_id))['question_id']
        answer_comment = request.form['answer_comment']
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.create_new_comment(answer_comment, user_id, answer_id=answer_id, question_id=question_id)
        data_manager.more_user_details(user_id=user_id)
        return redirect('/question/' + str(question_id))
    return render_template('add_cooment_to_answer.html', answer_id=answer_id)


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
@inject_variables('question_page')
def add_comment_to_question(question_id):
    if request.method == 'POST':
        question_comment = request.form['question_comment']
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.create_question_comment(question_comment, user_id, question_id=question_id)
        return redirect('/question/' + str(question_id))
    else:
        return render_template('comment_to_question.html', question_id=question_id)


@app.route('/comments/<comment_id>/delete', methods=['GET', 'POST'])
@inject_variables('display_list')
def delete_comment(comment_id):
    answer_id = data_manager.get_id_from_comment(comment_id=comment_id)['answer_id']
    try:
        question_id = (data_manager.get_question_id(answer_id))['question_id']
    except:
        question_id = (data_manager.get_id_from_comment(comment_id=comment_id))['question_id']
    data_manager.delete_comment(comment_id)
    return redirect('/question/' + str(question_id))


@app.route('/question/<question_id>/vote_up')
@inject_variables('display_list')
def vote_up_question(question_id):
    data_manager.vote_up_question(question_id)
    user_id = data_manager.get_display_question(question_id)['user_id']
    reputation = data_manager.get_reputation(user_id=user_id)
    data_manager.update_reputation(user_id, (reputation + 5))
    return redirect('/list')


@app.route('/question/<question_id>/vote_down')
@inject_variables('display_list')
def vote_down_question(question_id):
    data_manager.vote_down_question(question_id)
    user_id = data_manager.get_display_question(question_id)['user_id']
    reputation = data_manager.get_reputation(user_id=user_id)
    data_manager.update_reputation(user_id, (reputation - 2))
    return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
@inject_variables('display_list')
def vote_up_answer(answer_id):
    data_manager.vote_up_answer(answer_id)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)['question_id']
    user_id = data_manager.get_display_question(question_id)['user_id']
    reputation = data_manager.get_reputation(user_id=user_id)
    data_manager.update_reputation(user_id, (reputation + 10))
    return redirect('/question/' + str(question_id))


@app.route('/answer/<answer_id>/vote_down')
@inject_variables('display_list')
def vote_down_answer(answer_id):
    data_manager.vote_down_answer(answer_id)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)['question_id']
    user_id = data_manager.get_display_question(question_id)['user_id']
    reputation = data_manager.get_reputation(user_id=user_id)
    data_manager.update_reputation(user_id, (reputation - 2))
    return redirect('/question/' + str(question_id))


@app.route('/search')
def search_for_questions():
    search_text = request.args.get('search_text').replace('+', ' ')
    list_of_questions = data_manager.search_for_question(search_text)
    return render_template("search.html", search_text=search_text, list_of_questions=list_of_questions)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
@inject_variables('question_page')
def add_new_tag(question_id):
    if request.method == 'POST':
        tag_name = request.form['tag_name']
        new_tag_type = request.form['new_tag_type']
        tag_id = data_manager.get_id_from_tag(tag_name=tag_name)
        if new_tag_type == '':
            try:
                data_manager.add_new_tag(tag_id=tag_id, question_id=question_id)
            except:
                tags = data_manager.get_tags()
                return render_template('tag_problem.html', tags=tags, question_id=question_id)
        else:
            if data_manager.create_new_tag(new_tag=new_tag_type) != "None":
                tag_id = data_manager.get_id_from_tag(tag_name=new_tag_type)
                data_manager.add_new_tag(tag_id=tag_id, question_id=question_id)
            else:
                tags = data_manager.get_tags()
                return render_template('tag_problem.html', tags=tags, question_id=question_id)
        return redirect('/question/' + str(question_id))
    tags = data_manager.get_tags()
    return render_template('tag_new.html', tags=tags, question_id=question_id)


@app.route("/question/<question_id>/tag/<tag_id>/delete")
@inject_variables('question_page')
def delete_tag(question_id, tag_id):
    data_manager.delete_tags(question_id=question_id, tag_id=tag_id)
    return redirect('/question/' + str(question_id))


@app.route("/question/<question_id>/increase_view_number")
def increase_view_number(question_id):
    data_manager.update_view_number(question_id)
    return redirect('/question/' + str(question_id))


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        user_name = request.form['email']
        password = request.form['psw']
        if data_manager.get_usernames(user_name) is False:
            message = 'This username already exists. Please, choose another one!'
            return render_template('registration_incorrect.html', message=message)
        else:
            data_manager.new_registration(user_name=user_name, password=password)
            return redirect('/list')
    return render_template('registration.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if data_manager.get_usernames(username) is False:
            reg_password = data_manager.get_password(username)
            is_matching = util.verify_password(password, reg_password)
            if is_matching:
                session['username'] = request.form['username']
                return redirect(url_for('display_list'))
            else:
                message = "Wrong e-mail or password!"
                return render_template('login_fail.html', message=message)
        else:
            message = "Wrong e-mail or password!"
            return render_template('login_fail.html', message=message)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('display_list'))


@app.route('/users')
@inject_variables('display_list')
def users():
    users = data_manager.get_users()
    return render_template('users.html', users=users)


@app.route('/user/<user_name>')
@inject_variables('display_list')
def user_details(user_name):
    # user_id = data_manager.get_user_id_by_username(username=user_name)
    # data_manager.more_user_details(user_id=user_id)
    user_detail = data_manager.get_user_details(user_name=user_name)
    user_questions = data_manager.get_user_questions(user_name=user_name)
    user_answers = data_manager.get_user_answers(user_name=user_name)
    user_comments = data_manager.get_user_comments(user_name=user_name)
    return render_template('user_details.html', user_name=user_name, user_details=user_detail,
                           user_questions=user_questions, user_answers=user_answers, user_comments=user_comments)


@app.route('/tags')
def display_tags():
    count_of_tags = data_manager.count_tags()
    return render_template('tags.html', count_of_tags=count_of_tags)


@app.route('/answer/<answer_id>/accept_answer')
@inject_variables('display_list')
def accept_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)['question_id']
    user_questions = data_manager.get_user_questions(session['username'])
    question_ids = [q['id'] for q in user_questions]
    user_id_for_answer = data_manager.get_user_name_by_question_id(question_id)['id']
    if question_id in question_ids:
        data_manager.update_reputation_by_acceptance(answer_id, user_id_for_answer)
        data_manager.change_acceptance(answer_id)
    return redirect('/question/' + str(question_id))


if __name__ == "__main__":
    app.run(debug=True,
            port=8000,
            host='0.0.0.0')
