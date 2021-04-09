from config import Cue, spielberg, db
from lor_deckcodes import LoRDeck
from data import json
import helpers

toggle = True
toggle = False
command = []
#command = ['battle', 'attack', '0', 'commit', 'defend', '0', '0', 'commit']

def activateEntity(entity, b):
    def contextMan():
        if type(entity) is list:
            for subEntity in entity:
                activateEntity(subEntity, b)
        else:
            actuator()
    def actuator():
        if not negateGuy(entity, b['trigger']):
            print(helpers.textColor('green', ('Activating '+ str(entity))))
            activateCall(entity, b['trigger'])
            feedbackGuy(entity, b['trigger'])
    contextMan()

def negateGuy(entity, trigger):
    '''
    Returns true if negation condition is met. Otherwise, false.
    '''
    try:
        for listener in director.overrideDirectory[trigger]:
            listener.target = entity
            if negateCall(listener, trigger, entity) == True:
                return True
            return False
    except KeyError:
        pass

def negateCall(listener, trigger, entity):
    '''
    Negate triggers must be descriptive of what is allowed. Returns True if
    effect is negated.
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
    for idx, condition in enumerate(listener.effect['condition']):
        if 'negate' in condition.keys() and (trigger == condition['negate']) and same_guy(condition):
            if helpers.valueCheck(listener, condition, director, idx) == False:
                return(True)
    return(False)

def feedbackGuy(entity, triggerStr):
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
            errorCheck()
    def errorCheck():
        try:
            for listener in director.triggerDirectory[triggerStr]:
                listener.target = entity
                activateCall(listener, triggerStr)
        # if event has no listing in triggerDirectory
        except KeyError:
            pass
    if toggle:
        print('_enter feedback', entity, triggerStr)
    contextMan()

def callFeedbackGuy(entity, script):
    feedbackGuy(entity, script['trigger'])


def getInput():
    print('get input: ')
    def printmanual(entity,title):
        print(helpers.textColor('yellow', f"-------{title}------"))
        for x in entity:
            print(x)
    def dummytest(inputString):
        if inputString == 'create':
            createEntity({'cardCode': 'DUMMYTARGET', 'location': 'board', 'owner': 'self'})
            createEntity({'cardCode': 'DUMMY69', 'location': 'board', 'owner': 'oppo'})
        elif inputString == 'kill':
            x = [x for x in director.roster['card'].values() if x.cardCode == 'DUMMY69']
            modifyEntity(x, {'attribute': 'location', 'value': 'graveyard', 'method': 'set'})
        elif inputString == 'summon':
            x = [x for x in director.roster['card'].values() if x.cardCode == 'DUMMY69']
            modifyEntity(x, {'attribute': 'location', 'value': 'board', 'method': 'set'})
        elif inputString[:4] == 'show':
            printmanual([x for x in director.roster['card'].values() if x.location == inputString[5:] and x.owner == 'self'], 'SELF')
            printmanual([x for x in director.roster['card'].values() if x.location == inputString[5:] and x.owner == 'oppo'], 'OPPO')
        elif inputString == 'cue':
            print(director.cue.line)
        elif inputString == 'state':
            print(director.producer.state)
        elif inputString == 'player':
            print(director.producer.player)
        elif inputString == 'break':
            print(breakhere)
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
                inputEntity = director.options[int(inp)]
                director.producer.updateInput(inp, inputEntity)
            except IndexError:
                print(helpers.textColor('red', 'ERR 02: Selection not in stack.'))
                getInput()
        elif len(inp) > 1:
            feedbackGuy([director.options[int(x)] for x in inp], 'getInput')
    # if inp.isnumeric():
    #     try:
    #         print(director.producer.player)
    #         print(director.location[director.producer.player]['hand'])
    #     except KeyError:
    #         getInput()
    else:
        if inp in director.options:
            director.cue.update(inp)
            print(helpers.textColor('green', 'Command accepted.'))
            feedbackGuy(director.cue, inp)
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
        print('created >', creation)
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
    Modify entity attributes. Script needs {attribute, value, method}
    '''
    def contextMan(entity):
        if type(entity) is list:
            for subEntity in entity:
                contextMan(subEntity)
        elif type(script['attribute']) is str:
            actuator(entity, script['attribute'], script['value'])
        else:
            for index, subAttribute in script['attribute']:
                actuator(entity, subAttribute, script['value'][index])
    def actuator(entity, attribute, value):
        '''
        Performs the actual call-out procedure.
        '''
        trigger = ['modifyEntity']
        if attribute == 'location':
            trigger.append('changeLocation')
            entity.changeLocation(value, director)
        else:
            try:
                if type(script['trigger']) is list:
                    trigger.extend(script['trigger'])
                else:
                    trigger.append(script['trigger'])
            except:
                pass
        entity.modifyValue(attribute, value, script['method'])
        for subTrigger in trigger:
            #if negateGuy(entity, triggerStr) is False:
            feedbackGuy(entity, subTrigger)
    contextMan(entity)


def changePlayer():
    if director.producer.player == 'self':
        director.producer.player = 'oppo'
        director.producer.opposite = 'self'
    else:
        director.producer.opposite = 'oppo'
        director.producer.player = 'self'

#
# def resolve_spell_q():
#     for entity in director.spellStack:
#         entity.activateCall('activate', activateCall)


def activateCall(entity, trigger):
    '''
    Bridge function to call conditional functions. Does not have feedback.
    1. Check truthiness of conditions, then store in conditionmap.
    2. Iterate over each effect.
    3. Access condition requirements and refer against conditionmap.
    4. Effect can also be conditionless (autotrue).
    5. If conditions are met, call activate.
    '''
    print('>', entity.name, '>>', trigger)
    conditionmap = []
    try:
        effect = entity.effect
    except AttributeError: #no effect
        print(helpers.textColor('red', 'no effect'))
        return
    def conditions(index):
        condition = effect['condition'][index]
        if 'trigger' in condition.keys() and (trigger != condition['trigger']):
            return False
        elif condition['method'] == 'autotrue':
            return True
        else:
            return(helpers.valueCheck(entity, condition, director, index))
    def effectCycler():
        for effectIndex in effect['effect']:
            actuator(effectIndex)
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
            for boolean, condition in effectIndex['condition'].items():
                digitalBoolean = helpers.bool(boolean)
                # True: 0
                if type(condition) == int and (inner_check(condition, digitalBoolean)):
                    flag = False
                    break
                elif type(condition) == list:
                    for subCondition in condition:
                        # False: [0, 1]
                        if type(condition) == int and inner_check(subCondition, digitalBoolean):
                            flag = False
                            break
                        # False: [[0, 1], 2]
                        elif type(subCondition) == list and not inner_check_list(subCondition, digitalBoolean):
                            flag = False
                if not flag:
                    break
            if flag:
                print('   ', helpers.textColor(
                    'purple', effectIndex['condition']), helpers.textColor('green', effectIndex))
                activate(entity, effectIndex, effect)
            else:
                print('   ',helpers.textColor(
                    'purple', effectIndex['condition']), helpers.textColor('red', effectIndex))
        # effect has no condition
        except KeyError:
            print('   no condition', helpers.textColor('green', effectIndex))
            activate(entity, effectIndex, effect)
    effectCycler()
    if toggle:
        print('____ exit activate call')


def activate(entity, effectIndex, effect):
    # cannot send just target, because not all effects have target
    '''
    Actuator function to call effect functions.
    '''
    if toggle:
        print('__activate')
    function = effectIndex['func']
    if 'target' in effect:
        target = [helpers.acquire_target(entity, x, director) for x in effect['target']]
    try:
        param = helpers.deepcopy(effectIndex['param'])
        param.update({"origin": entity})
        try:
            if 'dynamic' in param['modifiers']:
                param = helpers.parse(param, target, entity, director)
        except KeyError:
            pass
        # subeffect level target
        if 'target' in param:
            for j in param['target']:
                #target['pass']
                if 'value_pointer' in param:
                    param['value'] = target[param['value_pointer']]
                if type(j) is str:
                    globals()[function](j, param)
                #target[0,1,2]
                elif type(j) is int:
                    if target is None:
                        return
                    else:
                        globals()[function](target[j], param)
        else:
            globals()[function](param)
    except KeyError:
        globals()[function]()
    if toggle:
        print('____exit activate effect')


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


def printer(lines):
    print(lines)

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
