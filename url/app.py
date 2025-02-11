from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for storing URL mappings
class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

# Route for the homepage (form for shortening URLs)
@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']

        # Check if the URL already exists
        existing_url = URLMap.query.filter_by(original_url=original_url).first()
        if existing_url:
            short_url = existing_url.short_url
        else:
            # Generate a random short URL
            short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            # Ensure unique short URL
            while URLMap.query.filter_by(short_url=short_url).first():
                short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            # Store the original and short URL in the database
            new_url = URLMap(original_url=original_url, short_url=short_url)
            db.session.add(new_url)
            db.session.commit()

    return render_template('index.html', short_url=short_url)

# Route for redirecting short URLs
@app.route('/<short_url>')
def redirect_to_original(short_url):
    url_map = URLMap.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url_map.original_url)

# Create the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
