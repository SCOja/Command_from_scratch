import redis


class RedisDB:
    def __init__(self, port):
        self.port = port
        self.client = redis.Redis(port=self.port)

    def data_to_get(self):
        value = self.client.get('surname')
        result = {'surname': value}
        return result

    def update_data(self, data):
        result = self.client.mset(data)
        if result is None:
            raise ValueError
