"""
CSCI-603 PreTee Lab
Author: RIT CS
Author: Bardh Rushiti
        Prakhar Gupta

The main program and class for a prefix expression interpreter of the
PreTee language.  See prog1.pre for a full example.

Usage: python3 pretee.py source-file.pre
"""

import sys  # argv
import literal_node  # literal_node.LiteralNode
import variable_node  # variable_node.VariableNode
import assignment_node  # assignment_node.AssignmentNode
import print_node  # print_node.PrintNode
import math_node  # math_node.MathNode
import syntax_error  # syntax_error.SyntaxError
import runtime_error  # runtime_error.RuntimeError


class PreTee:
    """
    The PreTee class consists of:
    :slot srcFile: the name of the source file (string)
    :slot symTbl: the symbol table (dictionary: key=string, value=int)
    :slot parseTrees: a list of the root nodes for valid, non-commented
        line of code
    :slot lineNum:  when parsing, the current line number in the source
        file (int)
    :slot syntaxError: indicates whether a syntax error occurred during
        parsing (bool).  If there is a syntax error, the parse trees will
        not be evaluated
    """
    __slots__ = 'srcFile', 'symTbl', 'parseTrees', 'lineNum', 'syntaxError'

    # the tokens in the language
    COMMENT_TOKEN = '#'
    ASSIGNMENT_TOKEN = '='
    PRINT_TOKEN = '@'
    ADD_TOKEN = '+'
    SUBTRACT_TOKEN = '-'
    MULTIPLY_TOKEN = '*'
    DIVIDE_TOKEN = '//'
    MATH_TOKENS = ADD_TOKEN, SUBTRACT_TOKEN, MULTIPLY_TOKEN, DIVIDE_TOKEN

    def __init__(self, srcFile):
        """
        Initialize the parser.
        :param srcFile: the source file (string)
        """
        self.srcFile = srcFile
        self.parseTrees = []
        self.symTbl = dict()
        self.lineNum = 0
        self.syntaxError = False

    def __parse(self, tokens):
        """
        The recursive parser that builds the parse tree from one line of
        source code.
        :param tokens: The tokens from the source line separated by whitespace
            in a list of strings.
        :exception: raises a syntax_error.SyntaxError with the message
            'Incomplete statement' if the statement is incomplete (e.g.
            there are no tokens left and this method was called).
        :exception: raises a syntax_error.SyntaxError with the message
            'Invalid token {token}' if an unrecognized token is
            encountered (e.g. not one of the tokens listed above).
        :return expression:
        """
        # Incomplete statement
        if len(tokens) < 1:
            self.syntaxError = True
            raise syntax_error.SyntaxError('Incomplete statement!')

        # Invalid token
        if not tokens[0].isdigit() and not tokens[0].isidentifier() and tokens[0] not in self.MATH_TOKENS:
            self.syntaxError = True
            raise syntax_error.SyntaxError(f'Invalid token {tokens[0]}')

        token = tokens.pop(0)
        # If it's a digit, creates a LiteralNode
        if token.isdigit():
            return literal_node.LiteralNode(token)
        # If it's a variable, creates a VariableNode
        elif token.isidentifier():
            return variable_node.VariableNode(token, self.symTbl)
        # Else it has to be a MathNode
        else:
            left = self.__parse(tokens)
            right = self.__parse(tokens)

            return math_node.MathNode(left, right, token)

    def parse(self):
        """
        The public parse is responsible for looping over the lines of
        source code and constructing the parseTree, as a series of
        calls to the helper function that are appended to this list.
        It needs to handle and display any syntax_error.SyntaxError
        exceptions that get raised.
        : return None
        """
        with open(self.srcFile) as f:
            lines = f.readlines()

            for line in lines:
                self.lineNum += 1

                # handle comments token and new lines
                if line.startswith(self.COMMENT_TOKEN) or line == "\n":
                    continue

                # handle assignment token
                elif line.startswith(self.ASSIGNMENT_TOKEN):
                    line = line.strip("\n").split(" ")

                    # Handle syntax_errors
                    try:
                        if len(line) == 1 or line[1].isdigit():
                            self.parseTrees.append(print_node.PrintNode())

                            self.syntaxError = True
                            raise syntax_error.SyntaxError(f"\n*** Syntax Error: "
                                                           f"Bad assignment to non-variable: Line {self.lineNum}")
                    except Exception as e:
                        print(e)
                        continue

                    # Handle syntax_errors
                    try:
                        expression = self.__parse(line[2:])
                    except Exception as e:
                        print(f"\n*** Syntax Error: {e}: Line {self.lineNum}")
                        continue
                    tree = assignment_node.AssignmentNode(variable_node.VariableNode(line[1], self.symTbl),
                                                          expression, self.symTbl, line[0])
                    self.parseTrees.append(tree)

                # Handles print token
                elif line.startswith(self.PRINT_TOKEN):
                    line = line.strip("\n").split(" ")

                    if len(line) == 1:
                        self.parseTrees.append(print_node.PrintNode())
                        continue

                    try:
                        expression = self.__parse(line[1:])
                    except Exception as e:
                        print(f"\n*** Syntax Error: {e}: Line {self.lineNum}")
                        continue
                    self.parseTrees.append(expression)

                # if it is neither, than it has to be an invalid token
                else:
                    # raise an exception
                    try:
                        self.syntaxError = True
                        raise syntax_error.SyntaxError(f"\n*** Syntax Error: Invalid token {line[0]}: Line {self.lineNum}")
                    except Exception as e:
                        print(e)
                        continue

    def emit(self):
        """
        Prints an infix string representation of the source code that
        is contained as root nodes in parseTree.
        :return None
        """
        for tree in self.parseTrees:
            print(print_node.PrintNode(tree).emit())

    def evaluate(self):
        """
        Prints the results of evaluating the root notes in parseTree.
        This can be viewed as executing the compiled code.  If a
        runtime error happens, execution halts.
        :exception: runtime_error.RunTimeError may be raised if a
            parse tree encounters a runtime error
        :return None
        """

        printInstance = print_node.PrintNode
        for tree in self.parseTrees:
            if tree.evaluate() is not None:
                printInstance(tree).evaluate()


def main():
    """
    The main function prompts for the source file, and then does:
        1. Compiles the prefix source code into parse trees
        2. Prints the source code as infix
        3. Executes the compiled code
    :return: None
    """
    if len(sys.argv) != 2:
        print('Usage: python3 pretee.py source-file.pre')
        return

    pretee = PreTee(sys.argv[1])
    print('PRETEE: Compiling', sys.argv[1] + '...')
    pretee.parse()
    print('\nPRETEE: Infix source...')
    pretee.emit()
    print('\nPRETEE: Executing...')
    try:
        pretee.evaluate()
    except runtime_error.RuntimeError as e:
        # on first runtime error, the supplied program will halt execution
        print('*** Runtime error:', e)


if __name__ == '__main__':
    main()
