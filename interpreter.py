#!/usr/bin/env python3
"""
SCRIPTOR Interpreter
Parses and executes .scp files written in Hollywood screenplay syntax.
"""

import sys
import re
from typing import Any


# ─── Lexer ────────────────────────────────────────────────────────────────────

TOKEN_PATTERNS = [
    ("STRING",          r'"[^"]*"'),
    ("NUMBER",          r'-?\d+(\.\d+)?'),
    ("BOOL",            r'\b(VILLAIN_TRUE|VILLAIN_FALSE)\b'),
    ("KEYWORD",         r'\b(SCRIPT|DIRECTOR\'S CUT|OPENING CREDITS|FADE OUT'
                        r'|SCENE|CHARACTER|AS|HERO|NARRATOR|VILLAIN|EXTRA'
                        r'|SAYS|SHOUTS|LINE|MEANWHILE|OTHERWISE'
                        r'|MONTAGE|FROM|TO|END MONTAGE'
                        r'|CUT TO|CAST|PLOT TWIST|SEQUEL TO|FLASHBACK'
                        r'|RETURN)\b'),
    ("COLON",           r':'),
    ("LPAREN",          r'\('),
    ("RPAREN",          r'\)'),
    ("COMMA",           r','),
    ("OP",              r'[+\-*/%]'),
    ("CMP",             r'(==|!=|<=|>=|<|>)'),
    ("ASSIGN",          r'='),
    ("IDENT",           r'[A-Za-z_][A-Za-z0-9_]*'),
    ("NEWLINE",         r'\n'),
    ("SKIP",            r'[ \t]+'),
    ("COMMENT",         r'#[^\n]*'),
    ("DOT",             r'\.'),
    ("MISMATCH",        r'.'),
]

# Build the master regex, preserving multi-word keyword order
_MASTER = '|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_PATTERNS)
_RE = re.compile(_MASTER)


def tokenize(source: str):
    tokens = []
    for m in _RE.finditer(source):
        kind = m.lastgroup
        value = m.group()
        if kind in ("SKIP", "COMMENT", "NEWLINE", "DOT"):
            continue
        if kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character: {value!r}")
        if kind == "STRING":
            value = value[1:-1]  # strip quotes
        if kind == "BOOL":
            value = value == "VILLAIN_TRUE"
        if kind == "NUMBER":
            value = float(value) if '.' in value else int(value)
        tokens.append((kind, value))
    tokens.append(("EOF", None))
    return tokens


# ─── Parser ───────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return ("EOF", None)

    def current(self):
        return self.peek(0)

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect_keyword(self, *words):
        kind, val = self.current()
        if kind == "KEYWORD" and val in words:
            return self.advance()
        raise SyntaxError(f"Expected keyword {words}, got {kind}:{val!r} at token {self.pos}")

    def expect_kind(self, kind):
        k, v = self.current()
        if k != kind:
            raise SyntaxError(f"Expected {kind}, got {k}:{v!r} at token {self.pos}")
        return self.advance()

    def match_keyword(self, *words):
        kind, val = self.current()
        return kind == "KEYWORD" and val in words

    def match_kind(self, kind):
        return self.current()[0] == kind

    # ── Top-level ──────────────────────────────────────────────────────────────

    def parse_program(self):
        self.expect_keyword("SCRIPT")
        self.expect_kind("COLON")
        title = self._collect_ident_or_string()

        opening_credits = []
        scenes = {}
        director_cut = []

        while not self.match_kind("EOF"):
            if self.match_keyword("OPENING CREDITS"):
                self.advance()
                opening_credits = self.parse_block()
            elif self.match_keyword("SCENE"):
                name, params, body = self.parse_scene()
                scenes[name] = (params, body)
            elif self.match_keyword("DIRECTOR'S CUT"):
                self.advance()
                director_cut = self.parse_block()
            elif self.match_keyword("FADE OUT"):
                self.advance()
                break
            else:
                self.advance()  # skip unknown top-level tokens

        return {
            "title": title,
            "opening_credits": opening_credits,
            "scenes": scenes,
            "director_cut": director_cut,
        }

    def _collect_ident_or_string(self):
        parts = []
        while self.match_kind("IDENT") or self.match_kind("STRING"):
            _, v = self.advance()
            parts.append(str(v))
        return " ".join(parts) if parts else ""

    def _collect_scene_name(self):
        """Collect a possibly multi-word scene name (stops at LPAREN or keyword)."""
        parts = []
        while self.match_kind("IDENT"):
            _, v = self.advance()
            parts.append(v)
        return " ".join(parts)

    # ── Scene ──────────────────────────────────────────────────────────────────

    def parse_scene(self):
        self.expect_keyword("SCENE")
        self.expect_kind("COLON")
        name = self._collect_scene_name()

        params = []
        if self.match_kind("LPAREN"):
            self.advance()
            if self.match_keyword("CAST"):
                self.advance()
                self.expect_kind("COLON")
                params = self.parse_param_list()
            self.expect_kind("RPAREN")

        body = self.parse_block()
        return name, params, body

    def parse_param_list(self):
        params = []
        while True:
            pname = self.expect_kind("IDENT")[1].strip()
            self.expect_keyword("AS")
            ptype = self.advance()[1]
            params.append((pname, ptype))
            if not self.match_kind("COMMA"):
                break
            self.advance()
        return params

    # ── Block ──────────────────────────────────────────────────────────────────

    def parse_block(self):
        stmts = []
        stop = {
            "SCENE", "DIRECTOR'S CUT", "OPENING CREDITS",
            "FADE OUT", "OTHERWISE", "END MONTAGE",
        }
        while not self.match_kind("EOF"):
            kind, val = self.current()
            if kind == "KEYWORD" and val in stop:
                break
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    # ── Statement ──────────────────────────────────────────────────────────────

    def parse_statement(self):
        kind, val = self.current()

        if kind == "KEYWORD":
            if val == "CHARACTER":
                return self.parse_character()
            if val == "MEANWHILE":
                return self.parse_meanwhile()
            if val == "MONTAGE":
                return self.parse_montage()
            if val == "CUT TO":
                return self.parse_cut_to()
            if val == "SAYS":
                return self.parse_bare_says()
            if val == "SHOUTS":
                return self.parse_bare_shouts()
            if val == "PLOT TWIST":
                return self.parse_plot_twist()
            if val == "RETURN":
                self.advance()
                expr = self.parse_expr()
                return ("return", expr)
            # skip unrecognised keywords
            self.advance()
            return None

        if kind == "IDENT":
            # Could be: <var> SAYS LINE | <var> SAYS <expr> | <var> = <expr>
            return self.parse_ident_stmt()

        self.advance()
        return None

    def parse_character(self):
        self.expect_keyword("CHARACTER")
        name = self.expect_kind("IDENT")[1].strip()
        self.expect_keyword("AS")
        typ = self.advance()[1]
        value = None
        if self.match_kind("ASSIGN"):
            self.advance()
            value = self.parse_expr()
        return ("declare", name, typ, value)

    def parse_meanwhile(self):
        self.expect_keyword("MEANWHILE")
        condition = self.parse_condition()
        body = self.parse_block()
        else_body = []
        if self.match_keyword("OTHERWISE"):
            self.advance()
            else_body = self.parse_block()
        return ("if", condition, body, else_body)

    def parse_montage(self):
        self.expect_keyword("MONTAGE")
        var = self.expect_kind("IDENT")[1].strip()
        self.expect_keyword("FROM")
        start = self.parse_atom()
        self.expect_keyword("TO")
        end = self.parse_atom()
        body = self.parse_block()
        if self.match_keyword("END MONTAGE"):
            self.advance()
        return ("montage", var, start, end, body)

    def parse_cut_to(self):
        self.expect_keyword("CUT TO")
        name_parts = []
        while self.match_kind("IDENT"):
            _, v = self.advance()
            name_parts.append(v)
        name = " ".join(name_parts)
        args = []
        if self.match_kind("LPAREN"):
            self.advance()
            if not self.match_kind("RPAREN"):
                args.append(self.parse_expr())
                while self.match_kind("COMMA"):
                    self.advance()
                    args.append(self.parse_expr())
            self.expect_kind("RPAREN")
        return ("call", name, args)

    def parse_bare_says(self):
        self.expect_keyword("SAYS")
        expr = self.parse_expr()
        return ("says", None, expr)

    def parse_bare_shouts(self):
        self.expect_keyword("SHOUTS")
        expr = self.parse_expr()
        return ("shouts", None, expr)

    def parse_plot_twist(self):
        self.expect_keyword("PLOT TWIST")
        try_body = self.parse_block()
        catch_body = []
        if self.match_keyword("OTHERWISE"):
            self.advance()
            catch_body = self.parse_block()
        return ("plot_twist", try_body, catch_body)

    def parse_ident_stmt(self):
        _, name = self.advance()
        name = name.strip()

        if self.match_keyword("SAYS"):
            self.advance()
            if self.match_keyword("LINE"):
                self.advance()
                return ("says", name, ("ident", name))
            expr = self.parse_expr()
            return ("says", name, expr)

        if self.match_keyword("SHOUTS"):
            self.advance()
            if self.match_keyword("LINE"):
                self.advance()
                return ("shouts", name, ("ident", name))
            expr = self.parse_expr()
            return ("shouts", name, expr)

        if self.match_kind("ASSIGN"):
            self.advance()
            expr = self.parse_expr()
            return ("assign", name, expr)

        return None

    # ── Expressions ────────────────────────────────────────────────────────────

    def parse_condition(self):
        left = self.parse_atom()
        if self.match_kind("CMP"):
            op = self.advance()[1]
            right = self.parse_atom()
            return ("cmp", op, left, right)
        return left

    def parse_expr(self):
        left = self.parse_atom()
        while self.match_kind("OP"):
            op = self.advance()[1]
            right = self.parse_atom()
            left = ("binop", op, left, right)
        return left

    def parse_atom(self):
        kind, val = self.current()
        if kind == "NUMBER":
            self.advance()
            return ("lit", val)
        if kind == "STRING":
            self.advance()
            return ("lit", val)
        if kind == "BOOL":
            self.advance()
            return ("lit", val)
        if kind == "IDENT":
            self.advance()
            name = val.strip()
            if self.match_kind("LPAREN"):
                self.advance()
                args = []
                if not self.match_kind("RPAREN"):
                    args.append(self.parse_expr())
                    while self.match_kind("COMMA"):
                        self.advance()
                        args.append(self.parse_expr())
                self.expect_kind("RPAREN")
                return ("call_expr", name, args)
            return ("ident", name)
        if kind == "KEYWORD" and val == "LINE":
            self.advance()
            return ("lit", "LINE")
        raise SyntaxError(f"Unexpected token in expr: {kind}:{val!r} at {self.pos}")


# ─── Interpreter ──────────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.globals = {}
        self.scenes = ast["scenes"]
        self.output = []

    def run(self):
        self._print_header()
        # Execute OPENING CREDITS (global scope)
        for stmt in self.ast["opening_credits"]:
            self._exec(stmt, self.globals)
        # Execute DIRECTOR'S CUT
        for stmt in self.ast["director_cut"]:
            self._exec(stmt, self.globals)
        self._print_footer()

    def _print_header(self):
        title = self.ast.get("title", "Untitled")
        print(f"\n{'='*50}")
        print(f"  SCRIPT: {title}")
        print(f"{'='*50}\n")

    def _print_footer(self):
        print(f"\n{'='*50}")
        print("  FADE OUT.")
        print(f"{'='*50}\n")

    # ── Scope helpers ──────────────────────────────────────────────────────────

    def _resolve(self, name, local):
        if name in local:
            return local[name]
        if name in self.globals:
            return self.globals[name]
        raise NameError(f"Unknown character: {name!r}")

    # ── Eval ──────────────────────────────────────────────────────────────────

    def _eval(self, expr, local):
        kind = expr[0]

        if kind == "lit":
            return expr[1]

        if kind == "ident":
            return self._resolve(expr[1], local)

        if kind == "binop":
            _, op, l, r = expr
            lv = self._eval(l, local)
            rv = self._eval(r, local)
            if op == '+':
                return lv + rv
            if op == '-':
                return lv - rv
            if op == '*':
                return lv * rv
            if op == '/':
                return lv / rv
            if op == '%':
                return lv % rv

        if kind == "cmp":
            _, op, l, r = expr
            lv = self._eval(l, local)
            rv = self._eval(r, local)
            ops = {'==': lv == rv, '!=': lv != rv,
                   '<':  lv < rv,  '>':  lv > rv,
                   '<=': lv <= rv, '>=': lv >= rv}
            return ops[op]

        if kind == "call_expr":
            _, name, args = expr
            return self._call_scene(name, args, local)

        raise ValueError(f"Unknown expr kind: {kind}")

    # ── Exec ──────────────────────────────────────────────────────────────────

    def _exec(self, stmt, local):
        kind = stmt[0]

        if kind == "declare":
            _, name, typ, value_expr = stmt
            value = self._eval(value_expr, local) if value_expr is not None else None
            local[name] = value

        elif kind == "assign":
            _, name, value_expr = stmt
            value = self._eval(value_expr, local)
            if name in local:
                local[name] = value
            elif name in self.globals:
                self.globals[name] = value
            else:
                local[name] = value

        elif kind == "says":
            _, speaker, expr = stmt
            value = self._eval(expr, local)
            if speaker:
                print(f"  {speaker}: \"{value}\"")
            else:
                print(f"  {value}")

        elif kind == "shouts":
            _, speaker, expr = stmt
            value = self._eval(expr, local)
            sys.stdout.flush()
            if speaker:
                print(f"  !! {speaker}: \"{value}\" !!", file=sys.stderr)
            else:
                print(f"  !! {value} !!", file=sys.stderr)

        elif kind == "if":
            _, condition, body, else_body = stmt
            result = self._eval(condition, local)
            if result:
                for s in body:
                    self._exec(s, local)
            else:
                for s in else_body:
                    self._exec(s, local)

        elif kind == "montage":
            _, var, start_expr, end_expr, body = stmt
            start = self._eval(start_expr, local)
            end = self._eval(end_expr, local)
            step = 1 if start <= end else -1
            for i in range(int(start), int(end) + step, step):
                local[var] = i
                for s in body:
                    self._exec(s, local)

        elif kind == "call":
            _, name, args = stmt
            self._call_scene(name, args, local)

        elif kind == "plot_twist":
            _, try_body, catch_body = stmt
            try:
                for s in try_body:
                    self._exec(s, local)
            except Exception as e:
                local["_error"] = str(e)
                for s in catch_body:
                    self._exec(s, local)

        elif kind == "return":
            _, expr = stmt
            raise ReturnSignal(self._eval(expr, local))

    # ── Scene call ─────────────────────────────────────────────────────────────

    def _call_scene(self, name, arg_exprs, caller_local):
        if name not in self.scenes:
            raise NameError(f"No SCENE named: {name!r}")
        params, body = self.scenes[name]
        # Local scope only contains params; globals are read via _resolve
        # and written back via _exec's assign logic (which checks self.globals)
        local = {}
        for (pname, _ptype), arg_expr in zip(params, arg_exprs):
            local[pname] = self._eval(arg_expr, caller_local)
        try:
            for stmt in body:
                self._exec(stmt, local)
        except ReturnSignal as r:
            return r.value
        return None


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <file.scp>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)

    try:
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse_program()
        interp = Interpreter(ast)
        interp.run()
    except SyntaxError as e:
        print(f"[SCRIPTOR SYNTAX ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[SCRIPTOR RUNTIME ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
