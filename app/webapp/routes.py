from flask import Blueprint, render_template

# On garde le nom 'main' pour ton interface web
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')