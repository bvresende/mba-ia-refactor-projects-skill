from flask import Flask
from flask_cors import CORS
from src.config.settings import settings
from src.database.db import close_db
from src.middlewares.error_handler import register_error_handlers
from src.routes.produto_routes import produto_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.pedido_routes import pedido_bp
from src.routes.relatorio_routes import relatorio_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    # Registro de rotas e Blueprints MVC
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)

    # Middlewares e ciclo de vida
    register_error_handlers(app)
    app.teardown_appcontext(close_db)

    return app
