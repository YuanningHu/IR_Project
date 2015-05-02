__author__ = 'tianzhichen'
import json, math, probReview
from elasticsearch import Elasticsearch


es = Elasticsearch()

"""
Note: there's a problem: useful ratings aren't normalized by anything.  Thus the more reviews the larger the sum
of the useful score will be.  There's another problem: all business ids returned are taken into this count- thus for
a given information need less relevant high count reviews will come up higher in the ranking rather than lower use count
documents that pertain more to the given information need.  Example: I searched for pizza and the highest ranked restaurant
did indeed seem popular but it was a bubble tea restaurant and pizza was mentioned only once- it was mentioned in relevance
to getting pizza before getting bubble tea.  How do we weight restuarants more highly that are more relevant to the
information need?
"""
def getUsefulCount(reviewDict, normQuery):
    score = 0
    for busSearch in reviewDict['hits']['hits']:
        score += busSearch['_source']['votes']['useful']
    if score == 0:
        score = 1
    termScore, relDoc = getTermWeight(reviewDict, normQuery)
    if termScore != 0 and relDoc: 
        return score+termScore
    elif termScore != 0 and not relDoc:
        return score*0.5 + termScore
    else:
        return score*0.01

"""
Note: there's a problem: only restaurants with very few reviews come back, as they're more likely not to have lower
star ratings.  How do we weight restuarants that have more reviews more hightly?
"""
def getStarCount(reviewDict, norm):
    stars = 0
    for busSearch in reviewDict['hits']['hits']:
        stars += busSearch['_source']['stars']

    termScore, relDoc = getTermWeight(reviewDict, norm)
    if termScore != 0 and relDoc: 
        return float(stars)/len(reviewDict['hits']['hits']) + math.log(termScore)
    elif termScore != 0 and not relDoc:
        return float(stars)/len(reviewDict['hits']['hits'])*0.75 + math.log(termScore)
    else:
        return float(stars)/len(reviewDict['hits']['hits'])*0.5
    """
    logScore = 0
    if reviewDict['hits']['hits'] <= 1:
        logScore = 1
    else:
        logScore = math.log10(len(reviewDict['hits']['hits']))"""
        
    #return float(stars)/len(reviewDict['hits']['hits'])

def getTermWeight(reviewList, norm):
    #norm = probReview.normalize_query(query)
    score = 0
    relDoc = False
    for docs in reviewList['hits']['hits']:
        doc = docs['_source']['text']
        tokenTList = probReview.tokenizer.tokenize(doc)
        lowerCase = [w.lower() for w in tokenTList]
        stopRemoveList = [w for w in lowerCase if w not in probReview.stop_list]
        stemmedWords = [probReview.stemmer.stem(w) for w in stopRemoveList]
        curr_score = 0
        for term in norm:
            if term in stemmedWords:
                curr_score +=1
        if curr_score == len(norm):
            relDoc = True
            curr_score += len(norm)
        score +=curr_score
    return score/len(reviewList['hits']['hits']), relDoc

def get_rev_Bus_Id(busId):
    search_body = {
        "from" : 0, "size" : 100000,
        "query": {
                        "bool" : {
                        "must" : [ 
                            { "match": { "business_id" : busId } },
                            { "match": { "type" : "review" } }
                            ]
                        }
                    }
                }
    rt = es.search(index='i_reviews', body = search_body)
    return rt


def get_rev_score_busId(resultsDict, query):
    scoreDict = {}
    normQuery = probReview.normalize_query(query)
    for business in result['hits']['hits']:
        busId = str(business['_source']['business_id'])
        busIdResults = get_rev_Bus_Id(busId)
        scoreDict[busId] = getUsefulCount(busIdResults, normQuery)

    scoreTuple = scoreDict.items()
    scoreTuple = sorted(scoreTuple, key=lambda tup: tup[1], reverse = True)
    #threeTuple = getThreeTupleBusId(scoreTuple, resultsDict)

    return scoreTuple

def get_avg_star_busId(result, query):
    starDict = {}
    query = probReview.normalize_query(query)
    for business in result['hits']['hits']:
        busId = str(business['_source']['business_id'])
        busIdResults = get_rev_Bus_Id(busId)
        starDict[busId] = getStarCount(busIdResults, query)

    starTuple = starDict.items()
    starTuple = sorted(starTuple, key=lambda tup: tup[1], reverse = True)

    return starTuple
    
def q_mw(string, verbose = False):
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
    rt = es.search(index='i_reviews', body = search_body)
    f = open('query_result.txt', 'w')
    json.dump(rt, f, indent=4, separators=(',', ': '))
    f.close()
    if verbose:
        print_summary(rt)
    return rt

def searchTextRev(string):
    search_body = {
    "from" : 0, "size" : 100000,
    "query": {
        "query_string": {
            "fields": ["text"],
            "query": string
        }
    }
    }
    rt = es.search(index='i_reviews', body = search_body)
    return rt

def print_summary(rt, num = 100):
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
            

    #TODO:
    # rank the restaurants:
            # by the usefulness of the results. (Will B)
            # TODO: add up the usefulness of all result reviews on a restaurant.
            # by ratings (Will B)
            # TODO: average the ratings of all result reviews on a restaurant.
            # by distance
            # TODO: rank restaurants by distance.

    # fitlers:
            # TODO: filter out reviews by usefulness:
                # usefulness = cool + funny + usefull
            # TODO: filter out reviews by usefulness:
    #Others:
            # TODO: weight the ratings by  5 / (average user rating): (average rating is available)




if __name__ == '__main__':
    result = searchTextRev("lobster bisque")
    busUseTuple = get_rev_score_busId(result, "greek food")
    print busUseTuple

    i = 0
    #businesses ranked by the most useful results
    for item in busUseTuple:
        print item
        i += 1
        if i > 10:
            break

    busStarTuple = get_avg_star_busId(result, "greek food")
    i = 0
    print
    #businesses ranked by avg number of stars
    for item in busStarTuple:
        print item
        i += 1
        if i > 10:
            break


