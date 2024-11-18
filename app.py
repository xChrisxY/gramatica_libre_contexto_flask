from flask import Flask, render_template, request, jsonify
from lark import Lark, Transformer, v_args

app = Flask(__name__)

# Gramática para analizar expresiones matemáticas
grammar = """
    ?start: expr
    ?expr: term
        | expr "+" term   -> add
        | expr "-" term   -> sub
    ?term: factor
        | term "*" factor -> mul
        | term "/" factor -> div
    ?factor: NUMBER       -> number
        | "(" expr ")"
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

# Árbol generado por Lark
class TreeBuilder(Transformer):
    @v_args(inline=True)
    def number(self, n):
        return {"value": float(n), "left": None, "right": None}

    def add(self, args):
        return {"value": "+", "left": args[0], "right": args[1]}

    def sub(self, args):
        return {"value": "-", "left": args[0], "right": args[1]}

    def mul(self, args):
        return {"value": "*", "left": args[0], "right": args[1]}

    def div(self, args):
        return {"value": "/", "left": args[0], "right": args[1]}

# Instanciar Lark
parser = Lark(grammar, parser='lalr', transformer=TreeBuilder())

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        expression = request.form.get("expression")
        print(expression)
        try:
            # Parsear la expresión
            tree = parser.parse(expression)
            result = eval(expression)
            return jsonify({"result": result, "tree": tree})  # Enviar el árbol serializable
        except Exception as e:
            return jsonify({"error": str(e)})
    return render_template("index.html")

def evaluate(tree):
    if isinstance(tree, tuple):
        op, left, right = tree
        left_val = evaluate(left)
        right_val = evaluate(right)
        if op == "+":
            return left_val + right_val
        elif op == "-":
            return left_val - right_val
        elif op == "*":
            return left_val * right_val
        elif op == "/":
            return left_val / right_val
    else:
        return tree

if __name__ == "__main__":
    app.run(debug=True)