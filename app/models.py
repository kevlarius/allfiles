import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UpdateMixin:
    """
    Provides convenience method for updating a Python object with a dictionary
    """

    def update(self, data):
        """
        Update an object's properties with the dictionary passed in
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class File(Base, UpdateMixin):
    __tablename__ = "file"

    id = db.Column(
        db.Integer(), db.Identity(always=False), primary_key=True, unique=True
    )
    # file's name full (with extension)
    name = db.Column(db.String, nullable=False)
    # file's base name (without extension)
    basename = db.Column(db.String, nullable=False)
    # file's extension (e.g.: "txt")
    extension = db.Column(db.String, nullable=True)
    # full path to file
    location = db.Column(db.String, nullable=False)
    # size in bytes
    size = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    edited_at = db.Column(db.DateTime, nullable=False)
