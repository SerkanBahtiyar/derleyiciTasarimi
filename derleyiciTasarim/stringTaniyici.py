
class StringLexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.current_position = 0
        self.current_char = source_code[self.current_position]

    def advance(self):
        self.current_position += 1 #mevcut pozisyon
        if self.current_position < len(self.source_code):
            self.current_char = self.source_code[self.current_position]
        else:
            self.current_char = None

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()
            elif self.current_char == '"':
                tokens.append(self.tokenize_string())
            else:
              
                self.advance()
        return tokens

    def tokenize_string(self):
        start_position = self.current_position
        string_value = ''
        self.advance()

        while self.current_char is not None and self.current_char != '"':
         # " kadar olan karakterleri birleştirerek string değeri oluşturma işlemi
            string_value += self.current_char
            self.advance()

        if self.current_char == '"':
            self.advance()  # ""karakterini atla

        return StringToken('string veri tipi', string_value)

class StringToken:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{self.type}, {self.value}"


string = 'print("serkanbahtiyar")'
lexer = StringLexer(string)
tokens = lexer.tokenize()
for token in tokens:
    print(token)   
    