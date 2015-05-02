import json, math, re, nltk
from elasticsearch import Elasticsearch

from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import *
from nltk.corpus import stopwords
from sets import Set

es = Elasticsearch()
tokenizer = RegexpTokenizer(r'\w+')
stop_list = stopwords.words('english')
stemmer = PorterStemmer()

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

def normalizeText(revObjTest):
    #get elastic search object for review Id
    tokenizedText = []
    
    #iterate for all reviews corresponding to id
    for review in revObjTest['hits']['hits']:
        doc = review['_source']['text']
        tokenTList = tokenizer.tokenize(doc)
        lowerCase = [w.lower() for w in tokenTList]
        stopRemoveList = [w for w in lowerCase if w not in stop_list]
        stemmedWords = [stemmer.stem(w) for w in stopRemoveList]
        tokenizedText.append(stemmedWords)
    
    return tokenizedText

def getCollectionSize(collDict):
    count = 0 
    for term in collDict.keyset():
        count = collDict[term] + 1

    return count

def createCollectionDict(tokeRevList):
    wordList = []
    for doc in tokeRevList:
        for word in doc:
            wordList.append(word)

    setWords = set(wordList)
    colDict = {}
    for item in setWords:
        colDict[item] = 0

    for doc in tokeRevList:
        for word in doc:
            colDict[word] = colDict[word] + 1

    return colDict

def createDocDict(docList):
    docDict = {}
    for word in docList:
        docDict[word] = 0
    for word in docList:
        docDict[word] = docDict[word] + 1

    return docDict

def normalize_query(query):
    tokenTList = tokenizer.tokenize(query)
    lowerCase = [w.lower() for w in tokenTList]
    stopRemoveList = [w for w in lowerCase if w not in stop_list]
    stemmedWords = [stemmer.stem(w) for w in stopRemoveList]

    return stemmedWords

def getCollSize(collDict):
    size = 0
    for term in collDict.keys():
        size += collDict[term]

    return size

def getRevCollScore(collDict, collSize, docList, query, lamda):
    queryNorm = normalize_query(query)

    cfTermList = []
    dfTermList = []
    docDict = createDocDict(docList)
    docLen = len(docList)
    
    for term in queryNorm:
        if term not in collDict.keys():
            cfTermList.append(0)
        else:
            cfTermList.append(collDict[term])
        if term not in docDict.keys():
            dfTermList.append(0)
        else:
            dfTermList.append(docDict[term])

    score = 0
    i = 0
    for term in queryNorm:
        score += math.log(lamda*dfTermList[i]/docLen + (1 - lamda)*cfTermList[i]/collSize)
        
    return score            

def getScoreRevList(tokeRevList, collDict, lamda, query):
    collSize = getCollSize(collDict)
    docScoreTuple = []
    i = 0
    for doc in tokeRevList:
        score = getRevCollScore(collDict, collSize, doc, query, lamda)
        docScoreTuple.append((i, score))
        i +=1

    docScoreTuple = sorted(docScoreTuple, key=lambda tup: tup[1], reverse = True)
    topThree = []
    count = 0
    for index, score in docScoreTuple:
        topThree.append(index)
        count += 1
        if count > 2:
            break
    return topThree

def getReviewText(reviewObj, scoreList):
    revText = []
    for index in scoreList:
        revText.append(reviewObj['hits']['hits'][index]['_source']['text'])
    return revText

#review dict
def get_top_3_rev_text(reviewObj, query):
    #businessId  = reviewObj['hits']['hits'][0]['_source']['business_id']
    #reviewObj = get_rev_Bus_Id(businessId) #'q-QYas8qfOvVas0If24pvg'
    tokeRevList = normalizeText(reviewObj)
    collDict = createCollectionDict(tokeRevList)
    score = getScoreRevList(tokeRevList, collDict, 0.7, query) #"pizza student"
    top3Revs = getReviewText(reviewObj, score)

    return top3Revs


#test
reviewObj = get_rev_Bus_Id('q-QYas8qfOvVas0If24pvg')
top3Revs = get_top_3_rev_text(reviewObj, "pizza student")
#for rev in top3Revs:
#    print rev


    
