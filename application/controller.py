from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask import current_app as app
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from .database import db
from .models import *

@app.route("/",methods=["GET","POST"])
def login():
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get("password")
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == password:
                session["user_id"] = this_user.id
                if this_user.type == "admin" :
                    return redirect("/admin")
                else:
                    return redirect("/user")
            else:
                return "password is incorrect !!"
        else:
            return "user does not exist !!"
        
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        qualification = request.form.get("qualification")
        dob = request.form.get("dob")
        dob = datetime.strptime(dob, "%Y-%m-%d").date()
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            return "user already exists !!"
        else:
            new_user = User(username=username,password=password,fullname=fullname,qualification=qualification,dob=dob)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")
    return render_template("register.html")

@app.route("/admin")
def admin():
    user_id = session.get("user_id")
    this_user = User.query.get(user_id)
    if request.method == "POST" :
        return render_template("newsubject.html")
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    sub_chapters = {}
    for chapter in chapters :
        q_count = Questions.query.join(Quiz).filter(Quiz.chapter_id == chapter.id).count()
        chapter.qcount = q_count
        sub_chapters.setdefault(chapter.subject_id,[]).append(chapter)
    return render_template("admin_dash.html",fullname=this_user.fullname,subjects=subjects,sub_chapters=sub_chapters)

@app.route("/quiz_management",methods=["GET","POST"])
def quiz_management():
    user_id = session.get("user_id")
    this_user = User.query.get(user_id)
    quizzes = Quiz.query.all()
    if request.method == "POST" :
        return redirect("/newquiz")
    else:
        return render_template("quiz_management.html",fullname=this_user.fullname,quizzes=quizzes)

@app.route("/search")
def search():
    query = request.args.get('query','').strip()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    return render_template("search.html",subjects=subjects,chapters=chapters,query=query)

@app.route("/user")
def user():
    user_id = session.get("user_id")
    this_user = User.query.get(user_id)
    quizzes = Quiz.query.all()
    return render_template("user_dash.html",this_user=this_user,quizzes=quizzes)

@app.route("/scores")
def scores():
    user_id = session.get("user_id")
    this_user = User.query.get(user_id)
    scores = Scores.query.filter_by(user_id=user_id).all()
    return render_template("scores.html",this_user=this_user,scores=scores)

@app.route("/newsubject",methods=["GET","POST"])
def newsubject():
    fullname = request.args.get("admin","Admin")
    if request.method == "POST" :
        sub_name = request.form.get("sub_name")
        description = request.form.get("description")
        this_sub = Subject.query.filter_by(name=sub_name).first()
        if this_sub:
            return "subject already exists !!"
        else:
            new_sub = Subject(name=sub_name,description=description)
            db.session.add(new_sub)
            db.session.commit()
            return redirect("/admin")
    else:
        return render_template("newsubject.html")

@app.route("/edit_sub/<int:sub_id>",methods=["GET","POST"])
def edit_sub(sub_id):
    subject = Subject.query.get(sub_id)
    if request.method == "POST" :
        subject.name = request.form.get("sub_name")
        subject.description = request.form.get("description")
        db.session.commit()
        return redirect("/admin")
    return render_template("editsub.html",subject=subject)

@app.route("/delete_sub/<int:sub_id>",methods=["GET","POST"])
def delete_sub(sub_id):
    subject = Subject.query.get(sub_id)
    chapters = Chapter.query.filter_by(subject_id=sub_id).all()
    for chapter in chapters:
        quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
        for quiz in quizzes:
            question = Questions.query.filter_by(quiz_id=quiz.id).delete()
            scores = Scores.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)
        db.session.delete(chapter)
    db.session.delete(subject)
    db.session.commit()
    return redirect("/admin")

@app.route("/newchapter",methods=["GET","POST"])
def newchapter():
    subject_id = request.args.get("subject_id") 
    subject_id = int(subject_id)
    if request.method == "POST" :
        ch_name = request.form.get("ch_name")
        description = request.form.get("description")
        
        this_ch = Chapter.query.filter_by(name=ch_name,subject_id=subject_id).first()
        if this_ch:
            return "chapter already exists !!"
        else:
            new_ch = Chapter(name=ch_name,description=description,subject_id=subject_id)
            db.session.add(new_ch)
            db.session.commit()
            return redirect("/admin")
    else:
        return render_template("newchapter.html",subject_id=subject_id)

@app.route("/edit_ch/<int:ch_id>",methods=["GET","POST"])
def edit_ch(ch_id):
    chapter = Chapter.query.get(ch_id)
    subject = Subject.query.get(ch_id)
    subject_id = subject.id
    if request.method == "POST" :
        chapter.name = request.form.get("ch_name")
        chapter.description = request.form.get("description")
        db.session.commit()
        return redirect("/admin")
    return render_template("editch.html",chapter=chapter,subject_id=subject_id)

@app.route("/delete_ch/<int:ch_id>",methods=["GET","POST"])
def delete_ch(ch_id):
    chapter = Chapter.query.get(ch_id)
    quizzes = Quiz.query.filter_by(chapter_id=ch_id).all()
    for quiz in quizzes:
        question = Questions.query.filter_by(quiz_id=quiz.id).delete()
        scores = Scores.query.filter_by(quiz_id=quiz.id).delete()
        db.session.delete(quiz)
    db.session.delete(chapter)
    db.session.commit()
    return redirect("/admin")

@app.route("/newquiz",methods=["GET","POST"])
def newquiz():
    if request.method == "POST" :
        ch_id = request.form.get("ch_id")
        date = request.form.get("date")
        duration = request.form.get("duration")
        remarks = request.form.get("remarks")
        date_of_quiz = datetime.strptime(date, "%Y-%m-%d").date()
        time_duration = timedelta(minutes=int(duration)) if duration else None
        this_quiz = Quiz.query.filter_by(chapter_id=ch_id).first()
        if this_quiz:
            return "quiz already exists !!"
        else:
            new_quiz = Quiz(chapter_id=ch_id,date_of_quiz=date_of_quiz,time_duration=time_duration,remarks=remarks)
            db.session.add(new_quiz)
            db.session.commit()
            return redirect("/admin")
    else:
        return render_template("newquiz.html")

@app.route("/edit_quiz/<int:quiz_id>",methods=["GET","POST"])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "quiz not found!"
    if request.method == "POST" :
        quiz.chapter_id = request.form.get("ch_id")
        quiz.date = request.form.get("date")
        quiz.duration = request.form.get("duration")
        quiz.remarks = request.form.get("remarks")
        db.session.commit()
        return redirect(url_for("quiz_management"))
    return render_template("editquiz.html",quiz=quiz)

@app.route("/delete_quiz/<int:quiz_id>",methods=["GET","POST"])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    scores = Scores.query.filter_by(quiz_id=quiz_id).delete()
    db.session.delete(quiz)
    db.session.commit()
    return redirect("/admin")

@app.route("/quizdetails/<int:quiz_id>",methods=["GET","POST"])
def quizdetails(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    q_count = Questions.query.filter_by(quiz_id=quiz_id).count()
    return render_template("quizdetails.html",quiz=quiz,chapter=chapter,subject=subject,q_count=q_count)

@app.route("/quizview/<int:quiz_id>",methods=["GET","POST"])
def quizview(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    q_count = Questions.query.filter_by(quiz_id=quiz_id).count()
    return render_template("quizview.html",quiz=quiz,chapter=chapter,subject=subject,q_count=q_count)

@app.route('/quizstart/<int:quiz_id>', methods=['GET', 'POST'])
def quizstart(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if 'index' not in session or session.get('quiz_id') != quiz_id:
        session['index'] = 0  
        session['quiz_id'] = quiz_id
        session['answers'] = [] 
    questions = quiz.questions
    if session['index'] >= len(questions):  # If all questions are answered
        return redirect(url_for('quiz_submit', quiz_id=quiz_id)) 
    current_question = questions[session['index']]
    if request.method == 'POST':
        selected_option = request.form.get('option')
        if selected_option:
            session['answers'].append(selected_option)
            session['index'] += 1
            session.modified = True
            return redirect(url_for('quizstart', quiz_id=quiz_id)) 

    return render_template('quizstart.html', question=current_question, quiz=quiz)

@app.route('/quiz_submit/<int:quiz_id>')
def quiz_submit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions 
    user_answers = session.get('answers', [])

    score = 0
    for question, user_answer in zip(questions, user_answers):
        if user_answer == question.correct_option:
            score += 1  
    new_score = Scores(user_id=session.get('user_id'), quiz_id=quiz_id, total_scored=score)
    db.session.add(new_score)
    db.session.commit()

    # Clear session quiz data
    session.pop('index', None)
    session.pop('quiz_id', None)
    session.pop('answers', None)
    flash(f'Quiz completed! Your score: {score}/{len(questions)}', 'success')
    return redirect(url_for('user'))  

@app.route("/newquestion<int:quiz_id>",methods=["GET","POST"])
def newquestion(quiz_id):
    if request.method == "POST" :
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        c_option = request.form.get("c_option")
        this_question = Questions.query.filter_by(question=question_statement,quiz_id=quiz_id).first()
        if this_question:
            return "question already exists !!"
        else:
            new_question = Questions(quiz_id=quiz_id,question=question_statement,option1=option1,option2=option2,option3=option3,option4=option4,correct_option=c_option)
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for("newquestion",quiz_id=quiz_id))
    else:
        return render_template("newquestion.html",quiz_id=quiz_id)

@app.route("/edit_question/<int:question_id>",methods=["GET","POST"])
def edit_question(question_id):
    if request.method == "POST" :
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        c_option = request.form.get("c_option")
        this_question = Question.query.filter_by(question_statement=question_statement).first()
        if this_question:
            return "question already exists !!"
        else:
            new_question = Question(quiz_id=quiz_id,question_statement=question_statement,option1=option1,option2=option2,option3=option3,option4=option4,c_option=c_option)
            db.session.add(new_question)
            db.session.commit()
            return redirect("/admin_dash")
    else:
        return render_template("newquestion.html")

@app.route("/delete_question/<int:question_id>",methods=["GET","POST"])
def delete_question(question_id):
    question = Questions.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect("/quiz_management")

# Function to generate Subject-wise Chapter Count Bar Plot
def generate_subject_chapter_chart():
    subjects = Subject.query.all()
    subject_names = [subject.name for subject in subjects]
    chapter_counts = [len(subject.chapter) for subject in subjects]

    plt.figure(figsize=(8, 4))
    plt.bar(subject_names, chapter_counts, color='skyblue')
    plt.xlabel("Subjects")
    plt.ylabel("Number of Quizzes")
    plt.title("Number of Quizzes per Subject")
    plt.xticks(rotation=45)

    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return base64.b64encode(img.getvalue()).decode('utf8')

# Function to generate Month-wise Quiz Attempt Pie Chart
def generate_quiz_attempt_chart():
    scores = Scores.query.all()
    months = {}
    
    for score in scores:
        month = score.time_stamp.strftime("%B")  # Get month name
        months[month] = months.get(month, 0) + 1
    
    month_labels = list(months.keys())
    quiz_counts = list(months.values())

    plt.figure(figsize=(4,4))
    plt.pie(quiz_counts, labels=month_labels, autopct='%1.1f%%', colors=['lightcoral', 'gold', 'lightblue', 'lightgreen'])
    plt.title("Number of Quizzes Attempted Per Month")

    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return base64.b64encode(img.getvalue()).decode('utf8')

@app.route('/summary_charts')
def summary_charts():
    user_id = session.get("user_id")
    this_user = User.query.get(user_id)

    if not this_user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))  # Redirect to login if user is not found

    if this_user.type == 'admin':  
        # Generate admin-specific charts
        subject_top_scores_chart = generate_subject_top_scores_chart()
        subject_user_attempts_chart = generate_subject_user_attempts_chart()

        return render_template("summary_charts.html",this_user=this_user,
                               chart1=subject_top_scores_chart, 
                               chart2=subject_user_attempts_chart, 
                               user_type='admin')
    else:  
        # Generate user-specific charts
        subject_chapter_chart = generate_subject_chapter_chart()
        quiz_attempt_chart = generate_quiz_attempt_chart()

        return render_template("summary_charts.html",this_user=this_user, 
                               chart1=subject_chapter_chart, 
                               chart2=quiz_attempt_chart, 
                               user_type='user')

def generate_subject_top_scores_chart():
    subjects = Subject.query.all()
    subject_names = []
    top_scores = []

    for subject in subjects:
        quizzes = subject.chapter  # Get all chapters under the subject
        max_score = None

        for chapter in quizzes:
            for quiz in chapter.quizzes:
                highest_score = Scores.query.filter_by(quiz_id=quiz.id).order_by(Scores.total_scored.desc()).first()
                if highest_score and highest_score.total_scored > max_score:
                    max_score = highest_score.total_scored

        subject_names.append(subject.name)
        top_scores.append(max_score if max_score is not None else 0)

    plt.figure(figsize=(8, 4))
    plt.bar(subject_names, top_scores, color='lightcoral')
    plt.xlabel("Subjects")
    plt.ylabel("Top Score")
    plt.title("Top Scores per Subject")
    plt.xticks(rotation=45)

    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return base64.b64encode(img.getvalue()).decode('utf8')

def generate_subject_user_attempts_chart():
    subjects = Subject.query.all()
    subject_attempts = {}

    for subject in subjects:
        total_attempts = 0

        for chapter in subject.chapter:
            for quiz in chapter.quizzes:
                attempts = Scores.query.filter_by(quiz_id=quiz.id).count()
                if attempts is None:
                    attempts = 0
                total_attempts += attempts

        subject_attempts[subject.name] = total_attempts

    subject_labels = list(subject_attempts.keys())
    attempt_counts = list(subject_attempts.values())

    if sum(attempt_counts) == 0:
        subject_labels = ["No Data Available"]
        attempt_counts = [1]

    plt.figure(figsize=(4, 4))
    plt.pie(attempt_counts, labels=subject_labels, autopct='%1.1f%%', colors=['lightblue', 'lightgreen', 'gold', 'lightcoral'])
    plt.title("User Quiz Attempts per Subject")

    # Convert plot to image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return base64.b64encode(img.getvalue()).decode('utf8')
