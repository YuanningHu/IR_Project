__author__ = 'tianzhichen'
import json, copy
from elasticsearch import Elasticsearch
import math


es = Elasticsearch()
def q_mw(string, verbose = True, star_cut_off = -1, usfellness_cut_off = -1 ):
    search_body = {
        "query":{
        "filtered":{
            "filter": {
                "and": [{"range": {
                    "stars": {
                        "from": star_cut_off
                    }
                }}, {"range": {
                    "usefulness": {
                        "from": usfellness_cut_off,
                        "to": 100
                    }
                }}]
            },
            "query":{"query_string": {
                     #use query_string to retrieve strings, fields are specified.
                        "fields": ["text"],
                         "query": string,
                        }
                     }
                 }
            },
            "highlight": {
                "fields": {
                # get at most 5 retrieved fragments
                    "text": {"fragment_size": 100, "number_of_fragments": 5}
                }
            }
        }

    #add size field to choose max reviews to return. default is 10
    rt = es.search(index='i_reviews', body = search_body, size = 1000)
    f = open('query_result.txt', 'w')
    json.dump(rt, f, indent=4, separators=(',', ': '))
    f.close()
    if verbose:
        print_summary(rt)
        #print avg_user_rating(rt)
    return rt

def print_summary(rt, num = 10):
    #print the results.
    print("============================")
    print("total hits: "+str(rt["hits"]["total"]))
    for index, i in enumerate(rt["hits"]["hits"]):
        if index < num:
            print("rank: " + str(index+1))
            #print("title: "+ i["_source"]["title"])
            print("_score: " + str(i["_score"]))
            for j in i["highlight"].keys():
                print(j, i["highlight"][j])
            print('\n')

__author__ = 'Michael Yu'
#get the average rating for each business based on all reviews
#currently returns dictionary of businesses and the rating information. --can be changed later--
def avg_user_rating(rt):
    reviews = {}
    #sums up all the ratings
    for rev in rt["hits"]["hits"]:
        bus_id = rev['_source']['business_id']
        rating = rev['_source']['stars']
        if not reviews.has_key(bus_id):
            reviews[bus_id] = {'total_ratings': rating, 'num_ratings': 1}
        else:
            reviews[bus_id]['total_ratings'] += rating
            reviews[bus_id]['num_ratings'] += 1
    #finds the average of the reviews
    for bus in reviews:
        reviews[bus]['avg_rating'] = reviews[bus]['total_ratings']/float(reviews[bus]['num_ratings'])
        reviews[bus]['logged_avg_rating'] = math.log(reviews[bus]['total_ratings'])*(reviews[bus]['total_ratings'] / float(reviews[bus]['num_ratings']))
        print reviews[bus]
    return reviews


def reviewFilter_votes(rt, lowerBorder = 0):
    rtCopy = copy.deepcopy(rt)
    newHits = []
    for hit in rtCopy['hits']['hits']:
        vote = hit['_source']['votes']
        if vote['funny']+vote['useful']+vote['cool'] >= lowerBorder:
            newHits.append(hit)
    rtCopy['hits']['hits'] = newHits

    print 'Reviews Filtered by Votes Greater or Equal to', lowerBorder
    print_summary(rtCopy)

    return rtCopy
                 

# TODO: filter out reviews by ratings: ( lucy )
def reviewFilter_stars(rt, lowerBorder = 0, upperBorder = 5):
    rtCopy = copy.deepcopy(rt)
    newHits = []
    for hit in rtCopy['hits']['hits']:
        if hit['_source']['stars'] >= lowerBorder and hit['_source']['stars'] <= upperBorder:
            newHits.append(hit)
    rtCopy['hits']['hits'] = newHits

    print 'Reviews Filtered by Business Stars from', lowerBorder, 'to', upperBorder
    print_summary(rtCopy)
    return rtCopy
    #Others:
            # TODO: weight the ratings by  5 / (average user rating): (average rating is available) (chen)
            # if the rating is larger than the user's average rating, give the rating more weight to increase scores
            # if the rating is less than the users's average rating, give the rating more weight to subtract scores
            # TODO: give people who rate more often a little bit more weight (chen)

            # TODO: noise tunnel to retrieve the correct word # language fix model
            # TODO: rank restaurants by distance./ Optional
            # TODO: INTERFACE


def search_combined(query, star_cut_off = 0, usfellness_cut_off = 0):
    rt = q_mw('good',True, star_cut_off, usfellness_cut_off)
    avg_user_rating(rt)

if __name__ == '__main__':
    search_combined("good", star_cut_off=0, usfellness_cut_off=0)




