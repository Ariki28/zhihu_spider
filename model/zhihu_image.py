# -*- coding: utf-8 -*-
from . import db
from pymongo.collection import Collection


class ZhihuImage(object):
    COL_NAME = 'ZhihuImage'
    col = Collection(db, COL_NAME)
    class Field(object):
        _id = '_id'
        url = 'url'
        update = 'update'
        imagesList = 'imagesList'
        zhihu_type = 'zhihu_type'
    class ZhihuTypeField(object):
        collection  = 1
        question  = 0
