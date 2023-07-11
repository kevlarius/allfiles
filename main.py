import argparse
import binascii
import hashlib
import http
import io
import logging
import os.path
from datetime import datetime

from exif import Image

from app.service import ExifService, FileService
from app.tools import ExifGetter, calculate_hash, close_session, get_session

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class FolderProcessor:
    # count of files to flush to DB
    # (to make bulk insert operation instead of inserting files by one )
    BUFFER_SIZE = 100

    def __init__(self, folder):
        self.folder = folder
        self._session = get_session()
        self.file_service = FileService(self._session)
        self.exif_service = ExifService(self._session)
        self._files_buffer = []

    def process(self):
        self._check_folder()
        self._remove_files_from_db()
        self._remove_exif_from_db()
        processed = 0
        try:
            for file_path in self._file_path_generator():
                self._process_file(file_path)
                processed += 1
        except KeyboardInterrupt:
            logger.info("Processing is interrupted.")
            self._finish_processing()
        except Exception as e:
            self._session.rollback()
            close_session(self._session)
            logger.error(str(e))
            raise e

        # flush buffer for case when it is not full
        self._finish_processing()
        logger.info(f"Processed: {processed} files.")

    def _remove_files_from_db(self):
        self.file_service.remove_all()

    def _remove_exif_from_db(self):
        self.exif_service.remove_all()

    def _check_folder(self):
        if not os.path.exists(self.folder):
            raise Exception(f"'{self.folder}' does not exist.")

        if not os.path.isdir(self.folder):
            raise Exception(f"'{self.folder}' is not a directory.")

    def _buffer_is_full(self):
        return len(self._files_buffer) == self.BUFFER_SIZE

    def _process_file(self, full_file_path):
        file_name = os.path.basename(full_file_path)
        logger.debug(f"Processing file: {file_name}")

        basename, extension = os.path.splitext(file_name)
        extension = str.lower(extension[1:]) if extension else None
        data = {
            "name": file_name,
            "basename": basename,
            "extension": extension,
            "location": full_file_path,
            "size": os.path.getsize(full_file_path),
            "created_at": datetime.fromtimestamp(os.path.getctime(full_file_path)),
            "edited_at": datetime.fromtimestamp(os.path.getmtime(full_file_path)),
        }
        self._add_hash_sums(full_file_path, data)
        if self._file_can_contain_exif(extension):
            self._add_exif_metadata(full_file_path, data)
        self._files_buffer.append(data)

        # flush to DB if buffer is full
        if self._buffer_is_full():
            self._flush()

    def _file_path_generator(self):
        for dir_path, _, filenames in os.walk(self.folder, topdown=False):
            for filename in filenames:
                full_file_path = os.path.abspath(os.path.join(dir_path, filename))
                yield full_file_path

    def _finish_processing(self):
        self._flush()
        self._session.commit()
        close_session(self._session)

    def _flush(self):
        if not self._files_buffer:
            return

        logger.debug(f"Flushing data to DB. Items to flush: {len(self._files_buffer)}")
        self.file_service.bulk_create(data=self._files_buffer)
        self._files_buffer = []

    @staticmethod
    def _add_hash_sums(full_file_path, file_data):
        sha1, crc32 = calculate_hash(full_file_path)
        file_data["crc32"] = crc32
        file_data["sha1"] = sha1

    def count_files(self):
        total = 0
        for dir_path, _, filenames in os.walk(self.folder, topdown=False):
            total += len(filenames)
        return total

    @staticmethod
    def _file_can_contain_exif(extension):
        return extension in ("jpg", "jpeg")

    def _add_exif_metadata(self, full_file_path, data):
        exif_data = ExifGetter(full_file_path).get_exif_data()
        if exif_data:
            exif_entry = self.exif_service.create(exif_data)
            data["exif_id"] = exif_entry.id


def run_app(folder):
    processor = FolderProcessor(folder)
    processor.process()
    # files_count = processor.count_files()
    # data = get_exif_data("D:\\DCIM\\100NIKON\\DSCN2107.JPG")
    # print(data)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        "Files processing tool",
        usage="python main.py <PATH>",
        description="Tool to process a folder with files and save metadata to database",
    )
    arg_parser.add_argument("path")
    options = arg_parser.parse_args()
    run_app(options.path)
