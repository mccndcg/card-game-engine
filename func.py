from config import Cue, spielberg, deque
from lor_deckcodes import LoRDeck
import helpers


toggle = True
#toggle = False


def feedbackGuy(entity, triggerStr):
    '''
    1. triggerDirectory[triggerStr] = [{'entity': v1, 'index': v2}]
    2. listener.target = entity > Entity that passed thru activation becomes
        target for listener.
    '''
    print(entity)
    def contextMan():
        if type(entity) is list:
            for subentity in entity:
                feedbackGuy(subentity, triggerStr)
        else:
            errorCheck()
    def errorCheck():
        try:
            for listenerDict in director.triggerDirectory[triggerStr]:
                actuator(listenerDict, triggerStr)
        # if event has no listing in triggerDirectory
        except KeyError:
            pass
    def actuator(listenerDict, triggerStr):
        print('actuator')
        index = listenerDict['idx']
        listener = listenerDict['entity']
        listener.target = entity
        if listener == director.producer:
            condition = getattr(listener, triggerStr)['condition'][index]
        else:
            condition = listener.effect['condition'][index]
        # check if condition with trigger in directory is true
        if (condition['method'] == 'autotrue' or
            helpers.valueCheck(listener, condition, director, index)):
            listener.activateCall(triggerStr, activateCall)
    contextMan()


def testing():
    x = director.createActor({'cardCode': "01PZ056",
                              'location': 'hand', 'owner': 'self'})
    {print(k, v) for k, v in director.triggerDirectory.items()}
    #card_activate(x)
    y = director.createActor({'cardCode': "01PZ004",
                              'location': 'hand', 'owner': 'self'})
    #card_activate(y)
    #moveEntity(y, ['summon_board'])


def getInput():
    print('get input: ')
#    print(director.roster)
#    {print(x) for x in director.roster['actors'].values() if x.location == 'hand'}
    def dummytest(inputString):
        if inputString == 'create':
            createEntity(None, {'cardCode': 'DUMMY69', 'location': 'board', 'owner': 'self'})
            getInput()
        elif inputString == 'kill':
            modifyEntity(director.dummy, {'attribute': 'location', 'value': 'graveyard', 'method': 'set'})
            print(director.dummy.location)
            getInput()
        else:
            print(helpers.textColor('red', 'ERR 01: Command not available. Choose from stack.'))
            getInput()
    inp = input()
    if inp.isnumeric():
        if len(inp) == 1:
            feedbackGuy(director.options[int(inp)], 'getInput')
        elif len(inp) > 1:
            feedbackGuy([director.options[int(x)] for x in inp], 'getInput')
    else:
        if inp in director.options:
            print(helpers.textColor('green', 'Command accepted.'))
            feedbackGuy(Cue(inp), 'getInput')
        else:
            dummytest(inp)

    # card_activate(hand[int(input())])


def init_game():
    global director
    director = spielberg()
    kurosawa = director.producer
    director.producer.state = 'alpha'
    game(kurosawa)
    print('FIN')


def game(kurosawa):
    kurosawa.activateCall(kurosawa.state, activateCall)
    if kurosawa.state == 'game_end' or kurosawa.state == 'round_end':
        return
    else:
        if kurosawa.state == 'round_start':
            script = {'cardCode': 'DUMMY69', 'location': 'board', 'owner': 'self', 'quantity': 1}
            director.dummy = director.createActor(script)
            print(director.dummy)
        game(kurosawa)

def addStack(entity, script):
    # access stack, initialize if needed
    try:
        getattr(director, script['stack'])
    except AttributeError:
        setattr(director, script['stack'], deque([]))
    if type(entity) == list:
        # append list
        setattr(director, script['stack'], getattr(
            director, script['stack']) + deque(entity))
    else:
        getattr(director, script['stack']).append(entity)
    print('stack added')


def resetStack(script):
    setattr(director, script['stack'], deque([]))


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
    print('FUCK')


def createEntity(reference, script):
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
            if script['method'] == 'copy':
                script.update({'reference': reference})
            elif script['method'] == 'random':
                y = helpers.db.values()
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
    feedbackGuy(creation, 'createCard')


def copyEntity(entityList, script):
    '''
    Function to copy existing entities. Due to quirks with python object
    references, copying entities are separate from creating new ones.
    '''
    print('_copyEntity')
    entityList[1] = helpers.deepcopy(entityList[0])


def modifyEntity(entityList, script):
    '''
    Modify entity attributes. Script needs {attribute, value, method}
    '''
    def contextMan(entityList):
        if type(entityList) is list:
            for entity in entityList:
                contextMan(entity)
        elif type(script['attribute']) is str:
            actuator(entityList, script['attribute'], script['value'])
        else:
            for index, subAttribute in script['attribute']:
                actuator(entityList, subAttribute, script['value'][index])
    def actuator(entity, attribute, value):
        '''
        Performs the actual call-out procedure.
        '''
        if attribute == 'location':
            trigger = 'changeLocation'
            entity.changeLocation(value, director)
        else:
            trigger = script['trigger']
        entity.modifyValue(attribute, value, script['method'])
        feedbackGuy(entity, trigger)
    contextMan(entityList)


def changePlayer():
    if director.producer.player == 'self':
        director.producer.player = 'oppo'
    else:
        director.producer.player = 'self'


def resolve_spell_q():
    for entity in director.spellStack:
        entity.activateCall('activate', activateCall)


def activateCall(entity, trigger, effect):
    '''
    Bridge function to call conditional functions.
    1. Check truthiness of conditions, then store in conditionmap.
    2. Iterate over each effect.
    3. Access condition requirements and refer against conditionmap.
    4. Effect can also be conditionless (autotrue).
    5. If conditions are met, call activate.
    '''
    if toggle:
        print('__activate call', entity.name, trigger)
    conditionmap = []
    def conditions():
        for idx, condition in enumerate(effect['condition']):
            print(condition)
            if 'trigger' in condition.keys() and (trigger != condition['trigger']):
                conditionmap.append(False)
            elif condition['method'] == 'autotrue':
                conditionmap.append(True)
            else:
                conditionmap.append(helpers.valueCheck(entity, condition, director, idx))
    def effectCycler():
        for effectIndex in effect['effect']:
            actuator(effectIndex)
    def actuator(effectIndex):
        print('actuator')
        # will try to access condition in effect: condition {True: [0,1], False: [2,3]}
        try:
            flag = True
            for boolean, conditionList in effectIndex['condition'].items():
                boolConditionmap = set([idx for idx, y in enumerate(
                    conditionmap) if y == helpers.bool(boolean)])
                if type(conditionList) == int and conditionList not in boolConditionmap:
                    flag = False
                    break
                elif type(conditionList) == list:
                    for conditionItem in conditionList:
                        if type(conditionItem) == int and conditionItem not in boolConditionmap:
                            flag = False
                            break
                        elif type(conditionItem) == list and set(conditionItem).isdisjoint(boolConditionmap):
                            flag = False
                            break
                if not flag:
                    break
            if flag:
                if effectIndex['func'] == 'override':
                    return [True, effect['param']]
                else:
                    print(helpers.textColor(
                        'purple', effectIndex['condition']['True']), helpers.textColor('green', effectIndex))
                    activate(entity, effectIndex, effect)
            else:
                print(helpers.textColor(
                    'purple', effectIndex['condition']['True']), helpers.textColor('red', effectIndex))
                try:
                    if effect['func'] == 'override':
                        return False
                except KeyError:
                    pass
        # effect has no condition
        except KeyError:
            print(helpers.textColor('green', effectIndex))
            activate(entity, effectIndex, effect)
    conditions()
    effectCycler()
    if toggle:
        print('____ exit activate call')


def activate(entity, effectIndex, effect):
    '''
    Actuator function to call effect functions.
    '''
    if toggle:
        print('__activate effect')
    function = effectIndex['func']
    try:
        param = effectIndex['param']
        param.update({"origin": entity})
        if 'target' in effect:
            # update store level target
            entity.targetStack = helpers.acquire_target(
                entity, effect['target'], director)
            target = entity.targetStack
            # parse values, copy the updated dynamic object
            try:
                param['modifiers']
                param = helpers.parse(param, target, director)
            except KeyError:
                pass
        # subeffect level target
        if 'target' in param:
            for j in param['target']:
                #target['pass']
                if type(j) is str:
                    globals()[function](j, param)
                #target[0,1,2]
                elif type(j) is int:
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
                    createEntity(None, dictVal)
        else:
            for i in list(LoRDeck.from_deckcode(script['deck'])):
                count, cardCode = i.split(':')
                count = int(count)
                while count > 0:
                    dictVal = {'cardCode': cardCode, 'creator': 'init',
                       'location': 'deck', 'owner': script['owner']}
                    createEntity(None, dictVal)
                    count = count - 1
    contextMan()

#
# def moveEntity(entityList, script):
#     try:
#         script = helpers.alias[script['shorthand']]
#     except KeyError:
#         pass
#     for card in entityList:
#         if script['destination'] in ['board', 'battlers'] and card.onPlay != 1:
#             modifyEntity(entityList, {'trigger': 'setOnPlay', 'attribute': 'onPlay',
#                                       'value': 1, 'method': 'set'})
#         elif script['destination'] not in ['board', 'battlers'] and card.location in ['board', 'battlers']:
#             modifyEntity(entityList, {'trigger': 'removeOnPlay', 'attribute': 'onPlay',
#                                       'value': 0, 'method': 'set'})
#         card.changeLocation(script['destination'], director)
#     script = {'trigger': 'changeLocation', 'attribute': 'location',
#               'value': script['destination'], 'method': 'set'}
#     modifyEntity(entityList, script)


def printer(lines):
    print(lines)


def printStack(script):
    print(helpers.textColor('yellow', '-------STACK------'))
    #[print(str(x)) for x in getattr(director, script['stack'])]
    for x in getattr(director, script['stack']):
        print(x)
    print(helpers.textColor('yellow', '------------------'))

if __name__ == '__main__':
    init_game()
