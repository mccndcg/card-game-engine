from functools import reduce
from random import choice
from data import alias, ops, colors
from copy import deepcopy


toggle = True
toggle = False


def string2entity(entity, alias, director):
    if alias == 'this':
        return(entity)
    elif alias == 'target':
        return(entity.target)
    elif alias == 'producer':
        return(director.producer)
    elif alias == 'cue':
        return(director.cue)
    elif alias == 'director':
        return(director)
    elif alias == 'producer.inputEntity':
        return(director.producer.inputEntity)
    elif alias == 'producer.inputEntityLast':
        return(director.producer.inputEntityLast)
    elif alias == 'stack':
        return(getattr(director, targetEntity['stack']))
    elif alias == 'none':
        return(None)
    else:
        return False


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
            # print(textColor('purple', idx), textColor('green', 'conditions pass'), a, c, reqt['a_attri'])
            return True
        else:
            # print(textColor('purple', idx), textColor('red', 'conditions fail'), a, c, reqt['a_attri'])
            return False
    def contextMan(method):
        if method == 'valCompare':
            return actuator(getA(method), getC(method))
        elif method == 'valDelta':
            return ( actuator(getA('valCompare'), getC('valCompare')) and
            actuator(getA('valDelta_old'), getC('valDelta_old')) )
    def getA_entity():
        entityA = deepcopy(reqt['a'])
        try:
            entityA = getAlias(entityA)
        except KeyError:
            pass
        # resolve a: the main entity
        a = string2entity(entity, entityA, director)
        if a:
            return a
        elif type(entityA) is dict:
            return(preFilter(entityA, entity, director))
        elif a[:6] == 'target':
            return(entity.targetStack[int(targ.strip('target#'))])
        return a
    def getA(method):
        a = getA_entity()
        if reqt['a_attri'] == 'count':
            a = len(a)
        else:
            # patchwork for filter{get: 1}. filter function returns a []
            try:
                if len(a) == 1:
                    a = a[0]
            except TypeError:
                pass
            try:
                if method == 'valDelta_old':
                    a = getattr(a, 'old_' + reqt['a_attri'])
                elif method == 'valCompare':
                    a = getattr(a, reqt['a_attri'])
                    for x in range(1, 9):
                        if 'a_attri'+str(x) in reqt:
                            a = getattr(a, reqt['a_attri' + str(x)])
                        else:
                            break
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
            entityB = deepcopy(reqt['b'])
            try:
                entityB = getAlias(entityB)
            except KeyError:
                pass
            b = preFilter(entityB, entity, director)
            c = getattr(b, reqt['b_attri'])
        return c
    return contextMan(reqt['method'])


def preFilter(filters, entity, director):
    newfilter = deepcopy(filters)
    try:
        if 'dynamic' in newfilter['modifiers']:
            newfilter['conditions'] = parse(newfilter['conditions'], None, entity, director)
    except KeyError:
        pass
    entity = newfilter['entity']
    if entity in ['card', 'nexus']:
        return(Filter(director.roster[entity], newfilter))
    elif newfilter['entity'] == 'cue':
        return director.cue


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


def acquire_target(entity, targetEntity, director):
    if toggle:
        print(f"_enter acquire_target {targetEntity}")
    if type(targetEntity) is list:
        targetEntity = choice(targetEntity)
    try:
        a = string2entity(entity, targetEntity['shorthand'], director)
        if a is not False:
            return a
        print(targetEntity)
        filter = deepcopy(getAlias(targetEntity['shorthand']))
    # no shorthand
    except KeyError:
        filter = targetEntity['filter']
    except AttributeError:
        return None
    try:
        filter['get']['count'] = targetEntity['quantity']
    # resort to default quantity
    except KeyError:
        pass
    return(preFilter(filter, entity, director))
    if toggle:
        print('_exit acquire_target')


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
        getter = lambda a, b: getattr(a, b)
        targ = attributeString.split('.')
        a = string2entity(entity, targ[0], director)
        if a is not False:
            targ[0] = a
        else:
            targ[0] = target[int(targ[0])]
        return reduce(getter, targ)
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
    if toggle:
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
            #print(textColor('red', 'ER getAlias 1'))
            return shortname
    elif type(shortname) is str:
        try:
            return alias[shortname]
        except KeyError:
            #print(textColor('red', 'ER getAlias 2'))
            return shortname
