# -*- coding: utf-8 -*-
from . import api
from flask import request, jsonify, session, redirect, render_template, abort
from flask.ext.login import (
    login_required,
    login_user,
    logout_user,
    current_user
)
from bson import ObjectId
import json
import requests
from BeautifulSoup import BeautifulSoup
from model.search_record import SearchRecord


@api.route('/zhihu_spider', methods=['GET'])
def spider_zhihu():
    url = request.args.get('url', None)
    header = {'Referer':url,'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Host':'www.zhihu.com'
    }
    if url:
        index = url.find('www')
        if index >= 0:
            url = 'https://' + url[index:]
        else:
            abort(400)
        r = requests.get(url, headers=header)
        soup=BeautifulSoup(r.content)
        if r.status_code == 200:
            find_record = SearchRecord.col.find_one({
                SearchRecord.Field.url: url
            })
            if find_record is None:
                title = soup.find('title').text
                SearchRecord.col.insert_one({
                    '_id': str(ObjectId()),
                    'title': title,
                    'searchCount': 1,
                    'url': url
                })
            else:
                SearchRecord.col.update_one({
                    SearchRecord.Field.url:url},
                    {'$inc':{SearchRecord.Field.searchCount:1}
                })
        soup.findAll('div', {'class':'zm-editable-content clearfix'})
        div_items=soup.findAll('div', {'class':'zm-editable-content clearfix'})
        result = []
        for i in div_items:
            imageList = i.findAll('img')
            for image in imageList:
                find_item = image.get('data-actualsrc')
                if find_item:
                    result.append(find_item)
        return jsonify(stat=1, imageList=result)
    else:
        abort(400)


@api.route('/hot_search', methods=['GET'])
def get_hot_search():
    start =  request.args.get('start', 0, type=int)
    end = request.args.get('end', 15, type=int)
    hot_items = SearchRecord.col.find().sort(
        SearchRecord.Field.searchCount, -1
    ).skip(start).limit(end - start)
    if hot_items.count() == 0:
        return jsonify(stat=1,result=[])
    else:
        result = []
        for i in hot_items:
            result.append({
                'url': i['url'],
                'title': i['title'],
                'count': i['searchCount']
            })
        return jsonify(stat=1,result=result)
