"""Module with base database model mixin"""

import os
from typing import List, Optional

from flask import current_app
from flask_sqlalchemy import BaseQuery, Pagination
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from shop.db import db


class BaseModelMixin(db.Model):
    """
    Class with base functions for database models
    """
    __abstract__ = True

    @classmethod
    def get_all(cls) -> List:
        return cls.query.all()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise err

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    def delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise err

    @classmethod
    def delete_all(cls):
        for instance in cls.get_all():
            instance.delete()

    @classmethod
    def update(cls, _id, **kwargs) -> None:
        try:
            cls.query.filter_by(id=_id).update(kwargs)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            raise err

    @classmethod
    def get(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        return instance

    @classmethod
    def get_random(cls):
        return cls.query.order_by(func.random()).first()

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if not instance:
            instance = cls.create(**kwargs)
        return instance

    @classmethod
    def filter(cls, **kwargs):
        kwargs = {field: value for field, value in kwargs.items() if value is not None}
        return cls.query.filter_by(**kwargs)

    @classmethod
    def get_pagination(cls, page: int = 1, query: Optional[BaseQuery] = None, paginate_by: int = None) -> Pagination:
        if query is None:
            query = cls.query
        return query.paginate(page, paginate_by or cls.PAGINATE_BY, False)

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class PictureHandleMixin:
    def update_image_file(self, new_image_file: str) -> None:
        if self.image_file != new_image_file:
            self._delete_image_file()
            self.image_file = new_image_file
            self.save()

    def _delete_image_file(self) -> None:
        if self.image_file != self.DEFAULT_IMAGE:
            image_path = os.path.join(
                current_app.root_path,
                'static',
                self.image_file,
            )
            os.remove(image_path)

    def delete(self) -> None:
        self._delete_image_file()
        return super().delete()
