import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    name = db.Column(db.String, nullable=False, index=True)
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
    # CRC32
    crc32 = db.Column(db.String, nullable=True, index=True)
    # SHA1
    sha1 = db.Column(db.String, nullable=True, index=True)

    exif_id = db.Column(
        db.Integer,
        db.ForeignKey("exif.id", name="exif_id"),
        nullable=True,
        index=True,
    )
    exif = relationship("ExifData", foreign_keys=[exif_id], backref="file")


class ExifData(Base, UpdateMixin):
    __tablename__ = "exif"

    id = db.Column(
        db.Integer(), db.Identity(always=False), primary_key=True, unique=True
    )
    version = db.Column(db.String, nullable=True)

    image_width = db.Column(db.Integer, nullable=True)
    image_height = db.Column(db.Integer, nullable=True)

    camera_producer = db.Column(db.String, nullable=True, index=True)
    camera_model = db.Column(db.String, nullable=True, index=True)
    iso = db.Column(db.String, nullable=True)
    # datetime when image was taken
    datetime_original = db.Column(db.DateTime, nullable=True)

    gps_latitude = db.Column(db.String, nullable=True)
    gps_longitude = db.Column(db.String, nullable=True)
    gps_altitude = db.Column(db.String, nullable=True)

    exposure_time = db.Column(db.String, nullable=True)
    f_number = db.Column(db.String, nullable=True)
    focal_length = db.Column(db.String, nullable=True)
    focal_length_in_35mm_film = db.Column(db.String, nullable=True)
    orientation = db.Column(db.String, nullable=True)
    software = db.Column(db.String, nullable=True)
    max_aperture_value = db.Column(db.String, nullable=True)
