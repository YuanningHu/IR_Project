__author__ = 'tianzhichen'
settings_body = {"settings": {
    "analysis": {
        "filter": {
            "english_stop": {
                # use standard stop words "_english_"
                "type": "stop",
                "stopwords": "_english_"
            },
            "english_stemmer": {
                # user standard english stammer
                "type": "stemmer",
                "language": "english"
            }
        },
        "analyzer": {
            "review_analyzer": {
                # user standard tokenizer and three filters below
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "english_stemmer"
                ]
            }
        }
    }
},
    "mappings": {
           "review": {
               "properties": {
                   #TODO: ADD ANALYZERS HERE


               }
        }
    }
}