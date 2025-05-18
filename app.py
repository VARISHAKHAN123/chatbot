from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from routes.chat_routes import chat_bp, chat_logs_bp
from database.user_model import load_user
from database.db_connection import get_db  
from flask_login import current_user
from flask_login import LoginManager, current_user


from routes.auth_routes import auth_routes




app = Flask(__name__)
app.secret_key = 'your_secret_key'



conn = get_db()
app.conn = conn 
# Setup Bcrypt
bcrypt = Bcrypt(app)
#  Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth_routes.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user_from_db(user_id):
    return load_user(user_id)

#  Register Blueprints
app.register_blueprint(chat_bp)
app.register_blueprint(chat_logs_bp)
app.register_blueprint(auth_routes, url_prefix='/auth') 

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
