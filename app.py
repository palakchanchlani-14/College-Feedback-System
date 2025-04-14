from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
import re
client = MongoClient("mongodb+srv://palakchanchlani14:palakchanchlani14@cluster0.n2olzwd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["feedback_db"]

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 🗂️ **MongoDB Connection**
client = MongoClient("mongodb://localhost:27017/")
db = client['CollegeFeedback']
collection = db['feedbacks']
users = db['users']

# ✅ **Fix MongoDB Indexing**
with app.app_context():
    collection.create_index([("name", 1), ("department", 1), ("faculty", 1), ("feedback", 1)])
    users.create_index([("username", 1)])

# 🏠 **Home Route - Show Login Choices First**
@app.route('/')
def home():
    return render_template('index.html')

# ✅ **Admin Login Route**
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error_message = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "palak" and password == "123":
            session['user'] = "admin"
            return redirect(url_for("admin_dashboard"))

        error_message = "❌ Incorrect credentials for Admin!"
    
    return render_template('admin_login.html', error=error_message)

# ✅ **Student Login Route**
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ✅ Now anyone can login with any username-password!
        session['user'] = username
        return redirect(url_for("feedback"))  

    return render_template('student_login.html')


# ✍ **Feedback Form Page (Students Only)**
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user' not in session or session['user'] == "admin":
        return redirect(url_for('student_login'))

    if request.method == 'POST':
        collection.insert_one({
            'name': session['user'],
            'email': request.form['email'],
            'subject': request.form['subject'],
            'department': request.form['department'],
            'faculty': request.form['faculty'],
            'feedback': request.form['feedback'],
            'rating': request.form['rating'],
            'suggestions': request.form['suggestions']
        })
        return redirect(url_for('thank_you'))

    return render_template('feedback.html')

# ✅ **Thank You Page After Feedback**
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# ✅ **Admin Dashboard (View All Feedbacks & Search)**
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session['user'] != "admin":
        return redirect(url_for('admin_login'))

    feedbacks = list(collection.find().sort("name"))
    return render_template("admin_dashboard.html", feedbacks=feedbacks)

# ✅ **Search Feedback by Name (For Admin)**
@app.route('/search_feedback', methods=['GET'])
def search_feedback():
    if 'user' not in session or session['user'] != "admin":
        return redirect(url_for('admin_login'))

    query_name = request.args.get('query', '').strip()
    feedbacks = list(collection.find({"name": {"$regex": f"^{re.escape(query_name)}", "$options": "i"}}).sort("name"))

    return render_template("search_feedback.html", feedbacks=feedbacks, query=query_name)

# ✅ **Logout Route**
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# 🚀 **Run Flask App**
if __name__ == '__main__':
    app.run(debug=True)
