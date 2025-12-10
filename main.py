import sys
import ply.lex as lex
import ply.yacc as yacc
from xml.dom.minidom import Document

# Список всех токенов, которые мы будем искать в тексте
tokens = (
    'NAME', 'NUMBER', 'ASSIGN', 'ARROW',
    'LBRACKET', 'RBRACKET', 'LARRAY', 'RARRAY',
    'COMMA', 'CONST_REF'
)

# Описываем простые символы с помощью регулярных выражений
t_ASSIGN = r':='
t_ARROW = r'=>'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LARRAY = r'<<'
t_RARRAY = r'>>'
t_COMMA = r','
t_ignore = ' \t'

# Однострочные комментарии
def t_COMMENT(t):
    r'\*.*'
    pass

# Константа
def t_CONST_REF(t):
    r'\#\([A-Z]+\)'
    t.value = t.value[2:-1]
    return t

# Имена
def t_NAME(t):
    r'[A-Z]+'
    return t

# Числа
def t_NUMBER(t):
    r'[+-]?([1-9][0-9]*|0)'
    t.value = int(t.value)
    return t

# Новая строка
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# # Если встретили символ, который не знаем выводим ошибку
def t_error(t):
    sys.stderr.write(f"Недопустимый символ '{t.value[0]}'\n")
    t.lexer.skip(1)

lexer = lex.lex(debug=0)

constants = {}
result_data = {}

# Парсер
def p_program(p):
    '''program : statements'''
    pass

# Список выражений
def p_statements(p):
    '''statements : statement
                  | statements statement'''
    pass

def p_statement(p):
    '''statement : NAME ASSIGN value'''
    constants[p[1]] = p[3]
    result_data[p[1]] = p[3]

# Число
def p_value_number(p):
    '''value : NUMBER'''
    p[0] = p[1]

# Ссылка на константу
def p_value_const(p):
    '''value : CONST_REF'''
    if p[1] in constants:
        p[0] = constants[p[1]]
    else:
        raise ValueError(f"Неопределённая константа: {p[1]}")

# Массив
def p_value_array(p):
    '''value : array'''
    p[0] = p[1]

# Словарь
def p_value_dict(p):
    '''value : dictionary'''
    p[0] = p[1]

# Массив
def p_array(p):
    '''array : LARRAY elements RARRAY'''
    p[0] = p[2]

# Элементы массива
def p_elements(p):
    '''elements : value
                | value COMMA elements'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Словарь
def p_dictionary(p):
    '''dictionary : LBRACKET pairs RBRACKET'''
    p[0] = dict(p[2])

# Пары словаря
def p_pairs(p):
    '''pairs : pair
             | pair COMMA pairs'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Ключ - значение
def p_pair(p):
    '''pair : NAME ARROW value'''
    p[0] = (p[1], p[3])

# Обработка синтаксических ошибок
def p_error(p):
    if p:
        sys.stderr.write(f"Синтаксическая ошибка в '{p.value}'\n")
    else:
        sys.stderr.write("Синтаксическая ошибка\n")

parser = yacc.yacc(debug=0, write_tables=0)

# Рекурсивная функция для превращения данных в XML
def build_xml(doc, parent, data):
    if isinstance(data, dict):
        for key, value in data.items():
            element = doc.createElement(key)
            parent.appendChild(element)
            build_xml(doc, element, value)
    elif isinstance(data, list):
        for item in data:
            element = doc.createElement("item")
            parent.appendChild(element)
            build_xml(doc, element, item)
    else:
        text = doc.createTextNode(str(data))
        parent.appendChild(text)

if __name__ == "__main__":
    try:
        input_text = sys.stdin.read()
        parser.parse(input_text)

        doc = Document()
        root = doc.createElement("config")
        doc.appendChild(root)

        build_xml(doc, root, result_data)

        print(root.toprettyxml(indent="    "))
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
