class test(object):
    def __init__(self):
        self.a = 1
        self.original_ = 2

x = test()
print([y for y in vars(x).keys() if y[:3] == 'ori'])
print(dict(filter(lambda x: x[0][:3] == 'ori', vars(x))))
x = 'create test'
print(x[7:])
