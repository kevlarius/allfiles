import argparse
import binascii
import enum
import hashlib
import http
import io
import logging
import os.path
import time
from datetime import datetime

from flask import Flask
from sqlalchemy.orm import Session

from app.service import ExifService, FileService, AudioMetaService
from app.tools import ExifGetter, calculate_hash, AudioMetaGetter, get_engine

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


app = Flask(__name__)


@app.route('/')
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/<name>")
def hello(name):
    return f"Hello, {name}!"


class FolderProcessor:
    # count of files to flush to DB
    # (to make bulk insert operation instead of inserting files by one )
    BUFFER_SIZE = 100
    # 256 MB
    MAX_HASH_SIZE = 256 * 1024 * 1024

    def __init__(self, folder, clear_db_required=False):
        self._clear_db_required = clear_db_required
        if '/' in folder:
            folder = folder.replace('/', '\\')
        self.folder = folder
        self._total_files = 0
        self.file_service = FileService()
        self.exif_service = ExifService()
        self.audio_meta_service = AudioMetaService()
        self._files_buffer = []

    def _print_progress(self, processed):
        percent = (processed / self._total_files) * 100
        print(f"\rProcessed: {processed}/{self._total_files} ({percent} %)    ", end="", flush=True)

    def process(self):
        self._check_folder()
        self._total_files = self.count_files()

        if self._clear_db_required:
            self._clear_db()

        processed = 0
        logger.info(f"Found: {self._total_files} to process. Start processing.")
        try:
            for file_path in self._file_path_generator():
                if not self._file_already_in_db(file_path):
                    self._process_file(file_path)
                processed += 1
                self._print_progress(processed)
        except KeyboardInterrupt:
            logger.info("Processing is interrupted.")
            self._finish_processing()
        except Exception as e:
            logger.error(str(e))
            raise e

        # flush buffer for case when it is not full
        self._finish_processing()
        logger.info(f"Processed: {processed} files.")

    def _clear_db(self):
        self._remove_files_from_db()
        self._remove_exif_from_db()
        self._remove_audio_meta_from_db()

    def _remove_files_from_db(self):
        self.file_service.remove_all()

    def _remove_exif_from_db(self):
        self.exif_service.remove_all()

    def _remove_audio_meta_from_db(self):
        self.audio_meta_service.remove_all()

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
        if data["size"] < self.MAX_HASH_SIZE:
            self._add_hash_sums(full_file_path, data)
        if self._file_can_contain_exif(extension):
            self._add_exif_metadata(full_file_path, data)
        elif self._file_can_contain_audio_meta(extension):
            self._add_audio_metadata(full_file_path, data)
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
        logger.info("Counting total files...")
        total = 0
        for dir_path, _, filenames in os.walk(self.folder, topdown=False):
            total += len(filenames)
        logger.info(f"Found: {total} files")
        return total

    @staticmethod
    def _file_can_contain_exif(extension):
        return extension in ("jpg", "jpeg")

    @staticmethod
    def _file_can_contain_audio_meta(extension):
        return extension in ("mp3",)

    def _add_exif_metadata(self, full_file_path, data):
        exif_data = None
        try:
            exif_data = ExifGetter(full_file_path).get_exif_data()
        except Exception as e:
            logger.error(f"Error when getting EXIF for: {full_file_path}:")
            logger.error(f"{e}")

        if exif_data:
            exif_entry = self.exif_service.create(exif_data)
            data["exif"] = exif_entry

    def _add_audio_metadata(self, full_file_path, data):
        audio_meta_data = None
        try:
            audio_meta_data = AudioMetaGetter(full_file_path).get_data()
        except Exception as e:
            logger.error(f"Error when getting audio meta for: {full_file_path}:")
            logger.error(f"{e}")

        if audio_meta_data:
            audio_meta_entry = self.audio_meta_service.create(audio_meta_data)
            data["audio_meta"] = audio_meta_entry

    def _file_already_in_db(self, file_path):
        with Session(get_engine()) as session:
            s = self.file_service.get_by_params(session, location=file_path)
            if s is not None:
                return True
            return False

    def check(self):
        with Session(get_engine()) as session:
            files_in_db = self.file_service.get_by_location_begin(session, self.folder)
            for file_entry in files_in_db:
                if not os.path.exists(file_entry.location):
                    logger.info(
                        f"File '{file_entry.location}' does not exist. Removing entry in DB.")
                    session.delete(file_entry)
            session.commit()


class Mode(enum.Enum):
    PARSE = "PARSE"
    CHECK = "CHECK"


def run_app(mode, folder):
    processor = FolderProcessor(folder)
    if mode == Mode.PARSE.value:
        logger.info("Parsing mode")
        processor.process()
    elif mode == Mode.CHECK.value:
        logger.info("Check mode")
        processor.check()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        "Files processing tool",
        usage="python main.py <MODE> <PATH>",
        description="Tool to process a folder with files and save metadata to database",
    )
    arg_parser.add_argument("mode")
    arg_parser.add_argument("path")
    options = arg_parser.parse_args()
    run_app(options.mode, options.path)
