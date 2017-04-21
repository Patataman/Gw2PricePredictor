import csv
from random import shuffle

class Process():

    def __init__(self, inst_size=5, obj_size=5):
        self.instance_size = inst_size   # nombre of instances for nn
        self.objects_size = obj_size    # number of objects

        self.buy_data = {
            '19727': [],
            '24325': [],
            '24292': [],
            '24344': [],
            '24289': []
        }
        self.sell_data = {
            '19727': [],
            '24325': [],
            '24292': [],
            '24344': [],
            '24289': []
        }

        self.normalize_buy_data = {
            '19727': [],
            '24325': [],
            '24292': [],
            '24344': [],
            '24289': []
        }
        self.normalize_sell_data = {
            '19727': [],
            '24325': [],
            '24292': [],
            '24344': [],
            '24289': []
        }

        self.data_max = {
            '19727': {
                'sell': {
                    'price': 0,
                    'quantity': 0
                },
                'buy': {
                    'price': 0,
                    'quantity': 0
                }
            },
            '24325': {
                'sell': {
                    'price': 0,
                    'quantity': 0
                },
                'buy': {
                    'price': 0,
                    'quantity': 0
                }
            },
            '24292': {
                'sell': {
                    'price': 0,
                    'quantity': 0
                },
                'buy': {
                    'price': 0,
                    'quantity': 0
                }
            },
            '24344': {
                'sell': {
                    'price': 0,
                    'quantity': 0
                },
                'buy': {
                    'price': 0,
                    'quantity': 0
                }
            },
            '24289': {
                'sell': {
                    'price': 0,
                    'quantity': 0
                },
                'buy': {
                    'price': 0,
                    'quantity': 0
                }
            }
        }
        self.data_min = 0

    def load_data(self):
        with open('data/iao_gw') as csvfile:
            reader = csv.DictReader(csvfile)
            reader = list(reader)

            for i in range(len(reader)):
                buy_price_attr = [reader[i+(j*self.objects_size)].get('buy_price') for j in range(self.instance_size+1) if i+(j*self.objects_size) < len(reader)]
                buy_quantity_attr = [reader[i+(j*self.objects_size)].get('buy_cuantity') for j in range(self.instance_size) if i+(j*self.objects_size) < len(reader)]

                if len(buy_price_attr) >= self.instance_size+1:
                    self.buy_data.get(reader[i].get('id')).append({'quantity': buy_quantity_attr, 'price': buy_price_attr[:-1], 'label': buy_price_attr[-1]})

                sell_price_attr = [reader[i+(j*self.objects_size)].get('sell_price') for j in range(self.instance_size+1) if i+(j*self.objects_size) < len(reader)]
                sell_quantity_attr = [reader[i+(j*self.objects_size)].get('sell_quantity') for j in range(self.instance_size) if i+(j*self.objects_size) < len(reader)]

                if len(sell_price_attr) >= self.instance_size+1:
                    self.sell_data.get(reader[i].get('id')).append({'quantity': sell_quantity_attr, 'price': sell_price_attr[:-1], 'label': sell_price_attr[-1]})

                # update max and min
                id = reader[i]['id']
                if int(reader[i]['sell_price']) > self.data_max[id]['sell']['price']:
                    self.data_max[id]['sell']['price'] = int(reader[i]['sell_price'])
                if int(reader[i]['buy_price']) > self.data_max[id]['buy']['price']:
                    self.data_max[id]['buy']['price'] = int(reader[i]['buy_price'])
                if int(reader[i]['sell_quantity']) > self.data_max[id]['sell']['quantity']:
                    self.data_max[id]['sell']['quantity'] = int(reader[i]['sell_quantity'])
                if int(reader[i]['buy_cuantity']) > self.data_max[id]['buy']['quantity']:
                    self.data_max[id]['buy']['quantity'] = int(reader[i]['buy_cuantity'])

    def normalize_data(self):
        for id in self.buy_data:
            for instance in self.buy_data[id]:
                quantities = []
                prices = []

                for quantity in instance['quantity']:
                    value = (int(quantity) - self.data_min)/(self.data_max[id]['buy']['quantity'] - self.data_min)
                    quantities.append(value)
                for price in instance['price']:
                    value = (int(price) - self.data_min)/(self.data_max[id]['buy']['price'] - self.data_min)
                    prices.append(value)

                value_label = (int(instance['label']) - self.data_min)/(self.data_max[id]['buy']['price'] - self.data_min)
                self.normalize_buy_data[id].append({'inputs': quantities + prices, 'outputs': [value_label]})

        for id in self.sell_data:
            for instance in self.sell_data[id]:
                quantities = []
                prices = []

                for quantity in instance['quantity']:
                    value = (int(quantity) - self.data_min)/(self.data_max[id]['sell']['quantity'] - self.data_min)
                    quantities.append(value)
                for price in instance['price']:
                    value = (int(price) - self.data_min)/(self.data_max[id]['sell']['price'] - self.data_min)
                    prices.append(value)

                value_label = (int(instance['label']) - self.data_min)/(self.data_max[id]['sell']['price'] - self.data_min)
                self.normalize_sell_data[id].append({'inputs': quantities + prices, 'outputs': [value_label]})

    def randomize_data(self):
        for id in self.normalize_buy_data:
            shuffle(self.normalize_buy_data[id])
        for id in self.normalize_sell_data:
            shuffle(self.normalize_sell_data[id])

    def setup_data(self):
        self.load_data()
        self.normalize_data()
        self.randomize_data()

    def get_train_test(self, data, train, test):
        return {
            'train': data[:int(len(data)*train)],
            'test': data[int(len(data)*train):]
        }

    """ type parameter filter by buy data or by sell data
        if normalized == 0: (no normalized)
            if id == None:
                Return a list of ids. Each id contains a list of instances and each instance contains also three data in a object:
                    'label': (single value) the label for this instance
                    'quantity': (list) the data for quantities for this instance
                    'price': (list) the data for prices for this instance
            id id == valid id number:
                Return a list of instances. Each instance has three data in a object:
                    'label': (single value) the label for this instance
                    'quantity': (list) the data for quantities for this instance
                    'price': (list) the data for prices for this instance

        if normalized == 1: (normalized)
            if id == None:
                Return a list of ids. Each id contains a list of instances and each instance contains also two data in a object:
                    'outputs': (single value in a list) the label for this instance
                    'inputs': (list) the data for quantities and prices merged for this instance
            id id == valid id number:
                Return a object that contains:
                    'train': (list) instances for train. Each instance has two data in a object:
                        'outputs': (single value in a list) the label for this instance
                        'inputs': (list) the data for quantities and prices merged for this instance
                    'test': (list) instances for test. Each instance has two data in a object:
                        'outputs': (single value in a list) the label for this instance
                        'inputs': (list) the data for quantities and prices merged for this instance
    """
    def get_data(self, type, normalized=1, id=None, train=0.8, test=0.2):
        if normalized == 0:
            if type == 'buy':
                if id is None:
                    return self.buy_data
                if self.buy_data.get(id) is not None:
                    return self.buy_data.get(id)
            elif type == 'sell':
                if id is None:
                    return self.sell_data
                if self.sell_data.get(id) is not None:
                    return self.sell_data[id]
        elif normalized == 1:
            if type == 'buy':
                if id is None:
                    return self.normalize_buy_data
                if self.normalize_buy_data.get(id) is not None:
                    return self.get_train_test(self.normalize_buy_data[id], train, test)
            elif type == 'sell':
                if id is None:
                    return self.normalize_sell_data
                if self.normalize_sell_data.get(id) is not None:
                    return self.get_train_test(self.normalize_sell_data.get(id), train, test)
        return None

    def denormalize_value(self, value, id, type):
        if type == 'buy' or type == 'sell':
            return value * (self.data_max[id][type]['price'] - self.data_min) + self.data_min
        return None

    def get_lstm_data(self, data):
        new_data = []
        limit = int(len(data[0])/2)

        for row in data:
            for j in range(limit):
                new_data.append([row[j], row[j+limit]])

        return new_data


#proc = Process()
#proc.setup_data()
#print(proc.get_data('sell', 0, '24344')[123])
#print(proc.get_data('sell', 1, '24344')['test'])
#print(proc.denormalize_value(proc.get_data('sell', 1, '24344')['train'][13]['outputs'][0], '24344', 'sell'))
#print(proc.data_max['24344']['sell'])
