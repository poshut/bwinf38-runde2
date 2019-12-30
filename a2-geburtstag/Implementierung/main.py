import sys
import math
import argparse
from collections import defaultdict
from itertools import combinations_with_replacement
from queue import Queue

MAX_DIGITS = 100
FACTORIALS = {}

_i = 3
_fac = math.factorial(_i)
while len(str(_fac)) <= MAX_DIGITS:
    FACTORIALS[_fac] = _i
    _i += 1
    _fac = math.factorial(_i)
MAX_FACTORIAL = _i -1

class Term(object):

    def __init__(self):
       pass 

    def number_of_digits(self):
        return NotImplementedError()
    
    def value(self):
        return NotImplementedError()
    
    def __str__(self):
        return NotImplementedError()

    def __repr__(self):
        return str(self)


class Number(Term):

    def __init__(self, val):
        self.val = val
    
    def value(self):
        return self.val
    
    def number_of_digits(self):
        return len(str(self.val))
    
    def __str__(self):
        return str(self.val)

class UnaryOperation(Term):
    OP_FAC = 0
    OPERATIONS = [OP_FAC]

    def __init__(self, val, op):
        assert op in self.__class__.OPERATIONS
        self.val = val
        self.op = op
    
    def value(self):
        if self.op == UnaryOperation.OP_FAC:
            return math.factorial(self.val.value())
        return NotImplementedError()
    
    def number_of_digits(self):
        return self.val.number_of_digits()
    
    def __str__(self):
        return '({}!)'.format(self.val)


class BinaryOperation(Term):

    OP_ADD = 0
    OP_SUB = 1
    OP_MULT = 2
    OP_DIV = 3
    OP_POW = 4
    OPERATIONS = [OP_ADD, OP_SUB, OP_MULT, OP_DIV, OP_POW]

    def __init__(self, val1, val2, op):
        assert op in self.__class__.OPERATIONS
        self.val1 = val1
        self.val2 = val2
        self.op = op

    def value(self):
        if self.op == BinaryOperation.OP_ADD:
            return self.val1.value() + self.val2.value()
        elif self.op == BinaryOperation.OP_SUB:
            return self.val1.value() - self.val2.value()
        elif self.op == BinaryOperation.OP_MULT:
            return self.val1.value() * self.val2.value()
        elif self.op == BinaryOperation.OP_DIV:
            v1 = self.val1.value()
            v2 = self.val2.value()
            res = v1/v2
            resint = int(res)
            assert res == resint
            return resint
        elif self.op == BinaryOperation.OP_POW:
            return self.val1.value() ** self.val2.value()
        return NotImplementedError()

    def number_of_digits(self):
        return self.val1.number_of_digits() + self.val2.number_of_digits()
    
    def __str__(self):
        return '({}{}{})'.format(str(self.val1), self.opchar(), str(self.val2))
    
    def opchar(self):
        if self.op == BinaryOperation.OP_ADD:
            return '+'
        elif self.op == BinaryOperation.OP_SUB:
            return '-'
        elif self.op == BinaryOperation.OP_MULT:
            return '*'
        elif self.op == BinaryOperation.OP_DIV:
            return '/'
        elif self.op == BinaryOperation.OP_POW:
            return '^'
        return NotImplementedError()
        

def add_to_table(term, table, extended=False):
    val = term.value()
    if extended and val >= 3 and val <= MAX_FACTORIAL:
        add_to_table(UnaryOperation(term, UnaryOperation.OP_FAC), table, extended=extended)
    digits = term.number_of_digits()
    if val in table and table[val][1] < digits:
        return
    table[val] = (term, digits)


def generate(digit, num_digits, aggregated_table, split_table, extended, debug=False):

    current_split_table = split_table[num_digits]        

    # Add 3, 33, 333 etc
    num = int(str(digit)*num_digits)
    add_to_table(Number(num), current_split_table, extended)
    swap = False

    for op1_num_digits in range(1, num_digits // 2 + 1):
        op2_num_digits = num_digits - op1_num_digits
        for op1_k in split_table[op1_num_digits]:
            op1_v = split_table[op1_num_digits][op1_k][0]
            for op2_k in split_table[op2_num_digits]:
                op2_v = split_table[op2_num_digits][op2_k][0]
                # Make sure that op1_k > op2_k
                if op1_k < op2_k:
                    op1_k, op2_k = op2_k, op1_k
                    op1_v, op2_v = op2_v, op1_v
                    swap = True


                add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_ADD), current_split_table, extended)
                add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_SUB), current_split_table, extended)
                add_to_table(BinaryOperation(op2_v, op1_v, BinaryOperation.OP_SUB), current_split_table, extended)
                add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_MULT), current_split_table, extended)
                if extended and op1_k >= 2 and op2_k >= 2:
                    if op2_k * math.log(op1_k, 10) <= MAX_DIGITS:
                        add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_POW), current_split_table, extended)
                    if op1_k * math.log(op2_k, 10) <= MAX_DIGITS:
                        add_to_table(BinaryOperation(op2_v, op1_v, BinaryOperation.OP_POW), current_split_table, extended)

                if op2_k != 0:
                    res = op1_k / op2_k
                    resint = int(res)
                    if res == resint:
                        add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_DIV), current_split_table, extended)

                if swap:
                    op1_k, op2_k = op2_k, op1_k
                    op1_v, op2_v = op2_v, op1_v
                    swap = False
    if debug:
        print("generated split table with digits:", num_digits, file=sys.stderr)

    for k in split_table[num_digits]:
        if k not in aggregated_table:
            aggregated_table[k] = split_table[num_digits][k]
    return aggregated_table, split_table

def scan(number, digit, aggregated_table, extended):
    results = set()
    if number in aggregated_table:
        results.add(aggregated_table[number][0])

    for j in aggregated_table:
        if number - j in aggregated_table:
            results.add(BinaryOperation(aggregated_table[j][0], aggregated_table[number-j][0], BinaryOperation.OP_ADD))
        if number + j in aggregated_table:
            results.add(BinaryOperation(aggregated_table[number+j][0], aggregated_table[j][0], BinaryOperation.OP_SUB))
        if j - number in aggregated_table:
            results.add(BinaryOperation(aggregated_table[j][0], aggregated_table[j-number][0], BinaryOperation.OP_SUB))
        
        if j != 0:
            if (number*j) in aggregated_table:
                results.add(BinaryOperation(aggregated_table[number*j][0], aggregated_table[j][0], BinaryOperation.OP_DIV))
            
            res = j / number
            resint = int(res)
            if res == resint and resint in aggregated_table:
                results.add(BinaryOperation(aggregated_table[j][0], aggregated_table[resint][0], BinaryOperation.OP_DIV))
        
            res = number / j
            resint = int(res)
            if res == resint and resint in aggregated_table:
                results.add(BinaryOperation(aggregated_table[number/j][0], aggregated_table[j][0], BinaryOperation.OP_MULT))
        
        if extended and number > 1 and j > 1:
            res = number ** (1/j)
            if res in aggregated_table and res != 1.0:
                results.add(BinaryOperation(aggregated_table[res][0], aggregated_table[j][0], BinaryOperation.OP_POW))
            res = math.log(number, j)
            if res in aggregated_table:
                results.add(BinaryOperation(aggregated_table[j][0], aggregated_table[res][0], BinaryOperation.OP_POW))
        

    if extended and j >= 3 and j <= 60 and j in FACTORIALS:
        results.add(UnaryOperation(aggregated_table[FACTORIALS[j]][0], UnaryOperation.OP_FAC))
        

    if len(results) == 0:
        return None
    res = 0
    n = math.inf
    for r in results:
        nr = r.number_of_digits()
        if nr < n:
            res = r
            n = nr
    return res

def find_shortest(number, digit, extended, debug=False):
    aggregated_table = {}
    split_table = defaultdict(dict)

    i = 1
    res_n = math.inf

    # Generate tables until shortest result will be available with scan()
    while i <= res_n - 2:
        aggregated_table, split_table = generate(args.digit, i, aggregated_table, split_table, extended, debug=debug)
        res = scan(number, digit, aggregated_table, extended)
        if res is not None:
            res_n = res.number_of_digits()
            if debug:
            print("found", res, "with", res.number_of_digits(), "digits, looking if shorter is possible")
        i += 1
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Decompose a number into a term using one digit")
    parser.add_argument("number", help="number to decompose", type=int)
    parser.add_argument("digit", help="digit to decompose into", type=int)
    parser.add_argument("--verbose", "-v", help="enable verbose output", action='store_true')
    args = parser.parse_args()

    if len(str(args.digit)) != 1 or args.digit == 0:
        print("Error:", args.digit, "is not a digit, exiting...", file=sys.stderr)
        exit(1)

    if args.verbose:
        print("looking for normal shortest")
    res_normal = find_shortest(args.number, args.digit, False, args.verbose)

    if args.verbose:
    print()
        print("looking for extended shortest")
    res_extended = find_shortest(args.number, args.digit, True, args.verbose)

    if args.verbose:
        print()
    print("normal result", res_normal)
    print("digits:", res_normal.number_of_digits())

    print()
    print("extended result", res_extended)
    print("digits:", res_extended.number_of_digits())

