from tokenizer import TokenList


def main():
    inputFile = open("input.txt")
    inputStr = inputFile.read()
    inputFile.close()
    testTokenList = TokenList(inputStr)

    # get filters seperated by ',', and remove all whitespaces
    filterFile = open("filters.txt")
    filters = ["".join(e.split()) for e in filterFile.read().split(",")]
    filterFile.close()
    testTokenList.replaceTokensFilter(filters)

    outputFile = open("output.txt", "w")
    outputFile.write(testTokenList.mergeTokens())
    outputFile.close()


if __name__ == "__main__":
    main()
