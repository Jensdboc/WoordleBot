count = 0

with open("data/wordlist.txt", "r") as orig:
    with open("data/bogglewords.txt", "w") as copy:
        lines = orig.readlines()
        for line in lines:
            line = line.rstrip()
            if line.isalpha() and " " not in line and len(line) > 2 and len(line) < 16:
                copy.write(line + "\n")

    print(len(lines))

with open("data/bogglewords.txt", "r") as copy:
    lines = copy.readlines()
    print(len(lines))
