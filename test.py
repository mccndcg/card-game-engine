from dataclasses import dataclass

@dataclass
class Test():
    pass

x = Test()
x.a = Test()
x.a.a = 5
print(x.a.a)
