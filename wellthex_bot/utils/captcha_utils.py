import random

def generate_math_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    op = random.choice(['+', '-'])
    if op == '+':
        answer = a + b
    else:
        answer = a - b
    question = f"{a} {op} {b} = ?"
    return question, str(answer) 