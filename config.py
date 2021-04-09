from data import db, alias, init_state
from helpers import textColor, deepcopy


def modifier(self, variable, value, operator):
    try:
        var = getattr(self, variable)
    # 'attribute not initialized'
    except AttributeError:
        setattr(self, variable, 0)
        var = 0
    # set old value
    setattr(self, 'old_' + variable, var)
    # default operator is set
    if operator == 'set':
        setattr(self, variable, value)
    # [1, 2, 3]
    # 1 > 2, 2 > 3, 3 > 1
    if operator == 'cycle':
        if value.index(var) != len(value) - 1:
            setattr(self, variable, value[value.index(var) + 1])
        else:
            setattr(self, variable, value[0])
    elif operator == 'clamp':
        max_var = getattr(self, 'max' + variable)
        if max_var >= var + value:
            setattr(self, variable, var + value)
        else:
            setattr(self, variable, max_var)
    elif operator == 'add':
        setattr(self, variable, var + value)
    elif operator == 'subtract':
        setattr(self, variable, var - value)
    print(textColor('grey', variable),
          textColor('grey', var), textColor('yellow', getattr(self, variable)))
    # return value for modifyValue to pass to feedbackGuy


class Cue(object):

    def __init__(self, line):
        self.command = line
        self.prevCommand = ''
        self.name = 'morricone'
        self.history = []

    def update(self, inp):
        self. prevCommand, self.command = self.command, inp
        self.history.insert(0, inp)

    def modifyValue(self, variable, value, operator):
        modifier(self, variable, value, operator)

    def __repr__(self):
        return f'(Current command is {self.command})'

    def __str__(self):
        return f'(Current command is  {self.command})'

class stateObject(object):

    def __init__(self, effect, name):
        self.effect = effect
        self.name = name

class producer(object):

    def __init__(self, director):
        print('_init_ created object producer')
        self.states = init_state()
        self.state = None
        self.prevState = None
        self.name = 'akira'
        self.player = 'self'
        self.opposite = 'oppo'
        self.roundturn = 'self'
        self.naturalturn = 'self'
        self.target = None
        self.targetList = None
        self.inputEntity = None
        self.inputIndex = None
        for state, effect in init_state().items():
            setattr(self, state, stateObject(effect, state))
            try:
                for condition in effect['condition']:
                    director.createSubscriber(getattr(self, state), condition)
            except KeyError: # no condition
                pass

    def updateInput(self, index, entity):
        self.inputEntityLast = self.inputEntity
        self.inputEntity = entity
        self.inputIndexLast = self.inputIndex
        self.inputIndex = index

    def modifyValue(self, variable, value, operator):
        modifier(self, variable, value, operator)

    def changeState(self, state):
        # self.prevState = deepcopy(self.state)
        self.prevState = self.state
        self.state = state
        print(textColor('grey', self.prevState), textColor('yellow', self.state))

    def activateCall(self, function):
        state_entity = getattr(self, self.state)
        function(state_entity, self.state)

    def __str__(self):
        return f'prod - {textColor("purple", self.name.upper())}'


class FilterDict(dict):
    def __init__(self, input_dict):
        for key, value in input_dict.iteritems():
            self[key] = value

    def filter(self, criteria):
        for key, value in self.items():
            if (criteria(value)):
                self.pop(key)


class card(object):
    _uid = 0

    def __init__(self, initial_data, secondary_data):
        for key, value in initial_data.items():
            setattr(self, key, value)
        for k, v in secondary_data.items():
            setattr(self, k, v)
        self.uid = card._uid
        card._uid += 1
        self.maxhealth = self.health
        self.onPlay = 0
        self.target = []


    def __str__(self):
        return f'({self.name} {self.location} {self.index} {self.owner} {self.type})'

    def activateCall(self, triggerStr, function):
        try:
            function(self, triggerStr, self.effect)
        except AttributeError:
            print(textColor('red', 'no effect encoded'), self, triggerStr)
            pass

    def changeLocation(self, destination, director):
        origin = deepcopy(self.location)
        #index is positioning in current location
        self.index = director.moveActor(destination, origin, self)

    def modifyValue(self, variable, value, operator):
        modifier(self, variable, value, operator)


class nexus(object):
    _uid = 0

    def __init__(self, owner):
        nexus._uid += 1
        self.name = 'default hendrix'
        self.health = 20
        self.maxhealth = 20
        self.mana = 10
        self.maxmana = 10
        self.maxmanagem = 3
        self.managem = 0
        self.owner = owner
        self.rally = 0
        self.type = 'nexus'
        self.region1 = 'Ionia'
        self.region2 = 'Demacia'

    def modifyValue(self, variable, value, operator):
        modifier(self, variable, value, operator)


class spielberg(object):
    _uid = 0

    def __init__(self):
        print('_init_ created object director')
        self.cue = Cue('')
        self.roster = {'card': {}, 'nexus': {}}
        self.triggerDirectory = {}
        self.overrideDirectory = {}
        self.constitution = {}
        self.location = {}
        self.producer = producer(self)
        self.deck2 = 'CEBQUAQGAQEAWFA2DQQCMLJ2AIBAGAYIAEAQGAQAAEAQCAZT'
        self.deck1 = 'CECAOAIEAEEBSHBUGY5ACAIBCYBQEAICAYFACAQEBIAQCAYECIBACAQEAMAQEAII'

    def modifyValue(self, variable, value, operator):
        modifier(self, variable, value, operator)

    def printStack(self, stack):
        for item in getattr(self, stack):
            print(item)

    def moveActor(self, destination, origin, entity):
        '''
        Sets location of entity in domain + space. Returns index in current domain.
        1. Appends uid of entity to current d + s.
        2. If domain does not exist, yet create, then perform 1.and
        3. Remove entity from previous d + s.
        4. Return index in current d + s.
        '''
        uid = entity.uid
        owner = entity.owner
        try:
            self.location[owner][destination].append(uid)
        except KeyError:
            self.location[owner][destination] = []
            self.location[owner][destination].append(uid)
        self.location[owner][origin].remove(uid)
        return self.location[owner][destination].index(uid)

    def createActor(self, dictVal):
        def birthingPod():
            destination = dictVal['location']
            owner = dictVal['owner']
            # copy method
            try:
                dictVal['method'] == 'copy'
                x = deepcopy(dictVal['reference'])
            except KeyError:
                x = card(db[dictVal['cardCode']], dictVal)
            # add to card database
            self.roster['card'].update({x.uid: x})
            # 'set origin'
            try:
                x.creator = dictVal['origin'].name
            except KeyError:
                x.creator = 'init'
            # 'add to location database'
            try:
                self.location[owner][destination].append(x.uid)
            except KeyError:
                self.location[owner][destination] = []
                self.location[owner][destination].append(x.uid)
            x.index = self.location[owner][destination].index(x.uid)
            return x
        def addListenersVariables(x):
            try:
                #set listener
                for condition in x.effect['condition']:
                    self.createSubscriber(x, condition)
                #set variables
                for variable in x.effect['variable']:
                    if variable['entity'] == 'player':
                        player = [v for k, v in self.roster['nexus'].items()
                                  if v.owner == 'self'][0]
                        setattr(player, variable['name'], variable['init_val'])
                    elif variable['entity'] == 'unit':
                        setattr(x, variable['name'], variable['init_val'])
            except AttributeError: # no effect
                pass
            except KeyError: # no condition
                pass
        x = birthingPod()
        addListenersVariables(x)
        return x

    def createSubscriber(self, entity, condition):
        if 'trigger' in condition:
            directory = self.triggerDirectory
            trigger = condition['trigger']
        elif 'negate' in condition:
            directory = self.overrideDirectory
            trigger = condition['negate']
        else:
            return
        try:
            if entity not in directory[trigger]:
                directory[trigger].append(entity)
        except KeyError:
            directory[trigger] = [entity]

    def createPlayer(self, owner):
        x = nexus(owner)
        self.roster['nexus'].update({x._uid: x})
        self.location.update({owner: {}})
