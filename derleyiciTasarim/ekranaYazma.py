import ply.lex as lex

# Token listesi
tokens = [
    'string',
    'sayi',
]

# Token tanımları
t_string = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_sayi = r'\d+'

#boşluk karakteri
t_ignore = ' \t'

#hata durumunda hata mesajı
def t_error(t):
    print("Geçersiz karakter: %s" % t.value[0])
    t.lexer.skip(1)

#lexer oluşturma
lexer = lex.lex()
def lexerYazma():
    kod = input("ekrana yazdırcağınız bilgiyi girin: ")
    lexer.input(kod)

    while True:
        token = lexer.token()
        if not token:
            break
        if token.type in ['string', 'sayi']:
            print(token.value)
#burda string ve sayıları ekrana yazdırma işlemini gerçekleştirmeye çalıştım
lexerYazma()