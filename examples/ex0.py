from typing import Tuple
from qlasskit import Int2, Int4, Int8, qlassf

def test() -> bool:
    return True 

def test(a: bool) -> bool:
    return a 

def test(a: bool) -> bool:
    return not a 

def test(a: bool, b: bool) -> bool:
    return not a and b

def test(a: bool, b: bool, c: bool) -> bool:
    return a and (not b) and c

def test(a: bool, b: bool, c: bool) -> bool:
    return a and (not b) and (a or c)

def test2(a: bool, b: bool, c: bool) -> bool:
    return True if a and (not b) and c else False

@qlassf
def test2(a: bool, b: bool, c: bool) -> bool:
    return (c and not b) if a and (not b) and c else (a and not c)

def test3(a: bool, b: bool, c: bool) -> bool:
    d = a and (not b) and c
    return True if d else False

def test4(a: bool, b: bool, c: bool) -> Tuple[bool,bool]:
    d = a and (not b) and c
    return True if d else False, False

def test5(a: Tuple[bool,bool]) -> bool:
    return True if a[0] and a[1] else False

def test6(a: Int2, b: bool) -> Int2:
    return True if a[0] and b else False

def test7(a: Int2, b: bool) -> bool:
    return True if a[5] and b else False

def test8(a: Int2) -> bool:
    return a == 1

def test9(a: Int8) -> bool:
    return a == 42

def test10() -> Int8:
    return 42

def test11(a: Int2) -> Int2:
    return a + 1

def test12(a: bool) -> Int8:
    return 42 if a else 38
