a='ㅁㄴㅇㄴㅁㅇㄹ123'

for i in a:
    print(f"영문 : {i} = {i.encode().isalpha()}")
    print(f"숫자 : {i} = {i.isnumeric()}")
