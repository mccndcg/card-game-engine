from dataclasses import dataclass
from config import Cue, spielberg, db, modifier
from lor_deckcodes import LoRDeck
from data import json
import helpers

toggle = True
toggle = False
toggler = 1
command = []
#command = ['battle', 'attack', '0', 'commit', 'defend', '0', '1', 'commit']
command = ['activate', '0']

def activateEntity(entity, script):
    def contextMan():
        if type(entity) is list:
            for subEntity in entity:
                activateEntity(subEntity, script)
        else:
            actuator()
    def actuator():
        if not negateGuy(entity, script['trigger']):
            print(helpers.textColor('green', f"Activating {str(entity)}"))
            activateCall(entity, script['trigger'])
            feedbackGuy(entity, script['trigger'])
    contextMan()

def negateGuy(entity, trigger):
    '''
    - Returns true if negation condition is met. Otherwise, false.
    - Negates can also have a subcondition.
            "condition": [
                {
                    "negate": "set defender",
                    "subCondition": [
                        {
                            "method": "valCompare",
                            "a": "target",
                            "a_attri": "attack",
                            "value": "0",
                            "operator": ">"
                        },
                        {
                        }
                    ]}]

    '''
    try:
        for listener in director.overrideDirectory[trigger]:
            listener.target = entity
            if negateMain(listener, trigger, entity):
                return True
            return False
    except KeyError:
        pass

def negateMain(listener, trigger, entity):
    '''
    - Negate triggers must be descriptive of what is not allowed.
    - Returns True if effect is negated.
    '''
    def same_guy(condition):
        if condition['a'] == 'this':
            a = listener
        elif condition['a'] == 'target':
            a = listener.target
        elif condition['a'] == 'producer':
            a = director.producer
        elif type(condition['a']) is dict:
            a = preFilter(condition['a'], entity, director)
        if a == entity:
            return True
        return False
    def actuator(condition, idx):
        return helpers.valueCheck(listener, condition, director, idx)
    for idx, condition in enumerate(listener.effect['condition']):
        if 'negate' in condition.keys() and (trigger == condition['negate']):
            if 'subCondition' in condition.keys():
                for subCondition in condition['subCondition']:
                    if not(same_guy(subCondition) and actuator(subCondition, idx)):
                        return False
                return True
            elif same_guy(condition) and actuator(condition, idx):
                return True
    return False

def feedbackGuy(entity, triggerStr, mode=None):
    '''
    Outdated:
    1. triggerDirectory[triggerStr] = [{'entity': v1, 'index': v2}]
    2. listener.target = entity > Entity that passed thru activation becomes
        target for listener.
    '''
    def contextMan():
        if type(entity) is list:
            for subentity in entity:
                feedbackGuy(subentity, triggerStr)
        else:
            if mode == 'tamper':
                listenersCheck(director.tamperDirectory)
            else:
                listenersCheck(director.triggerDirectory)
    def listenersCheck(directory):
        try:
            for listener in directory[triggerStr]:
                listener.target = entity
                if toggler == 2:
                    print(f"{triggerStr} {listener}")
                activateCall(listener, triggerStr)
        # if event has no listing in triggerDirectory
        except KeyError:
            pass
    printer('_enter feedback', entity, triggerStr)

    contextMan()

def callFeedbackGuy(script, entity=None):
    feedbackGuy(entity, script['trigger'])


def getInput(entity=None, script=None):
    print('get input: ')
    def cycler(entity, script):
        if type(entity) == list:
            [cycler(subentity, script) for subentity in entity]
        else:
            modifyEntity(entity, script)
    def printmanual(entity,title):
        print(helpers.textColor('yellow', f"-------{title}------"))
        for x in entity:
            print(x)
    def dummytest(inputString):
        if inputString[:6] == 'create':
            createEntity({'cardCode': 'DUMMY69', 'location': inputString[7:], 'owner': 'oppo'})
            createEntity({'cardCode': 'DUMMYTARGET', 'location': inputString[7:], 'owner': 'self'})
        elif inputString == 'fleeting':
            x = [x for x in director.roster['card'].values() if x.location == 'hand']
        elif inputString == 'draw':
            x = [x for x in director.roster['card'].values() if x.index == 0 and x.location == 'deck' and x.owner==director.producer.player]
            cycler(x, {'attribute': 'location', 'value': 'hand', 'method': 'set'})
        elif inputString == 'kill':
            x = [x for x in director.roster['card'].values() if x.cardCode == 'DUMMYTARGET']
            cycler(x, {'attribute': 'location', 'value': 'graveyard', 'method': 'set'})
        elif inputString == 'summon':
            x = [x for x in director.roster['card'].values() if x.cardCode == 'DUMMY69']
            cycler(x, {'attribute': 'location', 'value': 'board', 'method': 'set'})
        elif inputString[:4] == 'show':
            printmanual([x for x in director.roster['card'].values() if x.location == inputString[5:] and x.owner == 'self'], 'SELF')
            printmanual([x for x in director.roster['card'].values() if x.location == inputString[5:] and x.owner == 'oppo'], 'OPPO')
        elif inputString == 'cue':
            print(director.cue.line)
        elif inputString == 'state':
            print(director.producer.state)
        elif inputString == 'player':
            print(director.producer.player)
        else:
            print(helpers.textColor('red', 'ERR 01: Command not available. Choose from stack.'))
        getInput()
    if len(command) > 0:
        inp = command[0]
        command.pop(0)
    else:
        inp = input()
    if inp.isnumeric():
        if len(inp) == 1:
            try:
                # inputEntity = director.options[int(inp)]
                # print(inputEntity)
                # director.producer.updateInput(inp, inputEntity)
                entity.prevSelection = entity.selection
                entity.selection = director.options[int(inp)]
            except IndexError:
                print(helpers.textColor('red', 'ERR 02: Selection not in stack.'))
                getInput()
        elif len(inp) > 1:
            feedbackGuy([director.options[int(x)] for x in inp], 'getInput')
    else:
        if inp in director.options:
            director.cue.update(inp)
            print(helpers.textColor('green', 'Command accepted.'))
            feedbackGuy(director.cue, inp)
        elif inp == 'break':
            return False
        else:
            dummytest(inp)


def init_game():
    global director
    director = spielberg()
    kurosawa = director.producer
    director.producer.state = 'alpha'
    game(kurosawa)
    print('FIN')


def game(kurosawa):
    kurosawa.activateCall(activateCall)
    feedbackGuy(None, kurosawa.state)
    game(kurosawa)


def modifyState(script):
    kurosawa = director.producer
    if script['state'] == 'game_end':
        pass
    print(helpers.textColor('purple', 'modifyState'))
    if script['state'] in ['transition', 'sanitize']:
        kurosawa.changeState(kurosawa.state+'_'+script['state'])
    else:
        kurosawa.changeState(script['state'])
    #feedbackGuy(kurosawa, script['state'])


def testFunc():
    print('HI')

def exitFunc():
    exit()

def createEntity(script):
    '''
    Creates new entity. 1st param is for copying. Script must include:
    {'method':v1, 'quantity':v2, 'cardCode': v3, 'creator': v4,
       'location': v5, 'owner': v6}
    1. Set quantity.
    2. Update script according to method.
    3. Call director method createActor.
    '''
    try:
        script['quantity']
    except KeyError:
        script['quantity'] = 1
    for x in range(0, script['quantity']):
        try:
            # todo
            if script['method'] == 'copy':
                script.update({'reference': reference})
            elif script['method'] == 'random':
                y = db.values()
                for filterDict in script['filter']:
                    if filterDict['operator'] == 'in':
                        y = filter(
                            lambda v: v[filterDict['attribute']] in filterDict['list'], y)
                        y = list(y)
                    else:
                        y = filter(lambda v: helpers.ops[filterDict['operator']](
                            v[filterDict['attribute']], filterDict['value']), y)
                        y = list(y)
                script.update({'cardCode': helpers.getChoice(y)['cardCode']})
        except KeyError:
            pass
        creation = director.createActor(script)
        feedbackGuy(creation, 'createEntity')


def copyEntity(entityList, script):
    '''
    Function to copy existing entities. Due to quirks with python object
    references, copying entities are separate from creating new ones.
    '''
    print('_copyEntity')
    entityList[1] = helpers.deepcopy(entityList[0])


def modifyEntity(entity, script):
    '''
    Modify entity attributes. Script needs {attribute, value, method}.
    Builds a list of trigger, script can have ONE or LIST of triggers.
    Iterates triggerlist, then calls feedbackGuy.
    '''
    @dataclass
    class modifyEntityObject:
        attribute: str
        value: int
        method: str

        def __repr__(self):
            return f"({self.method} {self.attribute} {self.value})"
    #
    def judge(thing):
        method = ['set', 'clamp', 'add', 'subtract']
        value = (len(method) - method.index(thing.method))*10
        try:
            value += (len(method) - method.index(thing.value))
        except:
            pass
        return value
    def contextMan(entity):
        if type(script['attribute']) is str:
            actuator(entity, script['attribute'], script['value'])
        else:
            # can modify entity's multiple attribs, at the same call
            # ex: attrib: ['health', 'attack'], value [3, 4]
            for index, subAttribute in script['attribute']:
                actuator(entity, subAttribute, script['value'][index])
    def actuator(entity, attribute, value):
        '''
        Performs the actual call-out procedure.
        '''
        entity.modifyEntityObject = modifyEntityObject(attribute, value, script['method'])
        trigger = ['modifyEntity']
        try:
            if type(script['trigger']) is list:
                trigger.extend(script['trigger'])
            else:
                trigger.append(script['trigger'])
        except:
            pass
        # try:
        #     if script['mode'] == 'tamper':
        #         entity.tamperList.append(modifyEntityObject(attribute, value, script['method']))
        #         return
        # except KeyError:
        #     pass
        if attribute == 'location':
            trigger.append('changeLocation')
            entity.changeLocation(value, director)

        #entity.modifyEntityObject.tamperList = []
        for subTrigger in trigger:
            feedbackGuy(entity, 'modifyEntity', 'tamper')
        # entity.modifyEntityObject.tamperList.sort(key=judge)
        # entity.modifyEntityObject.tamperList.reverse()
        # print(entity.modifyEntityObject.tamperList)
        # for subtamperer in entity.modifyEntityObject.tamperList:
        #     entity.modifyEntityObject = subtamperer
        #     modifier(entity)
        modifier(entity)
        for subTrigger in trigger:
            feedbackGuy(entity, subTrigger)
    contextMan(entity)


def activateCall(entity, trigger):
    '''
    Bridge function to call conditional functions. Does not have feedback.
    1. Check truthiness of conditions, then store in conditionmap.
    2. Iterate over each effect.
    3. Access condition requirements and refer against conditionmap.
    4. Effect can also be conditionless (autotrue).
    5. If conditions are met, call activate.
            {
                "condition": {"True": 1},
                "func": "break"
            }
    '''
    printer(f" > {entity} >> {helpers.textColor('yellow', trigger)}")
    conditionmap = []
    try:
        effect = entity.effect
    except AttributeError: #no effect
        print(helpers.textColor('red', 'no effect'))
        return
    def conditions(index):
        condition = effect['condition'][index]
        if 'trigger' in condition.keys():
            if type(condition['trigger']) is list and (trigger not in condition['trigger']):
                return False
            elif type(condition['trigger']) is str and (trigger != condition['trigger']):
                return False
        try:
            if condition['method'] == 'autotrue':
                return True
            if condition['method'] == 'monad':
                if entity == entity.target:
                    return True
                else:
                    return False
        except KeyError:
            pass
        return helpers.valueCheck(entity, condition, director, index)
    def effectCycler():
        for effectIndex in effect['effect']:
            # for break
            if actuator(effectIndex) is False:
                return
    def actuator(effectIndex):
        def inner_check(conIndex, digitalBoolean):
            '''
            Returns true if bool and condition mismatch.
            '''
            if digitalBoolean != conditions(conIndex):
                return True
            return False
        def inner_check_list(subconIndex, digitalBoolean):
            # [0, 1]
            for subsubconIndex in subconIndex:
                if not inner_check(subsubconIndex, digitalBoolean):
                    return True
            return False
        flag = True
        try:
        #if 'condition' in effectIndex:
            for boolean, condition in effectIndex['condition'].items():
                digitalBoolean = helpers.bool(boolean)
                # True: 0
                if type(condition) == int and(inner_check(condition, digitalBoolean)):
                    flag = False
                    break
                elif type(condition) == list:
                    for subCondition in condition:
                        # False: [0, 1]
                        if type(subCondition) == int and inner_check(subCondition, digitalBoolean):
                            flag = False
                            break
                        # False: [[0, 1], 2]
                        elif type(subCondition) == list and not inner_check_list(subCondition, digitalBoolean):
                            flag = False
                if not flag:
                    break
            if flag:
                if toggler == 2:
                    print('   ', helpers.textColor(
                        'purple', effectIndex['condition']), helpers.textColor('green', effectIndex))
                if activate(entity, effectIndex, effect) == 'break':
                    return False
            else:
                if toggler == 2:
                    print('   ',helpers.textColor(
                        'purple', effectIndex['condition']), helpers.textColor('red', effectIndex))
        # effect has no condition
        except KeyError:
            if toggler == 2:
                print('   no condition', helpers.textColor('green', effectIndex))
            if activate(entity, effectIndex, effect) == 'break':
                return False
    effectCycler()
    printer('____ exit activate call')


def activate(entity, effectIndex, effect):
    # cannot send just target, because not all effects have target
    '''
    - Actuator function to call effect functions.
    - Checks if param has subparams, then calls negator function for the first
    subparam. If its negated, the entire subparam is negated.
            {
            "func": "modifyEntity",
            "param": {
                "trigger": "set defender",
                "subparam": [
                    {
                        "target": [1],
                    },
                    {
                        "target": [3],
                    }
                ]}}
    '''
    def negator(entity, trigger):
        if type(trigger) is not list:
            trigger = [trigger]
        for subTrigger in trigger:
            if negateGuy(entity, subTrigger):
                print(helpers.textColor('red', f"NEGATED"))
                return True
    def caller(function, **kwargs):
        try:
            if subparamIndex and function == 'modifyEntity' and negator(kwargs['entity'], kwargs['script']['trigger']):
                # negated
                return False
        except KeyError:
            pass
        if globals()[function](**kwargs) == 'break':
            return 'break'
        else:
            return True
    def actuator(param):
        try:
            if 'dynamic' in param['modifiers']:
                param = helpers.parse(param, target, entity, director)
        except KeyError:
            pass
        # subeffect level target
        if 'target' in param:
            for j in param['target']:
                if 'value_pointer' in param:
                    param['value'] = target[param['value_pointer']]
                # target['pass']

                if type(j) is str:
                    returnVal = caller(effectIndex['func'], entity=j, script=param)
                # target[0,1,2]
                elif type(j) is int:
                    if target[j] is not None:
                        # send targets one by one
                        if type(target[j]) is list:
                            returnVal = [caller(effectIndex['func'], entity=x, script=param) for x in target[j]]
                        else:
                            returnVal = caller(effectIndex['func'], entity=target[j], script=param)
                    else:
                        returnVal = None
            return returnVal
        else:
            caller(effectIndex['func'], script=param)
    if toggle == 2:
        print(helpers.textColor('red', 'ACTIVATE'))
    # becomes False via negator
    # becomes False if not current iter param is not index 0
    subparamIndex = True
    if 'target' in effect:
        target = [helpers.acquire_target(entity, x, director) for x in effect['target']]
    try:
        param = helpers.deepcopy(effectIndex['param'])
        if type(param) == list:
            for index, subparam in enumerate(param):
                subparam.update({"origin": entity})
                if index != 0:
                    subparamIndex = False
                flag = actuator(subparam)
                if index == 0 and not flag:
                    break
                if flag == 'break':
                    return 'break'
        else:
            param.update({"origin": entity})
            if actuator(param) == 'break':
                return 'break'
    except KeyError:
        caller(effectIndex['func'])
    printer('____exit activate effect')

def createPlayer(script):
    if type(script['owner']) is list:
        for owner in script['owner']:
            createPlayer({'owner': owner})
    else:
        director.createPlayer(script['owner'])

def createDeck(script):
    '''
    Creates entity deck. Point for plugins. Script must contain:
    {'deck':v1, 'owner':v2}
    '''
    def contextMan():
        if script['deck'] == 'standard':
            for num in range(1, 13):
                for suit in ['hearts', 'clubs', 'spades', 'diamonds']:
                    dictVal = {'num': num, 'suit': suit,
                       'location': 'deck', 'owner': script['owner']}
                    createEntity(dictVal)
        else:
            for i in list(LoRDeck.from_deckcode(script['deck'])):
                count, cardCode = i.split(':')
                count = int(count)
                while count > 0:
                    dictVal = {'cardCode': cardCode, 'creator': 'init',
                       'location': 'deck', 'owner': script['owner']}
                    createEntity(dictVal)
                    count = count - 1
    contextMan()

def sysout(script):
    print(helpers.textColor('green', f"{script['line']}"))

def printer(*args):
    if toggle:
        print(args)

def createDummy():
    createEntity({'cardCode': 'DUMMYTARGET', 'location': 'board', 'owner': 'self'})
    createEntity({'cardCode': 'DUMMY69', 'location': 'board', 'owner': 'oppo'})

def addStack(entity, script):
    # access stack, initialize if needed
    try:
        stackEntity = getattr(director, script['stack'])
    except AttributeError:
        setattr(director, script['stack'], [])
        stackEntity = getattr(director, script['stack'])
    if type(entity) == list:
        stackEntity.extend(entity)
    else:
        stackEntity.append(entity)
    stackEntity.reverse()

def resetStack(script):
    setattr(director, script['stack'], [])

def printStack(script):
    print(helpers.textColor('yellow', '-------STACK------'))
    for x in getattr(director, script['stack']):
        print(x)
    print(helpers.textColor('yellow', '------------------'))

if __name__ == '__main__':
    init_game()
