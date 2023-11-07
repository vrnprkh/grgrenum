from enum import Enum

# constants
LPAREN = "("
RPAREN = ")"
ON_STRING = " on "


def getIDFromString(inputString: str) -> tuple[str, str, str]:
    end: str = inputString
    foundID: bool = False
    idStart: int = 0
    idEnd: int = 0
    for i in reversed(range(len(inputString) - 1)):
        e: str = inputString[i]
        if not foundID and e.isalnum():
            foundID = True
            idEnd = i + 1
        elif foundID and not e.isalnum():
            idStart = i + 1
            break
    start = end[:idStart]
    id = end[idStart:idEnd]
    end = end[idEnd:]

    return (start, id, end)


class TokenType(Enum):
    body = 0
    id = 1
    reference = 2
    comment = 3

    def __str__(self) -> str:
        return super().__str__()


class Token:
    def __init__(self, text: str, kind: TokenType) -> None:
        self.kind: TokenType = kind
        self.text: str = text


# helper to generate reference and body tokens from a string after onstring
def getReferences(searchText: str) -> list[Token]:
    # assume this is AFTER on string
    splits = ["-", ",", " "]
    newSearchText: str = ""
    lastText: str = ""
    for i, e in enumerate(searchText):
        if e.isalnum() or e in splits:
            pass
        else:
            lastText = searchText[i:]
            newSearchText = searchText[:i]
            break

    tokens: list[Token] = []
    currentTokenStr: str = ""
    for e in newSearchText:
        if e in splits:
            if len(currentTokenStr) > 0:
                tokens.append(Token(currentTokenStr, TokenType.reference))
            tokens.append(Token(e, TokenType.body))
            currentTokenStr = ""
        else:
            currentTokenStr += e
    if len(currentTokenStr) > 0:
        tokens.append(Token(currentTokenStr, TokenType.reference))

    tokens.append(Token(lastText, TokenType.body))
    return tokens


class TokenList:
    def __init__(self, inputString: str) -> None:
        self.tokens: list[Token] = []
        self.initIDtoPos: dict[str, int] = {}
        self.idPos: list[int] = []
        self.referencePos: list[int] = []
        self.tokenize(inputString)

    def tokenize(self, inputString: str) -> None:
        # first pass to find all IDS
        firstPassTokens: list[Token] = self.tokenizeFirstPass(inputString)
        # second pass to find all references
        self.tokenizeSecondPass(firstPassTokens)
        # fill our map and lists
        self.fillAll()

    def tokenizeFirstPass(self, inputString: str) -> list[Token]:
        # LParen - RParen so far
        newTokens: list[Token] = []
        netParens: int = 0
        currentToken: str = ""

        # comment filtering
        inSingleLineComment: bool = False
        inMultiLineComment: bool = False

        for char in inputString:
            currentToken += char

            # TEST
            if inSingleLineComment:
                if char == "\n":
                    inSingleLineComment = False
                    newTokens.append(Token(currentToken, TokenType.comment))
                    currentToken = ""
                continue
            if inMultiLineComment:
                if currentToken[-2:] == "*/":
                    inMultiLineComment = False
                    newTokens.append(Token(currentToken, TokenType.comment))
                    currentToken = ""
                continue

            # check for comment entering
            if len(currentToken) >= 2:
                lastTwo: str = currentToken[-2:]

                if lastTwo == "//":
                    inSingleLineComment = True
                elif lastTwo == "/*":
                    inMultiLineComment = True
                if inMultiLineComment or inSingleLineComment:
                    newTokens.append(Token(currentToken[:-2], TokenType.body))
                    currentToken = lastTwo
                    continue

            # not comments
            if char == LPAREN:
                netParens += 1
            elif char == RPAREN:
                netParens -= 1
            if netParens < 0:
                body, id, end = getIDFromString(currentToken)
                newTokens.append(Token(body, TokenType.body))
                newTokens.append(Token(id, TokenType.id))
                # reset
                netParens = 0
                currentToken = end
            pass

        if len(currentToken) > 0:
            if inSingleLineComment or inMultiLineComment:
                newTokens.append(Token(currentToken, TokenType.comment))
            else:
                newTokens.append(Token(currentToken, TokenType.body))

        return newTokens

    def tokenizeSecondPass(self, firstPassTokens: list[Token]) -> None:
        for token in firstPassTokens:
            if token.kind == TokenType.id or token.kind == TokenType.comment:
                self.tokens.append(token)
                continue
            # we assume it is a body type now
            if ON_STRING not in token.text:
                self.tokens.append(token)
                continue

            onStringPos: int = token.text.find(ON_STRING)
            newBodyText: str = token.text[0 : onStringPos + len(ON_STRING)]
            self.tokens.append(Token(newBodyText, TokenType.body))
            searchText: str = token.text[onStringPos + len(ON_STRING) :]
            # find references
            for searchedToken in getReferences(searchText):
                self.tokens.append(searchedToken)

    # fill idPos, referencePos, and dict
    def fillAll(self) -> None:
        # first fill idPos and referencePos
        for i, token in enumerate(self.tokens):
            if token.kind == TokenType.id:
                self.idPos.append(i)
            elif token.kind == TokenType.reference:
                self.referencePos.append(i)
        # fill dict
        for e in self.idPos:
            self.initIDtoPos[self.tokens[e].text] = e

    # replaces all ids in numeric order
    def replaceTokensSimple(self) -> None:
        count = 0
        for i in self.idPos:
            count += 1
            self.tokens[i].text = str(count)
        for i in self.referencePos:
            replacement: str = self.tokens[self.initIDtoPos[self.tokens[i].text]].text
            self.tokens[i].text = replacement

    def mergeTokens(self) -> str:
        merged: str = ""

        for token in self.tokens:
            merged += token.text

        return merged

    def __str__(self) -> str:
        # for debuggin
        outputStr: str = "TOKENS:\n"
        for token in self.tokens:
            outputStr += str(token.kind) + ": " + token.text + "\n"

        outputStr += "DICT: \n"
        for e in self.initIDtoPos:
            outputStr += e + " : " + str(self.initIDtoPos[e]) + "\n"

        outputStr += "REFRENCE POS: \n"
        for i in self.referencePos:
            outputStr += str(i) + ", "

        outputStr += "\nID POS: \n"
        for i in self.idPos:
            outputStr += str(i) + ", "

        return outputStr
