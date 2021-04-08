from config import Cue, spielberg, deque, db
from lor_deckcodes import LoRDeck
from data import json
import helpers


toggle = True
#toggle = False

# def overrideGuy(entity, triggerStr):
#     pass
#


def activateEntity(entity, b):
    def contextMan():
        if type(entity) is list:
            for subEntity in entity:
                activateEntity(subEntity, b)
        else:
            actuator()
    def actuator():
        if not negateGuy(entity, b['trigger']):
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
        if type(triggerStr) is list:
            for subtrigger in triggerStr:
                feedbackGuy(entity, subtrigger)
        elif type(entity) is list:
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

def getInput():
    print('get input: ')
    def dummytest(inputString):
        if inputString == 'create':
            createEntity({'cardCode': 'DUMMY69', 'location': 'hand', 'owner': 'self'})
            createEntity({'cardCode': 'DUMMYTARGET', 'location': 'board', 'owner': 'oppo'})
        elif inputString == 'kill':
            x = [x for x in director.roster['actors'].values() if x.cardCode == 'DUMMY69']
            modifyEntity(x, {'attribute': 'location', 'value': 'graveyard', 'method': 'set'})
        elif inputString == 'summon':
            x = [x for x in director.roster['actors'].values() if x.cardCode == 'DUMMY69']
            modifyEntity(x, {'attribute': 'location', 'value': 'board', 'method': 'set'})
        elif inputString == 'show hand':
            x = [x for x in director.roster['actors'].values() if x.location == 'hand']
            print(x)
        elif inputString == 'cue':
            print(director.cue.line)
        elif inputString == 'state':
            print(director.producer.state)
        elif inputString == 'player':
            print(director.producer.player)
        else:
            print(helpers.textColor('red', 'ERR 01: Command not available. Choose from stack.'))
        feedbackGuy(None, 'test')
        getInput()
    inp = input()
    if inp.isnumeric():
        if len(inp) == 1:
            feedbackGuy(director.options[int(inp)], director.cue.command + '_select')
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
            director.cue.command = inp
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
    if kurosawa.state == 'game_end' or kurosawa.state == 'round_end':
        return
    else:
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
    getattr(director, script['stack']).reverse()


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
    else:
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
        def inner_check(condition, digitalBoolean):
            '''
            Returns true if bool and condition mismatch.
            '''
            if type(condition) == int and (digitalBoolean != conditions(index)):
                return True
            return False
        def inner_check_list(subCondition, digitalBoolean):
            for subSubCondition in subCondition:
                if inner_check(condition, digitalBoolean):
                    return True
            return False
        try:
            flag = True
            for index, (boolean, condition) in enumerate(effectIndex['condition'].items()):
                digitalBoolean = helpers.bool(boolean)
                if inner_check(condition, digitalBoolean):
                    flag = False
                    break
                elif type(condition) == list:
                    for subCondition in condition:
                        # False: [0, 1]
                        if inner_check(subCondition, digitalBoolean):
                            flag = False
                            break
                        elif type(subCondition) == list and inner_check_list(subCondition, digitalBoolean):
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
            print('   no condition', helpers.textColor('green', effectIndex),)
            activate(entity, effectIndex, effect)
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
            # parse values, copy the updated dynamic object
            try:
                if 'dynamic' in param['modifiers']:
                    param = helpers.parse(param, entity.targetStack, entity, director)
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
                    globals()[function](entity.targetStack[j], param)
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


def printStack(script):
    print(helpers.textColor('yellow', '-------STACK------'))
    #[print(str(x)) for x in getattr(director, script['stack'])]
    for x in getattr(director, script['stack']):
        print(x)
    print(helpers.textColor('yellow', '------------------'))

if __name__ == '__main__':
    init_game()
