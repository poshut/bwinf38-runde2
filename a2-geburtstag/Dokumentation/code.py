def add_to_table(term, table, extended=False):
    """
    Fügt den gegebenen Term der gegebenen Tabelle hinzu.
    Wenn extended wahr, wird auch die Fakulätsfunktion gebildet und der Tabelle hinzugefügt.
    """
    val = term.value()
    if extended and val >= 3 and val <= MAX_FACTORIAL:
        add_to_table(UnaryOperation(term, UnaryOperation.OP_FAC), table, extended=extended)
    digits = term.number_of_digits()
    if val in table and table[val][1] < digits:
        return
    table[val] = (term, digits)


def generate(digit, num_digits, aggregated_table, split_table, extended, debug=False):
    """
    Erweitert die Tabelle und fügt alle Terme mit der gegebenen Anzahl an Ziffern hinzu.
    Falls extended, werden auch Fakultäts- und Potenzfunktionen gebildet.
    Falls debug, werden zusätzliche Informationen ausgegeben.
    """

    current_split_table = split_table[num_digits]        
    next_split_table = split_table[num_digits+1]

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
                    if math.floor(op2_k * math.log(op1_k, 10)) + 1 <= MAX_DIGITS:
                        add_to_table(BinaryOperation(op1_v, op2_v, BinaryOperation.OP_POW), current_split_table, extended)
                    if math.floor(op1_k * math.log(op2_k, 10)) + 1 <= MAX_DIGITS:
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

    # Add 3, 33, 333 etc. Scan mit m Ziffern erwartet, dass die Zahl, die m+1 mal die Ziffer enthält, bereits eingetragen ist.
    num = int(str(digit)*(num_digits+1))
    add_to_table(Number(num), next_split_table, extended)
    add_to_table(Number(num), aggregated_table, extended)


    return aggregated_table, split_table

def scan(number, digit, aggregated_table, extended):
    """
    Sucht für jeden Term der Tabelle nach einem Partner, mit dem zusammen durch eine Rechenoperation die gegebene Zahl number erhalten wird.
    Falls extended, werden auch Fakultäts- und Potenzfunktionen benutzt.
    """
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
        

    if extended and j >= 3 and j <= 60 and j in FACTORIALS and FACTORIALS[j] in aggregated_table:
        results.add(UnaryOperation(aggregated_table[FACTORIALS[j]][0], UnaryOperation.OP_FAC))
        

    if len(results) == 0:
        return None

    # Use term with fewest digits. If there are multiple terms with the same number of digits, use the one that has fewer characters
    res = 0
    n = math.inf
    c = math.inf
    for r in results:
        nr = r.number_of_digits()
        nc = len(str(res))
        if nr < n or (nr == n and nc < c):
            res = r
            n = nr
            c = nc
    return res

def find_shortest(number, digit, extended, debug=False):
    """
    Findet den kürzesten Term, der die Zahl number nur durch die Ziffer digit repräsentiert.
    Sucht für jeden Term der Tabelle nach einem Partner, mit dem zusammen durch eine Rechenoperation die gegebene Zahl number erhalten wird.
    Falls extended, werden auch Fakultäts- und Potenzfunktionen benutzt.
    """
    aggregated_table = {}
    split_table = defaultdict(dict)

    # Bei 0 beginnen, dass generate() die Ziffer als Zahl der Tabelle hinzufügt
    i = 0
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