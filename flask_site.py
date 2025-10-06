from flask import Flask, render_template, request, redirect, url_for, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from markupsafe import escape
from weasyprint import HTML

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    idNum = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        new_item = Item(name=name)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/update/<int:idNum>', methods=['GET', 'POST'])
def update(idNum):
    item = Item.query.get_or_404(idNum)
    if request.method == 'POST':
        item.name = request.form['name']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', item=item)

@app.route('/delete/<int:idNum>', methods=['POST'])
def delete(idNum):
    item = Item.query.get_or_404(idNum)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

# @app.route('/')
# def index():
#     return "Index Page"

@app.route('/hello')
@app.route('/hello/')
@app.route("/hello/<user_name>")
def hello_user(user_name=None):
    return render_template('home.html', name=user_name)

@app.route('/report/preview')
def report_preview():
    report_content = "This is the report data."
    return render_template('report.html', report_content=report_content)

@app.route('/report/download')
def report_download():
    rendered_html = render_template('report.html', report_content="This is the report data.")
    pdf_file = BystesIO()
    HTML(string=rendered_html).write_pdf(pdf_file)
    pdf_file.seek(0)

    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response