# エラーが起きた村を記録する
def get_error_number():
    with open('../error_number.txt', encoding='utf_8', mode='r') as f:
        r = f.read()
    return r.split('\n')

def add_error_number(n):
    with open('../error_number.txt', encoding='utf_8', mode='a') as f:
        f.write("\n"+str(n))
    return True

add_error_number(6)
print(get_error_number())