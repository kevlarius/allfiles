import binascii
import enum
import hashlib
import os
import time
import zlib
from datetime import datetime
from typing import BinaryIO, List, Tuple

from exif import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Date format YYYY:MM:DD HH:mm:ss (e.g.:  "2018:07:22 10:32:25")
DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
DATE_FORMAT_ALT = "%Y/%m/%d %H:%M:%S"


# 128 MB
BUFFER_SIZE = 128 * 1024 * 1024


# calc CRC32 and SHA1 (path must exist)
def calculate_hash(path: str) -> Tuple[str, str]:
    sha1_obj = hashlib.sha1()
    crc32_val = 0

    with open(path, "rb") as file_obj:
        while True:
            data = file_obj.read(BUFFER_SIZE)
            if not data:
                break
            sha1_obj.update(data)
            crc32_val = zlib.crc32(data, crc32_val)

    crc32_hex = format(crc32_val & 0xFFFFFFFF, "08x")
    return sha1_obj.hexdigest(), crc32_hex


def get_database_url():
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS", "postgres")
    return f"postgresql://{db_user}:{db_pass}@localhost:5432/allfiles"


def open_connection(db_url) -> scoped_session:
    created_engine = create_engine(
        url=db_url,
        connect_args={"connect_timeout": 2},
        echo=False,
        pool_size=5,
    )
    session_factory = sessionmaker(bind=created_engine)
    session = scoped_session(session_factory)

    return session


def get_session() -> scoped_session:
    for _ in range(0, 3):
        try:
            return open_connection(get_database_url())
        except Exception as ex:
            print(f"Error {ex}")

    raise Exception("Could not connect to database")


def close_session(session: scoped_session):
    session.expunge_all()
    session.close()
    engine = session.get_bind()
    engine.dispose()


class ExifGetter:
    def __init__(self, image_path):
        self.image_path = image_path
        self.result = dict()

    @staticmethod
    def _get_orientation(image):
        try:
            return image.get("orientation", None)
        except ValueError:
            return None

    @staticmethod
    def _get_image_datetime(image):
        datetime_original_str = image.get(
            "datetime_original", image.get("datetime", None)
        )
        if datetime_original_str:
            date_format = (
                DATE_FORMAT if "/" not in datetime_original_str else DATE_FORMAT_ALT
            )
            try:
                return datetime.strptime(datetime_original_str, date_format)
            except TypeError:
                pass
        return None

    @staticmethod
    def _strip_string(value):
        if value is None:
            return None
        return value.strip()

    @staticmethod
    def _dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
        if coordinates is None or coordinates_ref is None:
            return None
        decimal_degrees = coordinates[0] + coordinates[1] / 60 + coordinates[2] / 3600

        if coordinates_ref == "S" or coordinates_ref == "W":
            decimal_degrees = -decimal_degrees

        return decimal_degrees

    def get_exif_data(self):
        with open(self.image_path, "rb") as image_file:
            image = Image(image_file)
            if not image.has_exif:
                return self.result

            self.result.update(
                {
                    "version": image.get("exif_version"),
                    "image_width": image.get(
                        "pixel_x_dimension", image.get("image_width")
                    ),
                    "image_height": image.get(
                        "pixel_y_dimension", image.get("image_height")
                    ),
                    "camera_producer": self._strip_string(image.get("make")),
                    "camera_model": self._strip_string(image.get("model")),
                    "iso": image.get("photographic_sensitivity"),
                    "datetime_original": self._get_image_datetime(image),
                    "gps_latitude": self._dms_coordinates_to_dd_coordinates(
                        image.get("gps_latitude"), image.get("gps_latitude_ref")
                    ),
                    "gps_longitude": self._dms_coordinates_to_dd_coordinates(
                        image.get("gps_longitude"), image.get("gps_longitude_ref")
                    ),
                    "gps_altitude": image.get("gps_altitude"),
                    # выдержка
                    "exposure_time": image.get("exposure_time"),
                    # диафрагма
                    "f_number": image.get("f_number"),
                    "focal_length": image.get("focal_length"),
                    "focal_length_in_35mm_film": image.get("focal_length_in_35mm_film"),
                    "orientation": self._get_orientation(image),
                    "software": image.get("software"),
                    # светосила
                    "max_aperture_value": image.get("max_aperture_value"),
                }
            )
            return self.result

    @staticmethod
    def _list_all_tags(image):
        for a in dir(image):
            if a.startswith("_"):
                continue
            try:
                print(f"{a}: {getattr(image, a)}")
            except NotImplementedError:
                pass
            except ValueError:
                pass
