__author__ = 'tianzhichen'
import json, copy
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
       # print_summary(rt)
        print avg_user_rating(rt)
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
    businesses = {}
    #sums up all the ratings
    for rev in rt["hits"]["hits"]:

        bus_id = rev['_source']['business_id']
        rating = rev['_source']['stars']
        if not businesses.has_key(bus_id):
            businesses[bus_id] = {'num_ratings': 1}
            businesses[bus_id]['total_ratings'] = rating
        else:
            businesses[bus_id]['total_ratings'] += rating
            businesses[bus_id]['num_ratings'] += 1
    #finds the average of the reviews
    for bus in businesses:
        businesses[bus]['avg_rating'] = businesses[bus]['total_ratings']/float(businesses[bus]['num_ratings'])
       # print  businesses[bus]

    #sorts to rank based on highest avg rating
    sorted_businesses= sorted(businesses, key=lambda avg_rating: businesses[avg_rating], reverse = True)
    get_bus_data(sorted_businesses)
    return sorted_businesses


#returns businesses information. Currently only returns a list of businesses names and their yelp url
#@param a list of IDs to return
def get_bus_data(busIDs):
    output_data = []
    bus_data = json.load(open('yelp_businesses_file.json', 'r'))
    for id in busIDs:
        print bus_data[id]['name'] + " : " + bus_data[id]['url']
        store_data = []
        store_data.append(bus_data[id]['name'])
        store_data.append(bus_data[id]['url'])
        output_data.append(store_data)
    return output_data

    #TODO:
    # TODO: Now, we only get 10 results. we need to change the schema to get all results.(m)
    # rank the restaurants:
            # TODO: SORT BUSINESS BY raw counts from elasticsearch results (will)
            
            # by the usefulness of the results.
            # TODO: add up the usefulness of all retrieved result reviews on a restaurant. (will)
            
            # by ratings
            # TODO: average the ratings of all result reviews on a restaurant./ or ratings of the businesses (micheal)
            
            # by distance

# filters:
# TODO: filter out reviews by usefulness: (lucy)
    # usefulness = cool + funny + useful
def reviewFilter_votes(rt, lowerBorder = 0):
    rtCopy = copy.deepcopy(rt)
    newHits = []
    for hit in rtCopy['hits']['hits']:
        vote = hit['_source']['votes']
        if vote['funny']+vote['useful']+vote['cool'] >= lowerBorder:
            newHits.append(hit)
    rtCopy['hits']['hits'] = newHits
    
    #print 'Reviews Filtered by Votes Greater or Equal to', lowerBorder
   # print_summary(rtCopy)
    
    return rtCopy
                 

# TODO: filter out reviews by ratings: ( lucy )
def reviewFilter_stars(rt, lowerBorder = 0, upperBorder = 5):
    rtCopy = copy.deepcopy(rt)
    newHits = []
    for hit in rtCopy['hits']['hits']:
        if hit['_source']['stars'] >= lowerBorder and hit['_source']['stars'] <= upperBorder:
            newHits.append(hit)
    rtCopy['hits']['hits'] = newHits
    

   # print 'Reviews Filtered by Business Stars from', lowerBorder, 'to', upperBorder
  #  print_summary(rtCopy)
    

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

if __name__ == '__main__':
    rt = q_mw('hot dog')
   ## print
  #  reviewFilter_votes(rt, 100)
  #  print
   # reviewFilter_stars(rt, 2, 3)


