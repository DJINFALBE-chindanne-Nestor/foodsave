# ============================================================
# POINT D'ENTREE DE L'APPLICATION FLASK
# ============================================================

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db
from models.user import User


def create_app():
    """Cree et configure l'application Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Base de donnees ---
    db.init_app(app)

    # --- Flask-Migrate ---
    migrate = Migrate(app, db)

    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Veuillez vous connecter pour acceder a cette page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Blueprints ---
    from routes.auth import auth_bp
    from routes.annonces import annonces_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp
    from routes.chatbot import chatbot_bp
    from routes.ontologie import ontologie_bp
    from routes.recommandation import recommandation_bp
    from routes.messages import messages_bp
    from routes.legal import legal_bp
    from routes.vision import vision_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(annonces_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(ontologie_bp)
    app.register_blueprint(recommandation_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(vision_bp)

    # --- Routes de base ---
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/ping')
    def ping():
        return "pong"

    @app.route('/service-worker.js')
    def service_worker():
        from flask import send_from_directory
        return send_from_directory('static', 'service-worker.js',
                                    mimetype='application/javascript')

    # --- Context processor ---
    @app.context_processor
    def injecter_variables():
        variables = {}
        try:
            from services.ontologie_service import nb_produits_en_attente
            variables['notification_produits_attente'] = nb_produits_en_attente
        except Exception:
            variables['notification_produits_attente'] = lambda: 0

        try:
            from routes.messages import compter_messages_non_lus
            variables['nb_messages_non_lus'] = compter_messages_non_lus
        except Exception:
            variables['nb_messages_non_lus'] = lambda: 0

        return variables

    # --- Initialisation dans le contexte Flask ---
    with app.app_context():
        # Import des modeles
        from models import user, annonce, reservation  # noqa
        from models.produit_ontologie import ProduitOntologie  # noqa
        from models.log_action import LogAction  # noqa

        # Migration ontologie (si la table existe)
        from sqlalchemy import inspect
        inspecteur = inspect(db.engine)
        tables_existantes = inspecteur.get_table_names()

        if 'produit_ontologie' in tables_existantes:
            try:
                from services.ontologie_service import migrer_produits_hardcodes
                n = migrer_produits_hardcodes()
                if n > 0:
                    print(f"[FoodSave] Migration ontologie : {n} produits ajoutes.")
            except Exception as e:
                print(f"[FoodSave] Migration ontologie ignoree : {e}")

        # --- Creation auto de l'admin ---
        import os
        email_admin = os.environ.get('ADMIN_EMAIL', 'admin@foodsave.com')
        password_admin = os.environ.get('ADMIN_PASSWORD', 'AdminFoodSave2026!')

        try:
            from datetime import datetime
            admin_existant = User.query.filter_by(email=email_admin).first()
            if not admin_existant:
                admin = User(
                    email=email_admin,
                    nom='Admin FoodSave',
                    role='admin',
                    ville="N'Djamena",
                    region="N'Djamena",
                    pays='Tchad',
                    telephone='+23566000000',
                    consentement_rgpd=True,
                    date_consentement=datetime.utcnow()
                )
                admin.set_password(password_admin)
                db.session.add(admin)
                db.session.commit()
                print(f"[FoodSave] Admin cree : {email_admin}")
            else:
                print(f"[FoodSave] Admin existant : {email_admin}")
        except Exception as e:
            print(f"[FoodSave] Creation admin ignoree : {e}")

    return app


# --- Instance globale ---
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)