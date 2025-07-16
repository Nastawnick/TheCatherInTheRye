# def decorator(func):
#     def wrapper(*args,**kwargs):
#         wrapper.has_exe = True
#         return func(*args,**kwargs)
#     wrapper.has_exe = False
#     return wrapper
#
# @decorator
# def a():
#     print(1)
# a = decorator(a)
# def b():
#     if a.has_exe:
#         print(2)
#     else:
#         print(3)
# a()
# b()

# def decorator(mode="default"):
#     def func(func):
#         def wrapper(*args, **kwargs):
#             if mode == "default":
#                 pass
#             elif mode == "custom":
#                 pass
#         return wrapper()

def decorator_b(mode="default"):
    def decorator(func_a):
        def wrapper(*args, **kwargs):
            func_a(*args, **kwargs)
            if mode == "default":
                print("Стандартное поведение Б")
            elif mode == "custom":
                print("Кастомное поведение Б")
        return wrapper
    return decorator

@decorator_b(mode="default")
def function_a():
    print("Функция А работает")

function_a()