from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, ReportSubscription, Task
from datetime import datetime, timedelta
from flask_mail import Message
from extensions import db, mail
from models import User, Task, ReportSubscription
from apscheduler.schedulers.background import BackgroundScheduler


auth = Blueprint("auth", __name__)

@auth.route("/")
def home():
    return render_template("index.html")

@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(username=username, email=email, password=password)
    new_user.hash_password()
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200




@auth.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        start_date=data.get('start_date'),
        due_date=data.get('due_date'),
        status=data.get('status', 'Pending'),
        user_id=current_user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully"}), 201

@auth.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    current_user_id = get_jwt_identity()
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Task.query.filter_by(user_id=current_user_id)
    if status:
        query = query.filter_by(status=status)
    if start_date and end_date:
        query = query.filter(Task.start_date >= start_date, Task.due_date <= end_date)

    tasks = query.all()
    tasks_list = [{"id": task.id, "title": task.title, "status": task.status} for task in tasks]
    return jsonify(tasks_list), 200

@auth.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.start_date = data.get('start_date', task.start_date)
    task.due_date = data.get('due_date', task.due_date)
    task.status = data.get('status', task.status)
    db.session.commit()

    return jsonify({"message": "Task updated successfully"}), 200

# حذف مهمة
@auth.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200





# وظيفة لتوليد التقرير وإرساله بالبريد الإلكتروني
def send_report(user_id, frequency):
    now = datetime.utcnow()
    if frequency == 'daily':
        end_date = now - timedelta(days=1)
    elif frequency == 'weekly':
        end_date = now - timedelta(weeks=1)
    elif frequency == 'monthly':
        end_date = now - timedelta(weeks=4)

    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.end_date >= end_date
    ).all()

    user = User.query.get(user_id)
    subject = f"Your {frequency} task report"
    body = "Here are your tasks for the last period:\n"
    for task in tasks:
        body += f"{task.title} - {task.status}\n"

    msg = Message(subject, recipients=[user.email], body=body)
    mail.send(msg)

@auth.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_report():
    user_id = get_jwt_identity()

    data = request.get_json()
    start_date = datetime.strptime(data['start_date'], "%d:%m:%Y %H")
    frequency = data['frequency']
    report_time = data['report_time']

    if frequency not in ['daily', 'weekly', 'monthly']:
        return jsonify({"error": "Invalid frequency"}), 400

    if not (0 <= report_time <= 23):
        return jsonify({"error": "Invalid report time (0-23 hours)"}), 400

    subscription = ReportSubscription(
        user_id=user_id,
        start_date=start_date,
        frequency=frequency,
        report_time=report_time
    )

    db.session.add(subscription)
    db.session.commit()

    # جدولة إرسال التقرير بناءً على التردد
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_report,
        'interval',
        hours=24 if frequency == 'daily' else 168 if frequency == 'weekly' else 720,
        args=[user_id, frequency],
        start_date=start_date.replace(hour=report_time, minute=0, second=0)
    )
    scheduler.start()

    return jsonify({"message": "Subscribed to reports successfully!"}), 201

@auth.route('/unsubscribe', methods=['DELETE'])
@jwt_required()
def unsubscribe_report():
    user_id = get_jwt_identity()

    subscription = ReportSubscription.query.filter_by(user_id=user_id).first()
    
    if not subscription:
        return jsonify({"error": "No subscription found"}), 404

    db.session.delete(subscription)
    db.session.commit()

    return jsonify({"message": "Unsubscribed from reports successfully!"})





# إرسال تقرير عبر البريد الإلكتروني
def send_report_email(user_email, tasks_report, frequency):
    msg = Message('Your Task Report',
                  sender='your-email@gmail.com',
                  recipients=[user_email])
    
    # تقرير المهام بشكل HTML
    msg.html = render_template('email_report.html', tasks_report=tasks_report, frequency=frequency)
    mail.send(msg)

# توليد التقارير بناءً على التكرار
@auth.route('/generate_reports', methods=['GET'])
def generate_reports():
    # التحقق من الاشتراكات
    report_subscriptions = ReportSubscription.query.all()
    
    for subscription in report_subscriptions:
        # تحديد فترة التقارير بناءً على التكرار
        if subscription.frequency == 'daily':
            start_date = datetime.now() - timedelta(days=1)
        elif subscription.frequency == 'weekly':
            start_date = datetime.now() - timedelta(weeks=1)
        elif subscription.frequency == 'monthly':
            start_date = datetime.now() - timedelta(days=30)
        else:
            continue  # إذا كان التكرار غير صحيح

        # الحصول على المهام التي انتهت في الفترة المحددة
        tasks = Task.query.filter(Task.end_date >= start_date).all()
        
        tasks_report = []
        for task in tasks:
            tasks_report.append({
                'title': task.title,
                'status': task.status,
                'end_date': task.end_date.strftime('%d/%m/%Y %H:%M')
            })
        
        # إرسال البريد الإلكتروني للمستخدم
        send_report_email(subscription.user.email, tasks_report, subscription.frequency)
        
    return "Reports sent successfully", 200

