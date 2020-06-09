import pymongo


class MongoDb:

    def __init__(self, uri):
        self.uri = uri
        self.client = pymongo.MongoClient(self.uri,
                                          maxPoolSize=50,
                                          wTimeoutMS=2500)
        self.db = self.client.test
        self.collection = self.db['warehouse']

    def data_to_paste(self, data):
        result = self.collection.insert_one(data)
        if result:
            print('Done')

    def data_to_get(self):
        result = self.collection.find_one({'name': 'John'})
        return result

    def correct_data(self, data):
        self.collection.update_one({'name': 'John'},
                                   {'$set': data},
                                   )

    def update_data(self, data):
        self.collection.update_one({'name': 'John'},
                                   {'$set': data}
                                   )
        result = self.collection.find_one({'name': 'John'})
        if result is None:
            raise ValueError
