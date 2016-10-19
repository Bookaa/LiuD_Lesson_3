
import re

class GDL01_main:
    def __init__(self, vlst):
        self.vlst = vlst
    def walkabout(self, visitor):
        return visitor.visit_main(self)

class GDL01_stmt:
    def __init__(self, v):
        self.v = v
    def walkabout(self, visitor):
        return visitor.visit_stmt(self)

class GDL01_datatype:
    def __init__(self, s):
        self.s = s
    def walkabout(self, visitor):
        return visitor.visit_datatype(self)

class GDL01_declare:
    def __init__(self, v, s):
        self.v = v
        self.s = s
    def walkabout(self, visitor):
        return visitor.visit_declare(self)

class GDL01_declare_with_value:
    def __init__(self, v1, s, v2):
        self.v1 = v1
        self.s = s
        self.v2 = v2
    def walkabout(self, visitor):
        return visitor.visit_declare_with_value(self)

class GDL01_value0:
    def __init__(self, s):
        self.s = s
    def walkabout(self, visitor):
        return visitor.visit_value0(self)

class GDL01_binvalue:
    def __init__(self, v1, s, v2):
        self.v1 = v1
        self.s = s
        self.v2 = v2
    def walkabout(self, visitor):
        return visitor.visit_binvalue(self)

class GDL01_value:
    def __init__(self, v):
        self.v = v
    def walkabout(self, visitor):
        return visitor.visit_value(self)

class GDL01_assign:
    def __init__(self, s, v):
        self.s = s
        self.v = v
    def walkabout(self, visitor):
        return visitor.visit_assign(self)

class GDL01_funccall:
    def __init__(self, s, v):
        self.s = s
        self.v = v
    def walkabout(self, visitor):
        return visitor.visit_funccall(self)

class Parser00:
    def __init__(self, txt):
        self.txt = txt
        self.pos = 0
    def handle_NAME(self):
        partn = '[A-Za-z_][A-Za-z0-9_]*'
        partn_compiled = re.compile(partn)
        m = partn_compiled.match(self.txt, self.pos)
        if m:
            content = m.group()
            self.pos = m.end()
            return content
        return None
    def handle_NUMBER(self):
        partn = r'0|[1-9]\d*'
        partn_compiled = re.compile(partn)
        m = partn_compiled.match(self.txt, self.pos)
        if m:
            content = m.group()
            self.pos = m.end()
            return content
        return None
    def handle_str(self, s):
        if self.txt[self.pos:].startswith(s):
            self.pos += len(s)
            return s
    def restorepos(self, pos):
        self.pos = pos
    def skipspacecrlf(self):
        while self.pos < len(self.txt) and self.txt[self.pos] in ' \n':
            self.pos += 1

class GDL01_Parser(Parser00):

    def handle_main(self):
        v = self.handle_stmt()
        if not v:
            return None
        savpos = self.pos
        vlst = [v]
        while True:
            self.skipspacecrlf()
            v = self.handle_stmt()
            if not v:
                break
            vlst.append(v)
            savpos = self.pos
        self.restorepos(savpos)
        return GDL01_main(vlst)

    def handle_stmt(self):
        v = self.handle_declare_with_value()
        if not v:
            v = self.handle_declare()
        if not v:
            v = self.handle_assign()
        if not v:
            v = self.handle_funccall()
        if not v:
            return None
        return GDL01_stmt(v)

    def handle_datatype(self):
        s = self.handle_str('int')
        if not s:
            s = self.handle_str('long')
        if not s:
            return None
        return GDL01_datatype(s)

    def handle_declare(self):
        savpos = self.pos
        v = self.handle_datatype()
        if not v:
            return None
        self.skipspacecrlf()
        s = self.handle_NAME()
        if not s:
            return self.restorepos(savpos)
        return GDL01_declare(v, s)

    def handle_declare_with_value(self):
        savpos = self.pos
        v1 = self.handle_datatype()
        if not v1:
            return None
        self.skipspacecrlf()
        s = self.handle_NAME()
        if not s:
            return self.restorepos(savpos)
        self.skipspacecrlf()
        if not self.handle_str('='):
            return self.restorepos(savpos)
        self.skipspacecrlf()
        v2 = self.handle_value()
        if not v2:
            return self.restorepos(savpos)
        return GDL01_declare_with_value(v1, s, v2)

    def handle_value0(self):
        s = self.handle_NUMBER()
        if not s:
            s = self.handle_NAME()
        if not s:
            return None
        return GDL01_value0(s)

    def handle_binvalue(self):
        savpos = self.pos
        v1 = self.handle_value0()
        if not v1:
            return None
        self.skipspacecrlf()
        s = self.handle_str('+')
        if not s:
            s = self.handle_str('-')
        if not s:
            return self.restorepos(savpos)
        self.skipspacecrlf()
        v2 = self.handle_value0()
        if not v2:
            return self.restorepos(savpos)
        return GDL01_binvalue(v1, s, v2)

    def handle_value(self):
        v = self.handle_binvalue()
        if not v:
            v = self.handle_value0()
        if not v:
            return None
        return GDL01_value(v)

    def handle_assign(self):
        savpos = self.pos
        s = self.handle_NAME()
        if not s:
            return None
        self.skipspacecrlf()
        if not self.handle_str('='):
            return self.restorepos(savpos)
        self.skipspacecrlf()
        v = self.handle_value()
        if not v:
            return self.restorepos(savpos)
        return GDL01_assign(s, v)

    def handle_funccall(self):
        savpos = self.pos
        s = self.handle_NAME()
        if not s:
            return None
        self.skipspacecrlf()
        if not self.handle_str('('):
            return self.restorepos(savpos)
        self.skipspacecrlf()
        v = self.handle_value()
        if not v:
            return self.restorepos(savpos)
        self.skipspacecrlf()
        if not self.handle_str(')'):
            return self.restorepos(savpos)
        return GDL01_funccall(s, v)

class GDL01_output:
    def __init__(self, outp):
        self.outp = outp
    def visit_main(self, node):
        for v in node.vlst:
            v.walkabout(self)
            self.outp.newline()
    def visit_stmt(self, node):
        node.v.walkabout(self)
    def visit_datatype(self, node):
        self.outp.puts(node.s)
    def visit_declare(self, node):
        node.v.walkabout(self)
        self.outp.puts(node.s)
    def visit_declare_with_value(self, node):
        node.v1.walkabout(self)
        self.outp.puts(node.s)
        self.outp.puts('=')
        node.v2.walkabout(self)
    def visit_value0(self, node):
        self.outp.puts(node.s)
    def visit_binvalue(self, node):
        node.v1.walkabout(self)
        self.outp.puts(node.s)
        node.v2.walkabout(self)
    def visit_value(self, node):
        node.v.walkabout(self)
    def visit_assign(self, node):
        self.outp.puts(node.s)
        self.outp.puts('=')
        node.v.walkabout(self)
    def visit_funccall(self, node):
        self.outp.puts(node.s)
        self.outp.puts('(')
        node.v.walkabout(self)
        self.outp.puts(')')

class OutP:
    def __init__(self):
        self.txt = ''
    def puts(self, s):
        #print s,
        self.txt += s
    def newline(self):
        #print
        self.txt += '\n'

nouse_syntax = '''
    main = stmt*
    stmt = declare_with_value | declare | assign | funccall
    datatype = 'int' | 'long'
    declare = datatype NAME
    declare_with_value = datatype NAME '=' value
    value0 = NUMBER | NAME
    binvalue = value0 ('+' | '-') value0
    value = binvalue | value0
    assign = NAME '=' value
    funccall = NAME '(' value ')'
'''

sample = '''
    int i = 22
    int j = 3 + i
    int k
    k = i - j
    print(k)
'''

import unittest
class Test(unittest.TestCase):
    def testhandle_NAME(self):
        the = Parser00('hello world')
        word1 = the.handle_NAME()
        self.assertEqual(the.pos, 5)
        the.pos = 2
        word2 = the.handle_NAME()
        the.pos = 5
        word3 = the.handle_NAME()
        the.pos = 6
        word4 = the.handle_NAME()
        self.assertEqual(word1, 'hello')
        self.assertEqual(word2, 'llo')
        self.assertEqual(word3, None)
        self.assertEqual(word4, 'world')
    def testParse(self):
        the = GDL01_Parser(sample)
        the.skipspacecrlf()
        main = the.handle_main()
        self.assertEqual(main.vlst[-1].v.s, 'print')

    def testOutput(self):
        psr = GDL01_Parser(sample)
        psr.skipspacecrlf()
        mod = psr.handle_main()

        outp = OutP()
        the = GDL01_output(outp)
        mod.walkabout(the)
        lines = outp.txt.splitlines()
        self.assertEqual(lines[-1], 'print(k)')
