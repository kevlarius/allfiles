import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    def update(self, data):
        """
        Update an object's properties with the dictionary passed in
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class File(Base):
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

    audio_meta_id = db.Column(
        db.Integer,
        db.ForeignKey("audiometa.id", name="audio_meta_id"),
        nullable=True,
        index=True,
    )
    audio_meta = relationship("AudioMeta", foreign_keys=[audio_meta_id], backref="file")


class ExifData(Base):
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


class AudioMeta(Base):
    __tablename__ = "audiometa"

    id = db.Column(
        db.Integer(), db.Identity(always=False), primary_key=True, unique=True
    )
    title = db.Column(db.String, nullable=True)
    artist = db.Column(db.String, nullable=True)
    album = db.Column(db.String, nullable=True)
    album_artist = db.Column(db.String, nullable=True)
    track_number = db.Column(db.String, nullable=True)
    year = db.Column(db.String, nullable=True)
    genre = db.Column(db.String, nullable=True)
    sampling_frequency = db.Column(db.String, nullable=True)
    bit_rate = db.Column(db.String, nullable=True)
    duration = db.Column(db.String, nullable=True)
