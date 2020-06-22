from flask import Flask, request, render_template, redirect
import data_manager
from datetime import datetime
import time
import os
import util

app = Flask(__name__)


@app.route("/")
def display_main_list():
    list_of_questions = data_manager.get_main_list(5)
    return render_template("mainlist.html", list_of_questions=list_of_questions)


@app.route('/list')
def display_list():
    mode = request.args.get('order_by')
    direction = request.args.get('order_direction')
    if mode:
        list_of_questions = data_manager.get_display_list(mode, direction)
    else:
        list_of_questions = data_manager.get_display_list()
    return render_template("list.html", list_of_questions=list_of_questions)


@app.route("/question/<int:question_id>")
def question_page(question_id):
    question_details = data_manager.get_display_question(question_id)
    answers = data_manager.get_display_answers('question_id', question_id)
    comments = data_manager.get_comments(question_id)
    tags = data_manager.get_tags_of_question()
    return render_template("question.html", question_id=question_id, question=question_details, answers=answers,
                           comments=comments, tags=tags)


@app.route('/add-question', methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        dictionary_of_questions = data_manager.create_new_question()
        file = request.files['questionimage']
        image = util.get_image_name(file)
        dictionary_of_questions.update(
            {'title': request.form.get('questiontitle'), 'message': request.form.get('questionbody'), 'image': image})
        data_manager.write_to_questions(dictionary_of_questions)
        return redirect('/list')
    else:
        return render_template('ask_questions.html')


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    if request.method == 'POST':
        data_manager.delete_question(question_id)
    return redirect('/list')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
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
def edit_comment(comment_id):
    comment_details = data_manager.get_display_comment(comment_id)
    if request.method == 'GET':
        return render_template("edit_comment.html", comment=comment_details)
    else:
        new_message = request.form['editbody']
        data_manager.update_comment(comment_id, new_message)
        answer_id = data_manager.get_id_from_comment(comment_id=comment_id)['answer_id']
        try:
            question_id = (data_manager.get_question_id(answer_id))['question_id']
        except:
            question_id = (data_manager.get_id_from_comment(comment_id=comment_id))['question_id']
        return redirect('/question/' + str(question_id))


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def add_new_answer(question_id):
    if request.method == "POST":
        new_answer = request.form["answer"]
        file = request.files['img']
        image = util.get_image_name(file)
        data_manager.create_new_answer(new_answer, question_id, image)
        return redirect("/question/" + question_id)
    else:
        return render_template("new_answer.html", question_id=question_id)


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    question_id = data_manager.get_question_id(answer_id)['question_id']
    data_manager.delete_answer_by_id(answer_id)
    return redirect('/question/' + str(question_id))


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    if request.method == 'POST':
        question_id = (data_manager.get_question_id(answer_id))['question_id']
        answer_comment = request.form['answer_comment']
        data_manager.create_new_comment(answer_comment, answer_id=answer_id, question_id=question_id)
        return redirect('/question/' + str(question_id))
    return render_template('add_cooment_to_answer.html', answer_id=answer_id)


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'POST':
        question_comment = request.form['question_comment']
        data_manager.create_question_comment(question_comment, question_id=question_id)
        return redirect('/question/' + str(question_id))
    else:
        return render_template('comment_to_question.html', question_id=question_id)


@app.route('/comments/<comment_id>/delete', methods=['GET', 'POST'])
def delete_comment(comment_id):
    answer_id = data_manager.get_id_from_comment(comment_id=comment_id)['answer_id']
    try:
        question_id = (data_manager.get_question_id(answer_id))['question_id']
    except:
        question_id = (data_manager.get_id_from_comment(comment_id=comment_id))['question_id']
    data_manager.delete_comment(comment_id)
    return redirect('/question/' + str(question_id))


@app.route('/question/<question_id>/vote_up')
def vote_up_question(question_id):
    data_manager.vote_up_question(question_id)
    return redirect('/list')


@app.route('/question/<question_id>/vote_down')
def vote_down_question(question_id):
    data_manager.vote_down_question(question_id)
    return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
def vote_up_answer(answer_id):
    data_manager.vote_up_answer(answer_id)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)['question_id']
    return redirect('/question/' + str(question_id))


@app.route('/answer/<answer_id>/vote_down')
def vote_down_answer(answer_id):
    data_manager.vote_down_answer(answer_id)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)['question_id']
    return redirect('/question/' + str(question_id))


@app.route('/search')
def search_for_questions():
    search_text = request.args.get('search_text').replace('+',' ')
    list_of_questions = data_manager.search_for_question(search_text)
    print (list_of_questions)
    return render_template("search.html", search_text=search_text, list_of_questions=list_of_questions)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
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
                return render_template('error_tag.html',tags=tags, question_id=question_id)
        else:
            if data_manager.create_new_tag(new_tag=new_tag_type) != "None":
                tag_id=data_manager.get_id_from_tag(tag_name=new_tag_type)
                data_manager.add_new_tag(tag_id=tag_id, question_id=question_id)
            else:
                tags = data_manager.get_tags()
                return render_template('error_tag.html', tags=tags, question_id=question_id)
        return redirect('/question/' + str(question_id))
    tags = data_manager.get_tags()
    return render_template('new_tag.html', tags=tags, question_id=question_id)


@app.route("/question/<question_id>/tag/<tag_id>/delete")
def delete_tag(question_id, tag_id):
    data_manager.delete_tags(question_id=question_id,tag_id=tag_id)
    return redirect('/question/' + str(question_id))


@app.route("/question/<question_id>/increase_view_number")
def increase_view_number(question_id):
    data_manager.update_view_number(question_id)
    return redirect('/question/' + str(question_id))


if __name__ == "__main__":
    app.run(debug=True,
            port=8000,
            host='0.0.0.0')
