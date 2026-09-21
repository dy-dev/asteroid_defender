# loops.py — Slow-motion loop interpreter for student_loops.py
# ---------------------------------------------------------------
# Parses the student file, finds while/for loops inside event blocks,
# and executes them ONE ITERATION PER CALL (one per game frame).
# The student writes standard Python; the engine runs it in slow motion.
# break and continue are handled via AST transformation (flag injection).

import ast
import os

MAX_ITERATIONS = 1000


class _BreakContinueTransformer(ast.NodeTransformer):
    """Injects __break__=True before break and __continue__=True before
    continue, so the slow-loop engine can detect them after exec."""
    def visit_Break(self, node):
        flag = ast.Assign(
            targets=[ast.Name(id='__break__', ctx=ast.Store())],
            value=ast.Constant(value=True),
            lineno=node.lineno, col_offset=node.col_offset)
        return [flag, node]

    def visit_Continue(self, node):
        flag = ast.Assign(
            targets=[ast.Name(id='__continue__', ctx=ast.Store())],
            value=ast.Constant(value=True),
            lineno=node.lineno, col_offset=node.col_offset)
        return [flag, node]


def _compile_body(body_stmts, source_path="<loop-body>"):
    """Compile a list of AST statements as a loop body.
    Wraps in 'for __once__ in [None]: ...' so break/continue are legal.
    Transforms break/continue to set detection flags.
    source_path: real file path so debuggers can set breakpoints."""
    tree = ast.Module(body=body_stmts, type_ignores=[])
    tree = _BreakContinueTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    # wrap in for __once__ in [None]: <body>
    wrapper_src = "for __once__ in [None]:\n    pass"
    wrapper = ast.parse(wrapper_src)
    wrapper.body[0].body = tree.body
    ast.fix_missing_locations(wrapper)
    return compile(wrapper, source_path, "exec")


class SlowLoop:
    """One loop extracted from the student file, stepped one iteration
    at a time by the engine."""

    def __init__(self, kind, test_code=None, body_code=None,
                 iter_target=None, loop_var=None):
        self.kind = kind
        self.test_code = test_code
        self.body_code = body_code
        self.iter_target = iter_target
        self.loop_var = loop_var
        self.active = False
        self.iterator = None
        self.iterations = 0
        self.finished = False
        self.error = None

    def start(self, namespace):
        self.active = True
        self.finished = False
        self.iterations = 0
        self.error = None
        namespace["__break__"] = False
        namespace["__continue__"] = False
        if self.kind == "for":
            try:
                iterable = eval(self.iter_target, namespace)
                self.iterator = iter(iterable)
            except Exception as e:
                self.error = str(e)
                self._stop()

    def step(self, namespace):
        """Execute ONE iteration. Returns True if loop continues."""
        if self.finished or not self.active:
            return False
        if self.iterations >= MAX_ITERATIONS:
            self.error = f"Loop exceeded {MAX_ITERATIONS} iterations (infinite loop?)"
            self._stop()
            return False
        try:
            namespace["__break__"] = False
            namespace["__continue__"] = False

            if self.kind == "while":
                if not eval(self.test_code, namespace):
                    self._stop()
                    return False
                exec(self.body_code, namespace)
                self.iterations += 1
                if namespace.get("__break__"):
                    self._stop()
                    return False
                return True

            elif self.kind == "for":
                try:
                    val = next(self.iterator)
                except StopIteration:
                    self._stop()
                    return False
                namespace[self.loop_var] = val
                exec(self.body_code, namespace)
                self.iterations += 1
                if namespace.get("__break__"):
                    self._stop()
                    return False
                return True

        except Exception as e:
            self.error = f"Error in loop body: {e}"
            self._stop()
            return False

    def stop(self):
        self._stop()

    def _stop(self):
        self.finished = True
        self.active = False


class SlowLoopEngine:
    """Parses student_loops.py and manages slow-motion loop execution."""

    SAFE_BUILTINS = {"range": range, "len": len, "int": int, "float": float,
                     "str": str, "True": True, "False": False, "None": None,
                     "abs": abs, "min": min, "max": max, "print": print}

    def __init__(self, path="student_loops.py"):
        self.path = path
        self.loops = {}
        self.namespace = {}
        self.mtime = 0
        self._last_error = None
        self._parse()

    def _parse(self):
        if not os.path.exists(self.path):
            return
        try:
            mtime = os.path.getmtime(self.path)
            if mtime == self.mtime:
                return
            self.mtime = mtime
            source = open(self.path, encoding="utf-8").read()
            tree = ast.parse(source)
        except SyntaxError as e:
            self.loops = {}
            self._last_error = f"Syntax error line {e.lineno}: {e.msg}"
            return

        self._last_error = None
        self.loops = {}
        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, ast.If):
                continue
            event_name = self._extract_event_name(node.test)
            if event_name is None:
                continue
            for child in node.body:
                if isinstance(child, ast.While):
                    loop = self._make_while(child)
                    if loop:
                        self.loops[event_name] = loop
                    break
                elif isinstance(child, ast.For):
                    loop = self._make_for(child)
                    if loop:
                        self.loops[event_name] = loop
                    break

    def _extract_event_name(self, test_node):
        if not isinstance(test_node, ast.Compare):
            return None
        if len(test_node.ops) != 1 or not isinstance(test_node.ops[0], ast.Eq):
            return None
        left = test_node.left
        if not (isinstance(left, ast.Name) and left.id == "event"):
            return None
        if len(test_node.comparators) != 1:
            return None
        comp = test_node.comparators[0]
        if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
            return comp.value
        return None

    def _make_while(self, node):
        try:
            test_code = compile(ast.Expression(body=node.test), self.path, "eval")
            body_code = _compile_body(node.body, self.path)
            return SlowLoop("while", test_code=test_code, body_code=body_code)
        except Exception:
            return None

    def _make_for(self, node):
        try:
            if not isinstance(node.target, ast.Name):
                return None
            loop_var = node.target.id
            iter_code = compile(ast.Expression(body=node.iter), self.path, "eval")
            body_code = _compile_body(node.body, self.path)
            return SlowLoop("for", iter_target=iter_code, body_code=body_code,
                           loop_var=loop_var)
        except Exception:
            return None

    def reload_if_changed(self):
        self._parse()

    def start_event(self, event_name, injected_state):
        self.reload_if_changed()
        if event_name not in self.loops:
            return False
        self.namespace = {"__builtins__": self.SAFE_BUILTINS}
        self.namespace.update(injected_state)
        self.namespace["event"] = event_name
        self.loops[event_name].start(self.namespace)
        return True

    def step_event(self, event_name):
        if event_name not in self.loops:
            return False, {}
        running = self.loops[event_name].step(self.namespace)
        return running, self.namespace

    def stop_event(self, event_name):
        if event_name in self.loops:
            self.loops[event_name].stop()

    def get_output(self, event_name, key, default=None):
        return self.namespace.get(key, default)

    def get_error(self, event_name):
        if event_name in self.loops:
            return self.loops[event_name].error
        return self._last_error

    def is_active(self, event_name):
        return event_name in self.loops and self.loops[event_name].active
