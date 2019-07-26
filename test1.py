
def get(msg: str, deep_lvl: int = 3, *args, **kwargs):
    final_index = []
    if '{}' in msg:
        print('Format msg found')
        if kwargs:
            colors = [str(c) for c in kwargs.values()]
            a_lens = [len(str(string)) for string in args]
            positions = [pos for pos, char in enumerate(msg) if char == '{']
            args_lens = 0
            for i in range(len(positions)):
                index = positions[i] + args_lens
                final_index.append((index, index+a_lens[i]))
                args_lens += a_lens[i]
            print(final_index)
    if len(final_index) == 0:
        return msg.format(*args)
    return msg.format(*args), final_index


message = ('Hi {}. Go to the {} or i will {}', 3)
arguments = ('Mike', 'river', 'go out')
kwarguments = {'c1': '#111', 'c2': '#222', 'c3': '#333'}

mess, pos = my_func(*message, *arguments, **kwarguments)

for p in pos:
    mess = mess[:p[0]] + '[' + mess[p[0]:]
    mess = mess[:p[1]+1] + ']' + mess[p[1]+1:]
print(mess)
