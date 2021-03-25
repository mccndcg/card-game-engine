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


ops = {
    '>': operator.gt,
    '<': operator.lt,
    '=': operator.eq,
    '>=': operator.ge,
    '<=': operator.le,
    '-': operator.sub,
    '+': operator.add,
    'set': operator.eq,
    'in': operator.contains
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
        for key, value in dictionary.items():
            if type(value) == 'string' and value.isnumeric():
                value = int(value)
            db[cardCode][key] = value
    with open('testcard.json', encoding="utf8") as json_file:
        db['DUMMY69']['effect'] = json.load(json_file)
    with open('testcard_attri.json', encoding="utf8") as json_file:
        dummyval = json.load(json_file)
        db['DUMMY69'].update(dummyval['dummy'])
        db['DUMMYTARGET'].update(dummyval['defender'])

def init_override():
    with open('override.json', encoding="utf8") as json_file:
        return {k: v for k, v in json.load(json_file).items()}

def init_state():
    with open('states.json', encoding="utf8") as json_file:
        return {k: v for k, v in json.load(json_file).items()}


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
