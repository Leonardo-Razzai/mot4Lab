import re

def realign(line):
    words = line.split()
    if len(words) == 0:
        return '\n'
    
    if re.match(r"\+",words[0].strip()):
        time = words[0]
        return f"{time:<10} {' '.join(words[1:-1]):<60} {words[-1]}\n"
    elif re.match(r"\(\d+\)",words[-1].strip()):
        address=words[-1]
        return f"{' '.join(words[:-1]):<70} {address}\n"
    else:
        return ' '.join(words) + '\n'

def refactor_file(file):
    with open(file, 'r') as f:
        lines = f.readlines()
        f.close()
        
    with open(file, 'w') as f:
        for line in lines:
            f.write(realign(line))
        f.close()
        
if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    refactor_file(fname)
