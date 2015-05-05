__author__ = 'tianzhichen'
import json, copy
from elasticsearch import Elasticsearch
import Tkinter

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
    if verbose:
        print_summary(rt)
        #print avg_user_rating(rt)
    return str(rt)

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
def avg_user_rating(rt,ranking_method):
    businesses = {}
    #sums up all the ratings
    for rev in rt["hits"]["hits"]:
        bus_id = rev['_source']['business_id']
        rating = rev['_source']['stars']
        highlit = rev['highlight']['text'][0]
        if not businesses.has_key(bus_id):
            businesses[bus_id] = {'total_ratings': rating, 'num_ratings': 1, "highlights" : [highlit]}

        else:
            businesses[bus_id]['total_ratings'] += rating
            businesses[bus_id]['num_ratings'] += 1
            businesses[bus_id]["highlights"].append(highlit)

    #finds the average of the reviews
    for bus in businesses:
        businesses[bus]['avg_rating'] = businesses[bus]['total_ratings']/float(businesses[bus]['num_ratings'])
        businesses[bus]['logged_avg_rating'] = math.log(businesses[bus]['total_ratings'])*(businesses[bus]['total_ratings'] / float(businesses[bus]['num_ratings']))

    if ranking_method == 'loggedstar':
        sorted_business = sorted(businesses, key = lambda obje: businesses[obje]["logged_avg_rating"],reverse = True)
    else:
        sorted_business = sorted(businesses, key=lambda obje: businesses[obje]["avg_rating"], reverse=True)

    businesses_with_highlights = []
    for bus in sorted_business:
        print (bus,businesses[bus]["highlights"])
        businesses_with_highlights.append((bus,businesses[bus]["highlights"]))
    return businesses_with_highlights


def present_rt_sorted_businesses(sorted_business,number = 10,high_lights_number = 3):
    f_out = open('present.txt','w')
    f = open("yelp_businesses_file.json",'r')
    buses_dict = json.load(f)

    for i in range(number):
        bus = buses_dict[sorted_business[i][0]]
        print '==========='+ str(i+1) +'==========='
        print 'Restaurant: ',bus["name"]
        print '------------------------------------'
        print bus["full_address"]
        print '  -----------  reviews  ------------'
        for j in range(high_lights_number):
            if j <= len(sorted_business[1]) - 1:
                print sorted_business[i][1][j]
        print ''

        f_out.write('==========='+ str(i+1) +'===========\n')
        f_out.write('Restaurant: '+ bus["name"].encode('utf-8') +'\n')
        f_out.write( '------------------------------------\n')
        f_out.write( bus["full_address"] + '\n')
        f_out.write( ' -----------  reviews  ------------\n')
        for j in range(high_lights_number):
            if j <= len(sorted_business[1]) - 1:
                f_out.write( sorted_business[i][1][j] + '\n')
        f_out.write('\n')
    f.close()

def get_highlights(query_string, bus_id):
    f_bus = open("yelp_businesses_file.json", 'r')
    f_review = open("yelp_reviews_file.json",'r')
    buses_dict = json.load(f_bus)
    revs_dict = json.load(f_review)

    f_bus.close()
    f_review.close()




# def get_key_field():



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


def search_combined(query, star_cut_off = 0,
                    usfellness_cut_off = 0,
                    sorted_number = 10,
                    highlights = 3, ranking_method = 'star'):
    # methods : star, loggedstar,

    rt = q_mw('good',False, star_cut_off, usfellness_cut_off)
    if ranking_method == 'star':
        sorted_businesses = avg_user_rating(rt)
    elif ranking_method == 'loggedstar':

    present_rt_sorted_businesses(sorted_businesses,sorted_number,highlights)

if __name__ == '__main__':
    rt = q_mw('paella')
   ## print
  #  reviewFilter_votes(rt, 100)
  #  print
   # reviewFilter_stars(rt, 2, 3)
    search_combined("good", star_cut_off=0, usfellness_cut_off=0)



    print
    #reviewFilter_votes(rt, 100)
    print
    #reviewFilter_stars(rt, 2, 3)


