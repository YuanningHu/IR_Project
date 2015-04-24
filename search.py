__author__ = 'tianzhichen'
import json
from elasticsearch import Elasticsearch


es = Elasticsearch()
def q_mw(string, verbose = True):
    search_body = {"query":
                       {
                        "query_string": {
                            #use query_string to retrieve strings, fields are specified.
                           "fields": ["text"],
                            "query": string,
                           }
                       },
                    "highlight": {
                        "fields": {
                            #get at most 5 retrieved fragments
                            "text": {"fragment_size": 100, "number_of_fragments": 5}
                    }
                }
            }
    #add size field to choose max reviews to return. default is 10
    rt = es.search(index='i_reviews', body = search_body, size = 100000)
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
        print reviews[bus]
    return reviews

    #TODO:
    # TODO: Now, we only get 10 results. we need to change the schema to get all results.(m)
    # rank the restaurants:
            # TODO: SORT BUSINESS BY raw counts from elasticsearch results (will)
            # by the usefulness of the results.
            # TODO: add up the usefulness of all retrieved result reviews on a restaurant. (will)
            # by ratings
            # TODO: average the ratings of all result reviews on a restaurant./ or ratings of the businesses (micheal)
            # by distance
    # fitlers:
            # TODO: filter out reviews by usefulness: (lucy)
                # usefulness = cool + funny + usefull
            # TODO: filter out reviews by ratings: ( lucy )
    #Others:
            # TODO: weight the ratings by  5 / (average user rating): (average rating is available) (chen)
            # TODO: give people who rate more often a little bit more weight (chen)



            # TODO: noise tunnel to retrieve the correct word
            # TODO: rank restaurants by distance./ Optional
            # TODO: INTERFACE

if __name__ == '__main__':
    q_mw('good')



