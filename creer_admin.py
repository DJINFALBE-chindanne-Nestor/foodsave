from app import app
from models import db
from models.user import User


def creer_admin():
    with app.app_context():
        existant = User.query.filter_by(email='admin@foodsave.com').first()
        if existant:
            print(">>> Admin deja existant (ID :", existant.id, ")")
            return

        admin = User(
            email='admin@foodsave.com',
            nom='Admin FoodSave',
            role='admin',
            ville="N'Djamena",
            region="N'Djamena",
            pays='Tchad',
            telephone='+23566000000'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(">>> Admin cree avec ID :", admin.id)
        print(">>> Email    : admin@foodsave.com")
        print(">>> Password : admin123")


if __name__ == '__main__':
    creer_admin()
