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

    @staticmethod
    def get_pereval_by_id(pereval_id):
        """
        Получение информации о перевале по ID
        Возвращает: (success: bool, result: dict or error message)
        """
        try:
            pereval = Pereval.query.get(pereval_id)

            if not pereval:
                return False, f"Pereval with id {pereval_id} not found"

            # Формируем результат
            result = {
                "id": pereval.id,
                "beauty_title": pereval.beauty_title,
                "title": pereval.title,
                "other_titles": pereval.other_titles,
                "connect": pereval.connect,
                "add_time": pereval.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                "status": pereval.status,
                "user": {
                    "email": pereval.user.email,
                    "fam": pereval.user.fam,
                    "name": pereval.user.name,
                    "otc": pereval.user.otc,
                    "phone": pereval.user.phone
                },
                "coords": {
                    "latitude": float(pereval.coord.latitude),
                    "longitude": float(pereval.coord.longitude),
                    "height": pereval.coord.height
                },
                "level": {
                    "winter": pereval.difficulty.winter if pereval.difficulty else "",
                    "summer": pereval.difficulty.summer if pereval.difficulty else "",
                    "autumn": pereval.difficulty.autumn if pereval.difficulty else "",
                    "spring": pereval.difficulty.spring if pereval.difficulty else ""
                },
                "images": [
                    {
                        "data": img.data,
                        "title": img.title
                    } for img in pereval.images
                ]
            }

            return True, result

        except Exception as e:
            logger.error(f"Error getting pereval by id {pereval_id}: {str(e)}")
            return False, f"Database error: {str(e)}"

    @staticmethod
    def update_pereval(pereval_id, data):
        """
        Обновление перевала (только если статус 'new')
        Возвращает: (success: bool, message: str)
        """
        try:
            pereval = Pereval.query.get(pereval_id)

            if not pereval:
                return False, f"Pereval with id {pereval_id} not found"

            # Проверяем статус
            if pereval.status != 'new':
                return False, f"Cannot update pereval with status '{pereval.status}'. Only 'new' status can be edited"

            # Обновляем поля перевала
            if 'beauty_title' in data:
                pereval.beauty_title = data['beauty_title']
            if 'title' in data:
                pereval.title = data['title']
            if 'other_titles' in data:
                pereval.other_titles = data['other_titles']
            if 'connect' in data:
                pereval.connect = data['connect']
            if 'add_time' in data:
                pereval.add_time = datetime.strptime(data['add_time'], '%Y-%m-%d %H:%M:%S')

            # Обновляем координаты
            if 'coords' in data:
                coord = pereval.coord
                coord.latitude = data['coords'].get('latitude', coord.latitude)
                coord.longitude = data['coords'].get('longitude', coord.longitude)
                coord.height = data['coords'].get('height', coord.height)

            # Обновляем сложность
            if 'level' in data and pereval.difficulty:
                diff = pereval.difficulty
                diff.winter = data['level'].get('winter', diff.winter)
                diff.summer = data['level'].get('summer', diff.summer)
                diff.autumn = data['level'].get('autumn', diff.autumn)
                diff.spring = data['level'].get('spring', diff.spring)

            # Обновляем изображения (удаляем старые, добавляем новые)
            if 'images' in data:
                # Удаляем старые изображения
                Image.query.filter_by(pereval_id=pereval.id).delete()

                # Добавляем новые
                for img_data in data['images']:
                    image = Image(
                        pereval_id=pereval.id,
                        data=img_data['data'],
                        title=img_data.get('title', '')
                    )
                    db.session.add(image)

            pereval.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Pereval {pereval_id} updated successfully")

            return True, "Pereval updated successfully"

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during update: {str(e)}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error during update: {str(e)}")
            return False, f"Internal server error: {str(e)}"

    @staticmethod
    def get_perevals_by_user_email(email):
        """
        Получение списка перевалов пользователя по email
        Возвращает: (success: bool, result: list or error message)
        """
        try:
            user = User.query.filter_by(email=email).first()

            if not user:
                return False, f"User with email {email} not found"

            perevals = []
            for pereval in user.perevals:
                perevals.append({
                    "id": pereval.id,
                    "beauty_title": pereval.beauty_title,
                    "title": pereval.title,
                    "other_titles": pereval.other_titles,
                    "connect": pereval.connect,
                    "add_time": pereval.add_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "status": pereval.status,
                    "coords": {
                        "latitude": float(pereval.coord.latitude),
                        "longitude": float(pereval.coord.longitude),
                        "height": pereval.coord.height
                    },
                    "level": {
                        "winter": pereval.difficulty.winter if pereval.difficulty else "",
                        "summer": pereval.difficulty.summer if pereval.difficulty else "",
                        "autumn": pereval.difficulty.autumn if pereval.difficulty else "",
                        "spring": pereval.difficulty.spring if pereval.difficulty else ""
                    },
                    "images_count": len(pereval.images)
                })

            return True, perevals

        except Exception as e:
            logger.error(f"Error getting perevals for user {email}: {str(e)}")
            return False, f"Database error: {str(e)}"
