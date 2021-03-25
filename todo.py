battle
    todo

create listener
when attack is commited
con:
    1 entity with pos board and index = self.index exists
    2 atk has double attack
    3 atk has quick attack
target:
    entity with pos board and index = self.index exists
    nexus oppo
effect 1
    false: 1
    modifyhp nexus oppo
effect 2
    false: 1, true: 2
    modifyhp nexus oppo
effect 3
    true: 1,2
    modifyhp def
effect 4
    true: 1,3
    modifyhp def
effect 5
    true: 1,3,4
    modifyhp atk
effect 6
    true: 1,2,4
    modifyhp def
effect 7
    true: 1, false: 2
    modifyhp def
    modifyhp atk


karma:
con:
    trigger: round_end
    onPlay
effect:
    create
