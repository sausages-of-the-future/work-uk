class Order():

    type_uri = None
    data = {}

    def to_dict(self):
        result = {}
        result['type_uri'] = self.type_uri
        return result

    @classmethod
    def from_dict(cls, data):
        order = Order()
        order.type_uri = data['type_uri']
        return order
