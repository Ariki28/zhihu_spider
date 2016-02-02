from model.image_collection import ImageCollection
from model.search_record import SearchRecord
import requests
from BeautifulSoup import BeautifulSoup
from time import sleep
from bson import ObjectId


all_items = list(SearchRecord.col.find())
for i in all_items:
    url = i[SearchRecord.Field.url]
    header = {'Referer':url,'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Host': 'www.zhihu.com'
    }
    index = url.find('www')
    if index >= 0:
        url = 'https://' + url[index:]
    else:
        continue
    r = requests.get(url, headers=header)
    soup=BeautifulSoup(r.content)
    soup.findAll('div', {'class': 'zm-editable-content clearfix'})
    div_items=soup.findAll('div', {'class': 'zm-editable-content clearfix'})
    result = []
    for i in div_items:
        imageList = i.findAll('img')
        for image in imageList:
            find_item = image.get('data-actualsrc')
            if find_item:
                result.append(find_item)
    find_img_col = ImageCollection.col.find_one({'url': url})
    if find_img_col:
        img_list = find_img_col.get(ImageCollection.Field.imagesList, [])
        old_set = set(img_list)
        new_set = set(result)
        if len(new_set - old_set) > 0:
            ImageCollection.col.update({'url': url}, {
                '$set': {
                    ImageCollection.Field.imagesList: list(old_set.union(new_set))
                }
            })
    else:
        ImageCollection.col.insert({
            '_id': str(ObjectId()),
            ImageCollection.Field.url: url,
            ImageCollection.Field.imagesList: result
        })
    sleep(0.5)