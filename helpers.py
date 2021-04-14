from functools import reduce
from random import choice
from data import alias, ops, colors
from copy import deepcopy


toggle = True
toggle = False
toggler = 1

def printer(*args):
    if toggle:
        print(args)

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
        if toggler == 2:
            print(a,c)
        if a is False:
            return False
        try:
            if ops[reqt['operator']](a, c):
                printer(textColor('purple', idx), textColor('green', 'conditions pass'), a, c, reqt['a_attri'])
                return True
            else:
                printer(textColor('purple', idx), textColor('red', 'conditions fail'), a, c, reqt['a_attri'])
                return False
        except TypeError:
            # ex: compare 1(int) and graveyard(str)
            return False
    def contextMan():
        if toggler == 2:
            try:
                print(entity, entity.target, reqt['a'], reqt['a_attri'])
            except AttributeError:
                print('error')
        return actuator(getA(reqt['a'], reqt['a_attri']), getC())
    def get_entity(targetString):
        entityTarget = deepcopy(targetString)
        try:
            entityTarget = getAlias(entityTarget)
        except KeyError:
            pass
        # resolve a: the main entity
        a = string2entity(entity, entityTarget, director)
        if a:
            return a
        elif type(entityTarget) is dict:
            return(preFilter(entityTarget, entity, director))
        elif a[:6] == 'target':
            return(entity.targetStack[int(targ.strip('target#'))])

        return a
    def subparser(attributeString, target):
        getter = lambda a, b: getattr(a, b)
        attribs = attributeString.split('.')
        attribs.insert(0, target)
        return reduce(getter, attribs)
    def getA(reqtEntity, reqtAttri):
        a = get_entity(reqtEntity)
        if reqtAttri == 'count':
            a = len(a)
        else:
            # patchwork for filter{get: 1}. filter function returns a []
            try:
                if len(a) == 1:
                    a = a[0]
            except TypeError:
                pass
            try:
                a = subparser(reqtAttri, a)
            except AttributeError:
                if toggler == 2:
                    print(textColor('purple', idx), textColor('red', 'conditions fail'), 'no attribute', reqtAttri)
                return False
        return a
    def getC():
        # B is value
        try:
            if reqt['value'] == 'this':
                c = entity
            else:
                c = reqt['value']
        # B is entity
        except KeyError:
            c = getA(reqt['b'], reqt['b_attri'])
        except AttributeError:
            printer(textColor('purple', idx), textColor('red', 'conditions fail'), 'no attribute', reqt['value'])
            return False
        return c
    return contextMan()


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
    printer(f"_enter acquire_target {targetEntity}")
    if type(targetEntity) is list:
        targetEntity = choice(targetEntity)
    try:

        a = string2entity(entity, targetEntity['shorthand'], director)
        if targetEntity['shorthand'] == 'stack':
            try:
                return(getattr(director, targetEntity['stack']))
            except AttributeError:
                setattr(entity, targetEntity['stack'], [])
                return(getattr(director, targetEntity['stack']))
        if a is not False:
            if 'attribute' in targetEntity:
                return getattr(a, targetEntity['attribute'])
            else:
                return a
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
    printer('_exit acquire_target')


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
    printer('_enter parse')
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
