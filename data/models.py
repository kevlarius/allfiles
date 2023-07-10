import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class File(Base):
    __tablename__ = "file"

    id = db.Column(
        db.Integer(), db.Identity(always=False), primary_key=True, unique=True
    )
    name = db.Column(db.String, nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    # type = db.Column(db.String, nullable=True)
