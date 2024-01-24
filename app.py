from flask import session , request , Flask , render_template , redirect , flash
from cs50 import SQL
from flask_session import Session
from werkzeug.security import generate_password_hash , check_password_hash 
from werkzeug.utils import secure_filename
import os 


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///database.db")
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'c','py'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def apology(message):
    return render_template("apology.html",message=message)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")
    
    rows = db.execute("SELECT * FROM code")

    if not rows:
        return redirect("/file")
    
    
    print(rows[0]["username"])
    return render_template("index.html",rows=rows)


@app.route("/file",methods=["GET","POST"])
def file():
    if not session.get("user_id"):
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("file.html")
    
    else:
        if 'file' not in request.files:
            return apology('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return apology('No selected file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session["filename"] = filename
            return redirect("/text")
        
@app.route("/text",methods=["GET","POST"])
def text():
    if not session.get("user_id"):
        return redirect("/login")
    
    if not session.get("filename"):
        return redirect("/file")
    
    if request.method == "GET":
        return render_template("text.html")
    
    else:
        title = request.form.get("title")
        description = request.form.get("description")

        username = db.execute("SELECT username FROM users WHERE id = ?",session["user_id"])[0]["username"]
        print(username)


        db.execute("INSERT INTO code (id,username,title,description,filename) VALUES(?,?,?,?,?)",session["user_id"],username,title,description,session["filename"])
        return redirect("/")


@app.route("/register",methods=["GET","POST"])
def register():
    session.clear()
    if request.method == "GET":
        return render_template("register.html")
    
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username:
            return apology("Username not provided ):")
        
        elif not password:
            return apology("Password not provided ):")
        
        elif not confirm_password:
            return apology("Password confirmation not provided ):")
        
        elif confirm_password!=password:
            return apology("Passwords do not match ):")
        

        name = db.execute("SELECT * FROM users WHERE username = ?",username)

        if name:
            return redirect("/register")        
        

        db.execute("INSERT INTO users (username,hash) VALUES(?,?)",username,generate_password_hash(password))

        rows = db.execute("SELECT * FROM users WHERE username = ?",request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        
        return redirect("/")
        


@app.route("/login",methods=["GET","POST"])
def login(): 
    session.clear()   
    if request.method == "GET":
        return render_template("login.html")
    
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("Username not provided ):")
        
        elif not password:
            return apology("Password not provided ):")
        

        rows = db.execute("SELECT * FROM users WHERE username = ?",username)

        if not rows or not check_password_hash(rows[0]["hash"],password):
            return apology("Password/Username Invalid ):")
        
        session["user_id"] = rows[0]["id"]

        return redirect("/")
        

@app.route("/logout",methods=["GET","POST"])
def logout():
    session.clear()
    return redirect("/login")


    

app.run(debug=True)