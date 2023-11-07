from tokenizer import TokenList


def main():
    inputFile = open("input.txt")
    testStr = inputFile.read()
    inputFile.close()
    testTokenList = TokenList(testStr)
    testTokenList.replaceTokensSimple()

    outputFile = open("output.txt", "w")
    outputFile.write(testTokenList.mergeTokens())
    outputFile.close()


if __name__ == "__main__":
    main()
