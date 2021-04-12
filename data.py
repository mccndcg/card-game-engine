import json
import operator


colors = {
    'green': '\033[1;32;40m',
    'white': '\033[1;37;40m',
    'red': '\033[1;31;40m',
    'grey': '\033[1;30;40m',
    'yellow': '\033[1;33;40m',
    'purple': '\033[1;35;40m'
}

def combinator(a, b):
    if type(a) is list and type(b) is list:
        return a.extend(b)

def inside(a, b):
    if type(a) is list and (b in a):
        return True
    elif type(b) is list and (a in b):
        return True
    else:
        return False

def outside(a, b):
    if type(a) is list and (b in a):
        return False
    elif type(b) is list and (a in b):
        return False
    else:
        return True

ops = {
    '>': operator.gt,
    '<': operator.lt,
    '=': operator.eq,
    '>=': operator.ge,
    '<=': operator.le,
    '-': operator.sub,
    '+': operator.add,
    'set': operator.eq,
    'in': inside,
    'not in': outside
}
db = {}


with open('shorthand.json', encoding="utf8") as json_file:
    alias = {k: v for k, v in json.load(json_file).items()}

#with open('effects.json', encoding="utf8") as json_file:
#    alias.update( {k: v for k, v in json.load(json_file).items()} )

with open('set.json', encoding="utf8") as json_file:
    for dictionary in json.load(json_file):
        cardCode = dictionary['cardCode']
        db[cardCode] = {}
        # convert digits in json to actual numbers
        for key, value in dictionary.items():
            if type(value) == 'string' and value.isnumeric():
                value = int(value)
            db[cardCode][key] = value
    with open('dummy.json', encoding="utf8") as json_file:
        dummyval = json.load(json_file)
        db['DUMMY69'] = dummyval['DUMMY69']
        db['DUMMYTARGET'] = dummyval['DUMMYTARGET']

with open('set_effects.json', encoding="utf8") as json_file:
    for cardCode, effect in json.load(json_file).items():
        db[cardCode]['effect'] = effect

def init_state():
    with open('states.json', encoding="utf8") as json_file:
        data =  {k: v for k, v in json.load(json_file).items()}
    with open('rules.json', encoding="utf8") as json_file:
        data.update({k: v for k, v in json.load(json_file).items()})
        return data


def init_globals():
    with open('globals.json', encoding="utf8") as json_file:
        data = json.load(json_file)
    for i in list(data):
        globaldata[i] = {}
        for j in data[i]:
            name = j['name']
            globaldata[i][name] = {}
            for k in list(j):
                globaldata[i][name][k] = j[k]
