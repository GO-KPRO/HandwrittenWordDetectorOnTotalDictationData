def getLevenshteinEditorialInstruction(str1, str2):
    n = len(str1)
    m = len(str2)
    prevList = [[x, 'i' * x] for x in range(n + 1)]
    curList = []
    for i in range(m):
        curList = [[i + 1, 'd' * (i + 1)]]
        for j in range(n):
            charEquality = 0
            editorialInstruction = 'm'
            if str1[j] != str2[i]:
                charEquality = 1
                editorialInstruction = 'r'
            insertChar = [curList[j][0] + 1, curList[j][1] + 'i']
            deleteChar = [prevList[j + 1][0] + 1, prevList[j + 1][1] + 'd']
            replaceOrMatchChar = [prevList[j][0] + charEquality, prevList[j][1] + editorialInstruction]
            curList.append(min(insertChar, deleteChar, replaceOrMatchChar, key=lambda x: x[0]))
        prevList = curList
    return curList[-1]


def align(str2, editorialInstruction):
    res = []
    counter1 = 0
    counter2 = 0
    for char in editorialInstruction:
        if char == 'm':
            res.append(str2[counter1])
            counter1 += 1
            counter2 += 1
        elif char == 'd':
            counter1 += 1
        elif char == 'i':
            res.append('i')
            counter2 += 1
        elif char == 'r':
            res.append('r')
            counter1 += 1
            counter2 += 1
    return res
