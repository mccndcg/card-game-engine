from random import choice
from data import alias, ops, colors
from copy import deepcopy

# def moveCheck():
#     '''
#     Determines the validity of a move (ex. requirements, valid targets)
#     '''
#     if entity.type == '':
#         as
#     elif entity.type == '':
#         as

def valueCheck(entity, reqt, director, idx):
    '''
    Conditional for effects.
    1. Get entity A.
    2. Get attribute x of A.
    3. Check whether valCompare or valDelta
    4. Get B (either entity or value)
    5. Return truthiness.
    '''
    def actuator(a, c):
        if a is False:
            return False
        if reqt['operator'] == 'in':
            a, c = c, a
        if ops[reqt['operator']](a, c):
            print(textColor('purple', idx), textColor('green', 'conditions pass'), a, c, reqt['a_attri'])
            return True
        else:
            print(textColor('purple', idx), textColor('red', 'conditions fail'), a, c, reqt['a_attri'])
            return False
    def contextMan(method):
        if method == 'valCompare':
            return actuator(getA(method), getC(method))
        elif method == 'valDelta':
            return ( actuator(getA('valCompare'), getC('valCompare')) and
            actuator(getA('valDelta_old'), getC('valDelta_old')) )
    def getA(method):
        try:
            reqt['a'] = deepcopy(getAlias(reqt['a_shorthand']))
        except KeyError:
            reqt['a'] = deepcopy(reqt['a'])
        # resolve a: the main entity
        if reqt['a'] == 'this':
            a = entity
        elif reqt['a'] == 'target':
            a = entity.target
        elif reqt['a'] == 'producer':
            a = director.producer
        elif type(reqt['a']) is dict:
            a = preFilter(reqt['a'], entity, director)
        elif reqt['a'][:6] == 'target':
            a = entity.targetStack[int(targ.strip('target#'))]
        if reqt['a_attri'] == 'count':
            a = len(a)
        else:
            try:
                if method == 'valDelta_old':
                    a = getattr(a, 'old_' + reqt['a_attri'])
                elif method == 'valCompare':
                    a = getattr(a, reqt['a_attri'])
            # ex 1
            except AttributeError:
                print(textColor('purple', idx), textColor('red', 'conditions fail'), 'no attribute', reqt['a_attri'])
                return False
        return a
    def getC(method):
        # B is value
        try:
            if reqt['value'] == 'this':
                c = entity
            elif method == 'valDelta_old':
                c = reqt['value_old']
            elif method == 'valCompare':
                c = reqt['value']
        # B is entity
        except KeyError:
            print(textColor('red', 'ER valueCheck 2'))
            b = preFilter(reqt['b'], entity, director)
            c = getattr(b, reqt['b_attri'])
        return c
    return contextMan(reqt['method'])


def preFilter(filters, entity, director):
    try:
        if 'dynamic' in filters['modifiers']:
            filters['conditions'] = parse(filters['conditions'], None, entity, director)
    except KeyError:
        pass
    if filters['entity'] == 'card':
        return(Filter(director.roster['actors'], filters))
    elif filters['entity'] == 'cue':
        return director.cue
    elif filters['entity'] == 'nexus':
        return(Filter(director.roster['nexus'], filters))


def Filter(x, filterDict):
    '''
    Returns a list of filtered entities.
    '''
    returnList = []
    for keyFilter, valueFilter in filterDict['conditions'].items():
        if type(valueFilter) == list:
            operator = 'in'
        elif type(valueFilter) == dict:
            operator = valueFilter['operator']
            valueFilter = valueFilter['value']
        else:
            operator = '='
        x = {k: v for k, v in x.items() if ops[operator](valueFilter, getattr(v, keyFilter))}
    y = [v for k, v in x.items()]
    try:
        get = filterDict['get']
    except KeyError:
        print(textColor('red', 'ER Filter 1'))
        return y
    if get['method'] == 'value':
        # toedit
        j = [v for v in sorted(y, reverse=get['reverse'], key=lambda item:
                               (getattr(item, get['value'][0]), getattr(item, get['value'][1])))]
        returnList = j[:get['count']]
    elif get['method'] == 'random':
        for returnIndex in range(0, get['count']):
            returnList.append(choice(y))
    elif get['method'] == 'pick':
        if get['reverse']:
            y.reverse()
        if get['count'] == 1:
            return y[0]
        returnList = y[:get['count']]
    return(returnList)


def acquire_target(entity, targetList, director):
    print('_enter acquire_target')
    target = []
    for index in targetList:
        if type(index) is list:
            index = choice(index)
        try:
            if index['shorthand'] == 'target':
                # target.append([entity.target])
                # continue
                if type(entity.target) == list:
                    target = target + [entity.target]
                else:
                    target.append([entity.target])
                continue
            elif index['shorthand'] == "this":
                target.append([entity])
                continue
            elif index['shorthand'] == "producer":
                target.append([director.producer])
                continue
            filter = deepcopy(getAlias(index['shorthand']))
        # no shorthand
        except KeyError:
            print(textColor('red', 'ER acquire_target 1'))
            filter = index['filter']
        try:
            filter['get']['count'] = index['quantity']
        # resort to default quantity
        except KeyError:
            pass
        if index['automatic'] == 'yes':
            target.append(preFilter(filter, entity, director))
        if index['automatic'] == 'no':
            target.append([choice(preFilter(filter, entity, director))])
    print('_exit acquire_target')
    return target


def a_t_helper(entity, target):
    if type(entity) == list:
        return target + entity
    else:
        return target.append([entity])


def getTarget(targetList):
    v = choice(targetList)
    return v


def getChoice(y):
    return choice(y)


def parse(param, target, entity, director):
    '''
    Converts static text pointers {target#0} in param to dynamic values.
    '''
    def subparser(attributeString):
        print(attributeString)
        targ, attri = attributeString.split('.', 1)
        if targ == 'director':
            return getattr(director, attri)
        elif targ == 'producer':
            return getattr(director.producer, attri)
        elif targ == 'this':
            return getattr(entity, attri)
        else:
            return getattr(target[int(targ.strip('target#'))], attri)
    def walker(parent, index, entity):
        if type(entity) is dict:
            for k, v in entity.items():
                walker(entity, k, v)
        elif type(entity) is list:
            for i, v in enumerate(entity):
                walker(entity, i, v)
        elif type(entity) is str and ('.' in entity):
            parent[index] = subparser(entity)
    # persist static text pointer, return the dynamic one to use
    print('_enter parse')
    cloneParam = deepcopy(param)
    walker(cloneParam, 0, cloneParam)
    return cloneParam

def bool(string):
    return string in ("True")

def textColor(color, string):
    return(colors[color] + f"{string}" + colors['white'])


def getAlias(shortname):
    if type(shortname) is dict:
        try:
            return alias[shortname['shorthand']]
        except KeyError:
            print(textColor('red', 'ER getAlias 1'))
            return shortname
    elif type(shortname) is str:
        try:
            return alias[shortname]
        except KeyError:
            print(textColor('red', 'ER getAlias 2'))
            return shortname
