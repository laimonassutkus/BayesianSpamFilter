from __future__ import division
from collections import Counter
import os
import re
import pickle

# path to directory which contains files that are marked as not spam
pathToNotSpam = "./../not_spam"

# path to directory which contains files that are marked as spam
pathToSpam = "./../spam"

# path to a file to be checked if it is spam or not
pathToFileValidation = "./mix.txt"

# path to serialized word table with spam probabilities (path or "-")
pathToSerializedTable = "./wordtable.p"

# number of words to consider when calculating files "spaminess"
numberOfWords = 100

# ignore words that have spam rating of 0 percent or 100 percent (y, n)
ignoreExtremum = True


def parseFile(pathToFile):
    lines = open(pathToFile, "r").read().splitlines()
    words = filter(lambda s: s, [filter(lambda s: s != "", re.split("[^a-zA-Z0-9\']", line)) for line in lines])
    return words

if pathToSerializedTable == "-":
    def getCounts(pathToFiles):
        wordTable = []
        for fileName in os.listdir(pathToFiles):
            wordTable.append(parseFile(pathToFiles + fileName))
        wordTable = Counter(sum([sum(lines, []) for lines in wordTable], []))
        return wordTable


    spamTable = getCounts(pathToSpam)
    nonSpamTable = getCounts(pathToNotSpam)

    allWords = list(set(spamTable.keys()) | set(nonSpamTable.keys()))

    pSpamTable = {key: value / len(allWords) for key, value in {key: spamTable[key] for key in allWords}.iteritems()}
    pNonSpamTable = {key: value / len(allWords) for key, value in {key: nonSpamTable[key] for key in allWords}.iteritems()}

    probOfSpam = {key: pSpamTable[key] / (pSpamTable[key] + pNonSpamTable[key]) for key in allWords}
    pickle.dump(probOfSpam, open("./wordtable.p", "wb"))
else:
    probOfSpam = pickle.load(open("./" + pathToSerializedTable, "rb"))

checkedFileWords = sum(parseFile(pathToFileValidation), [])
checkedFileSpamProb = [probOfSpam[word] if word in probOfSpam else 0.40 for word in checkedFileWords]
checkedFileSpamProb.sort(reverse=True)

if ignoreExtremum:
    checkedFileSpamProb = [prob for prob in checkedFileSpamProb if prob != 0.0 and prob != 1.0][0:int(numberOfWords)]
else:
    checkedFileSpamProb = checkedFileSpamProb[0:numberOfWords]

oppositeCheckedFileSpamProb = [1 - self for self in checkedFileSpamProb]

spamProbabilityMultiplied = reduce(lambda x, y: x * y, checkedFileSpamProb)
oppositeCheckedFileSpamProbMultiplied = reduce(lambda x, y: x * y, oppositeCheckedFileSpamProb)

spamProbability = spamProbabilityMultiplied / (spamProbabilityMultiplied + oppositeCheckedFileSpamProbMultiplied)


print(spamProbability)