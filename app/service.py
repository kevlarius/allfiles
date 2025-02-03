from typing import Dict, List

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models import Base, ExifData, File, AudioMeta
from app.tools import get_engine


class BaseService:
    """
    Base Service for initialising with a sessions
    """

    model: Base = None

    def __init__(self):
        pass

    def list(self):
        """
        Get a list of objects from the database
        """
        with Session(get_engine()) as session:
            return session.scalars(select(self.model))

    def create(self, data=None):
        if data is None:
            data = {}
        obj = self.model()
        obj.update(data=data)
        return obj

    def bulk_create(self, data: List[Dict] = None):
        if data is None:
            data = []

        objects = []

        for item in data:
            obj = self.model()
            obj.update(data=item)
            objects.append(obj)

        with Session(get_engine()) as session:
            session.add_all(objects)
            session.commit()

    def remove_all(self):
        query = self.list()
        query.delete(synchronize_session=False)

    # def remove_all(self):
    #     self.session.execute(text(f"TRUNCATE TABLE {self.model.__tablename__};"))

    def delete_by_id(self, id_):
        """
        Hard deletes an object by it's id with synchronize_session=False
        :param id:
        :return:
        """
        # we want to list all even inactive
        self.list().filter(self.model.id == id_).delete(
            synchronize_session=False
        )
    #
    # def search_by_fields(self, fields, search_query: str, query: Query = None) -> Query:
    #     """
    #     Uses text search to search by a fields using a search query
    #     :param fields: List of fields to search in the model (usually name,title etc)
    #     :param search_query: The string to search for
    #     :param query: Optional query to use
    #     :return:
    #     """
    #     if not isinstance(fields, list):
    #         fields = [fields]
    #
    #     query = query or self.list()
    #     filter_conditions = []
    #     for field in fields:
    #         filter_conditions.extend(
    #             [
    #                 field.ilike("%{}%".format(term.replace("%", "\\%")))
    #                 for term in search_query.split(" ")
    #             ]
    #         )
    #     return query.filter(or_(*filter_conditions))
    #

    #

    #
    # def create_with_list(self, data=None, user_id=None):
    #     """
    #     Create multiple objects with a list of data
    #
    #     :param data: An array of JSON objects
    #     :param user_id:  Optional parameter to create objects with `user_id`
    #     :return: [self.model]
    #     """
    #     if data is None:
    #         data = []
    #     objs = []
    #
    #     for json_obj in data:
    #         obj = self.model()
    #
    #         if user_id:
    #             obj.user_id = user_id
    #
    #         obj.update(data=json_obj)
    #         self.session.add(obj)
    #         objs.append(obj)
    #
    #     self.session.flush()
    #     # todo optimize this to only call refresh on updated object.
    #     self.session.expire_all()
    #
    #     return objs
    #
    # def from_query_update(self, obj, data):
    #     """
    #     Update an object in the database with the given object
    #
    #     If obj is None, will get ignored.
    #
    #     :param obj: The object to update
    #     :param data: The data to update the object with
    #     :return: The updated object
    #     """
    #     if obj:
    #         for key, value in data.items():
    #             if hasattr(obj, key):
    #                 setattr(obj, key, value)
    #
    #         self.session.flush()
    #         self.session.expire_all()
    #
    #     return obj
    #
    # def update(self, id, data, user_id=None):
    #     """
    #     Update an object in the database with the given ID
    #
    #     :param id: The ID of the object to update
    #     :param data: The data to update the object with
    #     :param str user_id: Optional parameter to filter objects by `user_id`
    #     :return: The updated object
    #     """
    #     obj = self.get(id=id, user_id=user_id)
    #     return self.from_query_update(obj, data)
    #
    # def from_query_update_list(self, obj_list, data):
    #     """
    #     Update objects in query
    #     :param query obj_list: query of list of objects to be updated
    #     :param data: data that should be updated
    #     :return: number of objects updated
    #     """
    #     data = {k: v for k, v in data.items() if hasattr(self.model, k)}
    #     return obj_list.update(data, synchronize_session=False)
    #
    # def from_query_delete(self, obj, soft_delete=True):
    #     """
    #     Delete an object from the database with the given ID
    #     :param obj: query of the object to be deleted
    #     :param soft_delete: Boolean to determine whether to soft or hard delete the object
    #     :return: Boolean stating whether the deletion was a success
    #     """
    #     if obj:
    #         if soft_delete:
    #             # Makes the assumption that the model has an active flag on it.
    #             if hasattr(obj, "active"):
    #                 obj.active = False
    #             if hasattr(obj, "end") and obj.end is None:
    #                 obj.end = datetime.datetime.now().date()
    #             self.session.flush()
    #         else:
    #             obj.delete()
    #
    #         return True
    #
    #     return False
    #
    # def delete(self, id, user_id=None, soft_delete=True):
    #     """
    #     Delete an object from the database with the given ID
    #
    #     :param id: The ID of the object to delete
    #     :param str user_id: Optional parameter to filter objects by `user_id`
    #     :param soft_delete: Boolean to determine whether to soft or hard delete the object
    #     :return: Boolean stating whether the deletion was a success
    #     """
    #     obj = self.get(id=id, user_id=user_id)
    #     return self.from_query_delete(obj, soft_delete)
    #
    # def from_query_delete_list(self, obj_list, soft_delete=True):
    #     """
    #     Delete an object from the database with the given ID
    #     :param obj_list: query of list of objects to be updated
    #     :param soft_delete: Boolean to determine whether to soft or hard delete the object
    #     :return: Boolean stating whether the deletion was a success
    #     """
    #     if obj_list and obj_list.count() > 0:
    #         if soft_delete:
    #             updates = {}
    #             if hasattr(obj_list[0], "end"):
    #                 updates["end"] = datetime.datetime.now()
    #             if hasattr(obj_list[0], "active"):
    #                 updates["active"] = False
    #             if updates:
    #                 obj_list.update(updates, synchronize_session=False)
    #                 self.session.flush()
    #         else:
    #             obj_list.delete(synchronize_session=False)
    #         return True
    #
    #     return False
    #
    # def delete_list(self, soft_delete=True, **kwargs):
    #     """
    #     Delete an object from the database with the given ID
    #     :param soft_delete: Boolean to determine whether to soft or hard delete the object
    #     :param kwargs: contain the params to filter the list by & specifies if the delete is soft delete or not
    #     :return: Boolean stating whether the deletion was a success
    #     """
    #
    #     obj_list = self.list(**kwargs)
    #     return self.from_query_delete_list(obj_list, soft_delete)
    #
    # @staticmethod
    # def paginate(query, page_size, page_number):
    #     """
    #     Return the total count & the paginated response
    #
    #     :param query: query to be paginated
    #     :param page_size: request input page size
    #     :param page_number: request input page number
    #     :return: Paginated result
    #     """
    #
    #     count = query.count()
    #     results = query.limit(page_size).offset(page_size * (page_number - 1))
    #     return results, count
    #
    # @staticmethod
    # def paginate_and_sort(query, page_size, page_number, order_by: tuple):
    #     """
    #     similar to paginate but also sort the results
    #
    #     :param query: query to be paginated
    #     :param page_size: request input page size
    #     :param page_number: request input page number
    #     :param order_by: the list of sort by fields
    #     :return: Paginated result
    #     """
    #
    #     count = query.count()
    #     # from self is needed because query might include a distinct
    #     results = (
    #         query.from_self()
    #         .order_by(*order_by)
    #         .limit(page_size)
    #         .offset(page_size * (page_number - 1))
    #     )
    #
    #     return results, count


class FileService(BaseService):
    model = File

    def get_by_params(self, session, location):
        return session.scalar(select(File).where(File.location == location))

    def get_by_location_begin(self, session, location_begin):
        return session.scalars(select(File).where(File.location.istartswith(location_begin, escape='/')))

    def remove_file(self, file_entry: File):
        if file_entry.exif_id is not None:
            self.session(ExifData).filter(ExifData.id == file_entry.exif_id).delete(synchronize_session=False)
        if file_entry.audio_meta_id is not None:
            self.session(AudioMeta).filter(AudioMeta.id == file_entry.audio_meta_id).delete(synchronize_session=False)
        self.delete_by_id(file_entry.id)

    def remove_file2(self, file_entry: File):
        statements = []
        if file_entry.exif_id is not None:
            statements.append(delete(ExifData).where(ExifData.id == file_entry.exif_id))
        if file_entry.audio_meta_id is not None:
            statements.append(delete(AudioMeta).where(AudioMeta.id == file_entry.audio_meta_id))
        statements.append(delete(File).where(File.id == file_entry.id))
        self.session.execute(statements, execution_options={"synchronize_session": False})


class ExifService(BaseService):
    model = ExifData


class AudioMetaService(BaseService):
    model = AudioMeta
