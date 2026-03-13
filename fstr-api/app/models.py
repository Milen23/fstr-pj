from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    fam = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    otc = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    perevals = db.relationship('Pereval', backref='user', lazy=True)


class Coord(db.Model):
    __tablename__ = 'coords'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    height = db.Column(db.Integer, nullable=False)

    perevals = db.relationship('Pereval', backref='coord', lazy=True)


class Pereval(db.Model):
    __tablename__ = 'perevals'

    id = db.Column(db.Integer, primary_key=True)
    beauty_title = db.Column(db.String(100))
    title = db.Column(db.String(100), nullable=False)
    other_titles = db.Column(db.String(255))
    connect = db.Column(db.String(255))
    add_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coords_id = db.Column(db.Integer, db.ForeignKey('coords.id'), nullable=False)

    images = db.relationship('Image', backref='pereval', lazy=True, cascade='all, delete-orphan')
    difficulty = db.relationship('Difficulty', backref='pereval', uselist=False, cascade='all, delete-orphan')


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    pereval_id = db.Column(db.Integer, db.ForeignKey('perevals.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)  # base64
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Difficulty(db.Model):
    __tablename__ = 'difficulties'

    id = db.Column(db.Integer, primary_key=True)
    pereval_id = db.Column(db.Integer, db.ForeignKey('perevals.id'), unique=True, nullable=False)
    winter = db.Column(db.String(10))
    summer = db.Column(db.String(10))
    autumn = db.Column(db.String(10))
    spring = db.Column(db.String(10))