import sys
import os
from datetime import datetime, timezone

# Assegura que o diretório atual do task-manager-api esteja no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from config.settings import settings
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    # Registro de Blueprints MVC
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    # Middlewares globais
    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("TASK MANAGER API (ARQUITETURA MVC REFATORADA)")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=5000)
