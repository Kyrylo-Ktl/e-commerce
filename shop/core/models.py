"""Module with base database model mixin"""

from typing import List, Optional

from flask_sqlalchemy import BaseQuery, Pagination
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
    def get_pagination(cls, page: int = 1, query: Optional[BaseQuery] = None) -> Pagination:
        if query is None:
            query = cls.query
        return query.paginate(page, cls.PAGINATE_BY, False)

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
