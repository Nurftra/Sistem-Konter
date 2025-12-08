import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # 'auth' will be our authentication blueprint

import app.models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Register blueprints here
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from app.staf.routes import staf_bp
    app.register_blueprint(staf_bp)

    # Register CLI commands
    from app.cli import seed
    app.cli.add_command(seed)

    # Error handlers
    from flask import render_template
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    return app
