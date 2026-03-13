from app import db
from app.models import User, Coord, Pereval, Image, Difficulty
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerevalData:
    """Класс для работы с данными перевалов"""

    @staticmethod
    def add_pereval(data):
        """
        Добавление нового перевала в БД
        Возвращает: (success: bool, message: str, id: int or None)
        """
        try:
            # 1. Проверяем существование пользователя по email
            user_data = data['user']
            user = User.query.filter_by(email=user_data['email']).first()

            if not user:
                # Создаем нового пользователя
                user = User(
                    email=user_data['email'],
                    fam=user_data['fam'],
                    name=user_data['name'],
                    otc=user_data.get('otc', ''),
                    phone=user_data['phone']
                )
                db.session.add(user)
                db.session.flush()  # Чтобы получить id пользователя

            # 2. Создаем координаты
            coord = Coord(
                latitude=data['coords']['latitude'],
                longitude=data['coords']['longitude'],
                height=data['coords']['height']
            )
            db.session.add(coord)
            db.session.flush()

            # 3. Создаем перевал
            pereval = Pereval(
                beauty_title=data.get('beauty_title', ''),
                title=data['title'],
                other_titles=data.get('other_titles', ''),
                connect=data.get('connect', ''),
                add_time=datetime.strptime(data['add_time'], '%Y-%m-%d %H:%M:%S'),
                user_id=user.id,
                coords_id=coord.id,
                status='new'
            )
            db.session.add(pereval)
            db.session.flush()

            # 4. Добавляем изображения
            for img_data in data['images']:
                image = Image(
                    pereval_id=pereval.id,
                    data=img_data['data'],
                    title=img_data.get('title', '')
                )
                db.session.add(image)

            # 5. Добавляем сложность по сезонам
            level_data = data['level']
            difficulty = Difficulty(
                pereval_id=pereval.id,
                winter=level_data.get('winter', ''),
                summer=level_data.get('summer', ''),
                autumn=level_data.get('autumn', ''),
                spring=level_data.get('spring', '')
            )
            db.session.add(difficulty)

            # Сохраняем все изменения
            db.session.commit()
            logger.info(f"Pereval added successfully with id: {pereval.id}")

            return True, "Отправлено успешно", pereval.id

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error: {str(e)}")
            return False, f"Ошибка подключения к базе данных: {str(e)}", None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error: {str(e)}")
            return False, f"Внутренняя ошибка сервера: {str(e)}", None