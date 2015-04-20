__author__ = 'tianzhichen'
import json
from elasticsearch import Elasticsearch
from settings import settings_body

class Review(object):
    def __init__(self,review_id):
        self.review_id = review_id

def data_convert(jsonfilename = 'yelp_academic_dataset.json'):
    yelp_dataset_file = open(jsonfilename,'r')

    yelp_users_file = open('yelp_users_file.json','w')
    yelp_reviews_file = open('yelp_reviews_file.json', 'w')
    yelp_businesses_file = open('yelp_businesses_file.json', 'w')

    yelp_users_dict = {}
    yelp_reviews_dict = {}
    yelp_businesses_dict = {}
    for line in yelp_dataset_file:
        a = json.loads(line)
        if a['type'] == 'user':
            yelp_users_dict[a['user_id']] = a

        if a['type'] == 'review':
            yelp_reviews_dict[a['review_id']] = a

        if a['type'] == 'business':
            yelp_businesses_dict[a['business_id']] = a
    json.dump(yelp_users_dict, yelp_users_file)
    json.dump(yelp_reviews_dict, yelp_reviews_file)
    json.dump(yelp_businesses_dict, yelp_businesses_file)
    yelp_users_file.close()
    yelp_reviews_file.close()
    yelp_businesses_file.close()


def bulkload_data(type, json_filename,num = 100,):

    f = open(json_filename,'r')
    data_dict = json.load(f)
    list = []
    for id, novel in enumerate(data_dict.keys()):
        # put actions and data in the list
        action = {"create": {"_index": "i_reviews", "_type": type , "_id": str(id)}}
        list.append(action)
        data = data_dict[novel]
        list.append(data)
        # for every num files, bulk load them to server
        if id % num == 0 or id == (len(data_dict.keys())-1):
            es.bulk(list)
            list = []
    return list

if __name__ == '__main__':
    data_convert('small_yelp_dataset.json')

    es = Elasticsearch()

    print settings_body
    es.indices.delete(index='i_reviews')
    es.indices.create(index='i_reviews', body = settings_body)
    # bulkload to the server
    bulkload_data('review', 'yelp_reviews_file.json')
    bulkload_data('users', 'yelp_users_file.json')
    bulkload_data('business', 'yelp_businesses_file.json')


    # TODO:
    # schema:
    # for type review:
        # standard analyze the review_text
        # modify the schema, settings.py

    # TODO:
    #'small_yelp_dataset.json' is only a data for testing and debugging
        # change the data from 'small_yelp_dataset.json' to 'yelp_academic_dataset.json'

