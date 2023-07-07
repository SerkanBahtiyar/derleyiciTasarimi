
import string
from hata import *
import re
#Burada classımızdaki bilgileri kullanmak için gerekli olan kısım içe aktarma işlemi
#Sabit değerler
#Rakamları tutuyorum
#Bir karakterin rakam olup olmadığını tespit edebilmek için kullanım yapısı
RAKAMLAR= '9876543210'
#Bir karakterin harf olup olmadığını tespit edebilmek için yapılan işlem
HARFLER = string.ascii_letters
#Bir karakterin harf + rakam olup olmadığını tespit edebilmek için
RAKAMLARHARFLER = HARFLER + RAKAMLAR
#Hatalar için kullanacağımız kodlar
#Aradığımız karakteri bulamazsak bazı hatalar vermemiz gerekiyor, bu yüzden burada yapacağım şey özel hata sınıfı oluşturmak.

#Bu metotumuz hata isimli,detaylar ve posizyon başlangıcı ve bitişi değerlerini alıyor
class hata:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

#Burada bir metot oluşturuyoruz ve bu sadece bir string oluşturacak,hata adını ve ayrıntılarını gösterme işlemi gerçekleştirecek.
    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + \
            hatalar(self.pos_start.ftxt,
                               self.pos_start, self.pos_end)
        #hatalar fonksiyonu, self.pos_start.ftxt (metin), self.pos_start (başlangıç konumu) ve self.pos_end (bitiş konumu) argümanlarıyla çağrılır. 
        #bu fonksiyon, self.pos_start ve self.pos_end arasındaki metin aralığında hata bildirimi için kullanılacak bir metin bloğu oluşturmasına sağlayacak.
        return result

#Geçersiz Karakter Hatası
class gecersizKarakterError(hata):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'geçersiz karakter', details)

#Beklenen Karakter Hatası
class beklenenKarakterError(hata):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'beklenen karakter hatası', details)

#Geçersiz syntax için hatası sınıfı
#bu hatalar bolme işleminde bir hata olduğunda oluşturulacaktır
class gecersizSyntaxError(hata):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'geçersiz syntax oluştu', details)

#Çalışma zamanı hatası için kullanacak olduğumuz bölge
class zamanError(hata):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'çalışma zamanı hatası', details)
        self.context = context
    #göster
    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + \
            hatalar(self.pos_start.ftxt,
                               self.pos_start, self.pos_end)
        return result
    #geri izleme traceback bilgisini oluşturmak için kullanacağımız yapı
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'geri izleme:\n' + result
               #geri izleme(en son arama)
  #ctx değişkeni değeri none olana kadar döngü içindeki işlemler gerçekleştirilir

#Pozisyon bilgilerinde kullanacağımız kısım yani konum
#Position,satır numarası sütun numarasını ve mevcut indeksi takip ediyor
class Pozisyon:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    #Satır İçerisinde ilerlemek için kullanacağımız kısım,bu sadece bir sonrak indekse geçme işlemini gerçekleştiricek
    #advance(ilerleme) yap
    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':#current_char yeni satır karakteri ('\n') olup olmadığı kontrol edilir.
            self.ln += 1
            self.col = 0
        #eğer mevcut karakter bir yeni satır karakteri ise, self.ln özelliği bir artırılır ve self.col özelliği sıfırlanır. 
        return self

      #Sadece konumun bir kopyasını oluşturmak için kullanacak bir kopyalama metodu
    def copy(self):
        return Pozisyon(self.idx, self.ln, self.col, self.fn, self.ftxt)


#token bilgilerimiz
#Farklı töken türleri için sabitlerimizi tanımlama işlemlerini gerçekleştiriyoruz
#degisken tiplerimiz int ve float string taniyici da stringTaniyici sınıfında kullanılmaya çalışıldı
TOKENFLOAT = 'FLOAT' 
TOKENINT = 'INT' 
#değişkenler Keyword,identifier 
TOKENIDENTIFIER = 'IDENTIFIER'
TOKENKEYWORD = 'KEYWORD'

#Operatörler
TOKENARTI = 'ARTI'      #Toplama(+)
TOKENEKSI = 'EKSI'      #Çıkarma(-)
TOKENCARPI = 'CARPI'    #Çarpma (*)
TOKENBOLU = 'BOLU'      #Bölme(/)
TOKENESIT = 'ESIT'      #Eşittir(=)
TOKENMOD = 'MOD'        #mod(%)
TOKENUS = 'US'          #üst(^) 

#Özel Semboller
TOKENSOLPARANTEZ = 'SOLPAR'  #Sol Parantez (
TOKENSAGPARANTEZ = 'SAGPAR'  #Sağ Parantez )


TOKENSATIRSONU = "SATIRSONU"#Satır Sonu
TOKENESITTIR = 'ESITTIR'  #Eşittir
TOKENESITDEGILDIR = 'ESITDEGILDIR'  #Eşitt Değildir
TOKENKUCUKTUR = 'KUCUKTUR'  #Küçüktür
TOKENKUCUKESITTIR= 'KUCUKESITTIR' #Küçük Eşittir
TOKENBUYUKTUR= 'BUYUKTUR'  #Büyüktür
TOKENBUYUKESITTIR = 'BUYUKESITTIR' #Büyük Eşittir

#yapımızda kullanacağımız keywordler
KEYWORDS = ['degisken','veya','ve','not', 'if','else','then', 'elif', 'for','while','to','step']
#diğer anahtar kelimeler
#token kodun küçük bir bölümünden gelir
#token class'ında token'in tipi, değeri pozisyon başlangıcı ve bitişi bulunuyor
#pozisyon başlangıç ve bitişi bize hatanın nerede olduğunu göstermek için mevcut
class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    #Eğer token türümüz ve değeri eşleşirse bu işlemi gerçekleştirme işlemi yapacağız
    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    #representation metodu ile düzenleme işlemi
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
#Token değere sahip olduktan sonra,türü ve ardından değeri yazdırır bir değeri yoksa yalnızca türü yazdırma işlemi

#Lexer Programı input olarak alıp tokenlere bölecek
#Lexer karakter karakter girdiden geçecek ve metni, süreçte tokens dediğimiz bir listeye bölme işlemini gerçekleştiricek
class Lexer:
    #Initialize method kısmında,işleyeceğimiz metni almamız gerekecek
    #Bunu sadece self.text'e atayacağız
    #Mevcut pozisyonu ve aynı zamanda mevcut karakteri takip etmemiz gerekecek
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Pozisyon(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    #Satır içerisinde ilerlemek için bu fonksiyonu kullanacağız
    #Metinde sadece bir sonraki karaktere ilerleme işlemini gerçekleştircek drurum tanımlandı
    #Pozisyonu artırıp mevcut karakteri metin içinde o konumdaki karaktere ayarlanılıyor
    #Bunu ancak konum metnin uzunluğundan küçükse yapabiliyoruz
    #Metnin sonuna ulaştığımızda,onu none olarak ayarlanıyor
    def advance(self):
        #else durumunda satırın sonun gelmişiz demektir
        #Girilen text içerisindek,text uzunluğu kadar dolaşacağız
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

    #Token oluşturuyoruz
    def tokenOlustur(self):
        tokens = []
        #Okunan karakter boş olmadığı sürece
        #Metindeki her karaktere giden bir döngü oluşturulup mevcut karakterin none'a eşit olmadığını kontrol ediliyor
        #Çünkü yukarıda metnin sonuna geldiğimizde onu none olarak ayarlamıştık
        while self.current_char != None:
            #Boşluk varsa bir adım ilerle
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in RAKAMLAR:
                tokens.append(self.make_number())
            elif self.current_char in HARFLER:
                tokens.append(self.make_identifier())
            #Okunan karakter + ise bunu ARTİ tokeni olarak tutcağız
            elif self.current_char == '+':
                #+ karakterini token listemize TOKENARTİ adıyla ekledik
                tokens.append(Token(TOKENARTI, pos_start=self.pos))
                self.advance()  #Bir karekter ilerliyoruz
                #Toplama işlemi için yaptığımız adımları,en üstte tanımladığımız tüm sabitler içinde yapıyoruz
                #Çıkarma İşlemi TOKENEKSI ile token listesine eklendi
            elif self.current_char == '-':
                tokens.append(Token(TOKENEKSI, pos_start=self.pos))
                self.advance()
                #Çarpma İşlemi 
                 #Çarpma İşlemi TOKENCARPI ile token listesine eklendi
            elif self.current_char == '*':
                tokens.append(Token(TOKENCARPI, pos_start=self.pos))
                self.advance()
             
              #bölme İşlemi TOKENBOLU ile token listesine eklendi
            elif self.current_char == '/':
                tokens.append(Token(TOKENBOLU, pos_start=self.pos))
                self.advance()
            #Üs (Kuvvet) İşlemi
            elif self.current_char == '^':
                tokens.append(Token(TOKENUS, pos_start=self.pos))
                self.advance()
            #mod işlemi
            elif self.current_char == '%':
                tokens.append(Token(TOKENMOD, pos_start=self.pos))
                self.advance()
            #eşit
            elif self.current_char == '=':
                tokens.append(Token(TOKENESIT, pos_start=self.pos))
                self.advance()
            #Sağ Parantez
            elif self.current_char == ')':
                tokens.append(Token(TOKENSAGPARANTEZ, pos_start=self.pos))
                self.advance()
            #Sol Parantez
            elif self.current_char == '(':
                tokens.append(Token(TOKENSOLPARANTEZ, pos_start=self.pos))
                self.advance()
            #Değil Eşit
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            #Eşit mi ?
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            #Küçüktür
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            #Büyüktür
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            #Eğer tanımlı olan karakterlerden biri gelmediyse hata döndürme işlemi gerçekleştiriyoruz bunu da gecersizKarakterError ile yapıyoruz
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], gecersizKarakterError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TOKENSATIRSONU, pos_start=self.pos))
        return tokens, None

    #Sayı birden fazla karakter olabilir bu yüzden, aslında bir sayı yapan bir fonksiyon yapıyoruz
    #Bu fonksiyon ya bir integer tokeni ya da bir float tokeni yapacaktır
    def make_number(self):
        #sayımız int ya da float mı kontrol etmek için kullandığımız ifade
        #Rakamları string formunda takip etmemiz gerekiyor
        num_str = ''
        #Ayrıca nokta sayısını da takip etmemiz gerekecek.
        dot_count = 0  #Nokta Sayısı
        pos_start = self.pos.copy() #self.pos nesnesinin bir kopyasını pos_start adlı yeni bir değişkene atma işlemi
        #Sayıda nokta yoksa bu bir integerdir, ancak sayıda nokta varsa o zaman bir floattır
        #Bu fonksiyonun içinde, mevcut karakterin none olmadığını ve mevcut karakterin bir rakam veya nokta olup olmadığını kontrol edecek başka bir döngü oluşturuluyor
        while self.current_char != None and self.current_char in RAKAMLAR + '.':
            #None değilse, yani mevcut karakter bir değere sahipse, döngü devam eder
            #Geçerli karakter bir noktaysa eğer nokta sayısını artıracağız nokta sayısının zaten bire eşit olması durumunda,döngüden çıkıyoruz çünkü tek sayıda iki nokta olamaz
            if self.current_char == '.':
                if dot_count == 1:  #Sayı içerisinde birden fazla nokta olmaz
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
                 #Eğer nokta yoksa rakam stringini bir artırıyoruz çünkü sıradaki karakter bir rakam olmak zorunda
            self.advance()#ilerleme

            #Sayıda hiç nokta yoksa tipi int tipindedir
            #Nokta sayısının sıfıra eşit olup olmadığını kontrol edilip eğer sıfırsa sayımız bir integer değilse floattır
        if dot_count == 0:
            return Token(TOKENINT, int(num_str), pos_start, self.pos)
        #dot_counter'ın 0'dan farklı olduğu zaman sayıda nokta var demektir
        #Tipi floattır
        else:
            return Token(TOKENFLOAT, float(num_str), pos_start, self.pos)

    #Girilen string geçerli mi asci'ye uyuyor olup olmadığı kontrolü
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in RAKAMLARHARFLER + '_':
            id_str += self.current_char
            self.advance()

        #Token Tipi kulanılabilir bir keyword mü onu kontrol ettiğimiz kısım
        tok_type =TOKENKEYWORD if id_str in KEYWORDS else TOKENIDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    #Eşit değil mi kontrolü
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TOKENESITDEGILDIR, pos_start=pos_start, pos_end=self.pos), None
         #Eğer eşit değildir sembolü eşittirden sonra geldiyse beklenen karakter hatası çıkarıyoruz
        self.advance()
        return None, beklenenKarakterError(pos_start, self.pos, "'=' (sonra '!')")

    #Eşit mi kontrolü 
    def make_equals(self):
        tok_type = TOKENESIT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOKENESITTIR

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    #Küçük mü kontrolü
    def make_less_than(self):
        tok_type = TOKENKUCUKTUR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOKENKUCUKESITTIR

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    #Büyük mü kontrolü
    def make_greater_than(self):
        tok_type = TOKENBUYUKTUR
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TOKENBUYUKESITTIR

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


#Düğümler
#Parser bir ağaç oluşturacak, önce birkaç farklı düğüm türü tanımlamlıyoruz
class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

     # represent methodu tanımlayıp sadece tokeni string olarak döndürecek.
    def __repr__(self):
        return f'{self.tok}'

#degisken Tipi Erişimi için
class degiskenAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

#degisken Tipi Atama işlemi için
class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end
#self.pos_end = self.value_node.pos_end: pos_end özelliğini value_node nesnesinin pos_end özelliğine atar.
#Bu, değerin bittiği konumu temsil eder.

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    # sınıfın sol düğümü, operatör belirteci ve sağ düğümün temsili.
 
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'
    #op_tok özelliği, bir operatör belirteciyi temsil ederken, node özelliği düğümü temsil edecek.
   
#If yapısı İçin
class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start  #pos_start özelliğini, cases listesinin ilk durumunun ilk ifade düğümünün pos_start özelliğine atar
        self.pos_end = (
            self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

#For Döngüsü İçin
class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end #pos_end özelliğini body_node nesnesinin pos_end özelliğine atar. Bu, döngü ifadesinin bittiği konumu temsil eder.
 
#While Döngüsü için kullandığımız ifade
class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start #pos_start özelliğini condition_node nesnesinin pos_start özelliğine atar while döngüsünün başladığı konumu temsil eder.
        self.pos_end = self.body_node.pos_end

#Parser
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self): 
        self.advance_count += 1  #advance_count özelliğini 1 birim artır

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        #res sonucunun bir hata içerip içermediğini kontrol eder. Eğer res bir hata içeriyorsa, error özelliğine res.error atanır. 
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):   #tok_idx özelliğinin, token listesinin uzunluğundan küçük olup olmadığını kontrol eder.
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TOKENSATIRSONU: #res sonucunda bir hata olmadığını ve geçerli tokenin satır sonu olup olmadığını kontrol eder.
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "beklenen '+', '-', '*', '/' veya '^' '%'"
            ))
        return res

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TOKENKEYWORD, 'if'): #current_tok özelliğinin 'if' anahtar kelimesiyle eşleşmediğini kontrol eder. matches yöntemi, belirtecin türünü ve değerini kontrol ederek eşleşme durumunu belirler.
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"if' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENKEYWORD, 'then'):
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"'Then' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res
        cases.append((condition, expr))

        while self.current_tok.matches(TOKENKEYWORD, 'elif'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            if not self.current_tok.matches(TOKENKEYWORD, 'then'):
                return res.failure(gecersizSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"'then' Bekleniyor"
                ))

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.matches(TOKENKEYWORD, 'else'):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENKEYWORD, 'for'):
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"'for' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOKENIDENTIFIER:
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Tanimlayici Bekleniyor"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TOKENESIT:
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Bekleniyor '='"
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENKEYWORD, 'to'):
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"'to' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TOKENKEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.matches(TOKENKEYWORD, 'then'):
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"'then' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TOKENKEYWORD, 'while'):
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"'while' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TOKENKEYWORD, 'then'):
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"'then' Bekleniyor"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOKENINT, TOKENFLOAT): #tok belirtecinin tipinin tamsayı veya ondalık sayı türlerinden birine eşit olup olmadığını kontrol eder. 
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TOKENIDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(degiskenAccessNode(tok))

        elif tok.type == TOKENSOLPARANTEZ:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TOKENSAGPARANTEZ:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(gecersizSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "')' Bekleniyor"
                ))

        elif tok.matches(TOKENKEYWORD, 'if'):#if anahtar kelimesiye eşleşme durumu kontrolü
            if_expr = res.register(self.if_expr()) #if_expr değişkenine self.if_expr() yöntemini çağırarak ifadeyi işler
            if res.error: #if_expr ifadesinin işlenmesi sırasında bir hata oluştuysa, hatayı döndürerek işlemi durduracağız.
                return res
            return res.success(if_expr)  #if_expr ifadesinin başarılı bir şekilde işlendiğini ve sonucunun döndürüldüğünü gösterir. 

        elif tok.matches(TOKENKEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TOKENKEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        return res.failure(gecersizSyntaxError(  #geçersiz sözdizimi hatasını döndür
            tok.pos_start, tok.pos_end,
            "beklenenler int, float, identifier, '+', '-', '('"
        ))

    def power(self):
        return self.bin_op(self.atom, (TOKENUS, ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TOKENARTI,TOKENEKSI):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TOKENCARPI, TOKENBOLU))

    #Matematiksel işlemler için  kullanacağımız ifade
    def arith_expr(self):
        return self.bin_op(self.term, (TOKENARTI, TOKENEKSI,TOKENMOD))

    #Eşitlik Kontrol İfadeleri ( <=,==)
    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TOKENKEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(
            self.arith_expr, (TOKENESITTIR, TOKENESITDEGILDIR, TOKENKUCUKTUR, TOKENBUYUKTUR, TOKENKUCUKESITTIR, TOKENBUYUKESITTIR))) #operatörler

        if res.error:
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "beklenen int, float, tipindedir, '+', '-', '(' veya 'not'"
            ))

        return res.success(node)  #Sonucu Dön

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TOKENKEYWORD, 'degisken'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOKENIDENTIFIER:
                return res.failure(gecersizSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Tanimlayici Bekleniyor"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TOKENESIT:
                return res.failure(gecersizSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "bekleniyor'='"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(
            self.comp_expr, ((TOKENKEYWORD, 've'), (TOKENKEYWORD, 'veya'))))

        if res.error:
            return res.failure(gecersizSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "beklenen 'degisken', int, float, identifier, '+', '-' veya '('"
            ))

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
        ##tokenin türünün ops parametresinde belirtilen operatörler listesinde olup olmadığını kontrol eder eğer geçerli belirteç bir operatörse, döngüye girilir.
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)#sol ifade, operatör belirteci ve sağ ifadeyi kullanarak bir BinOpNode oluşturur ve left değişkenine atar. 

        return res.success(left)


#Çalışma Zamanı Sonuçları için kullanacağımız kod kısmı
#Mevcut sonucu takip edecek ve varsa bir hatayı da takip edecek
class calismaZamaniResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

#Değerler için kullanacağımız kod kısmı
class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.durumBelirle()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def durumBelirle(self, context=None):
        self.context = context
        return self

    def cikarma(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).durumBelirle(self.context), None
    def toplama(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).durumBelirle(self.context), None

    def carpma(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).durumBelirle(self.context), None
    def mod(self, other):
        if isinstance(other, Number):
            return Number(self.value % other.value).durumBelirle(self.context), None

    def bolunme(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, zamanError(
                    other.pos_start, other.pos_end,
                    self.context
                )

            return Number(self.value / other.value).durumBelirle(self.context), None

    #Üs(Kuvvet Alma)
    def usAl(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).durumBelirle(self.context), None
    #Eşitlik Durumu
    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).durumBelirle(self.context), None
    #Eşit Değil Durumu (Değil Eşit)
    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).durumBelirle(self.context), None
    #Küçüktür Durumu
    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).durumBelirle(self.context), None
    #Büyüktür Durumu
    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).durumBelirle(self.context), None
    #Küçük Eşittir Durumu
    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).durumBelirle(self.context), None
    #Büyük Eşittir Durumu
    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).durumBelirle(self.context), None
    #VE Durumu
    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).durumBelirle(self.context), None
    #VEYA Durumu
    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).durumBelirle(self.context), None
    #Değil Durumu (not)
    def notted(self):
        return Number(1 if self.value == 0 else 0).durumBelirle(self.context), None
    def is_true(self):
        return self.value != 0

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.durumBelirle(self.context)
        return copy

    def __repr__(self):
        return str(self.value)

#Context
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        #Varsayılan değeri None olduğundan, üst bağlama giriş pozisyonunun olup olmadığı kontrol edilir.
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

#sembol tablosu
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value): # name isimine sahip sembolü ve onun değerini sembol tablosuna ekler 
        self.symbols[name] = value

    def remove(self, name): # name isimine sahip sembolü ve onun değerini sembol tablosundan kaldırır
        del self.symbols[name]


#Yorumlayıcı için kullanılan kod kısmı
class Interpreter:
     # Bu metot,o düğümü işleyecek ve ardından tüm alt düğümleri dolaşacak
    def visit(self, node, context):
       #metot ismini almak için
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    #Eğer o isimde bir metot yoksa
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method bulunamadı')


    #Her düğüm türü için gez metodu tanımlıyorum
    def visit_NumberNode(self, node, context):
        return calismaZamaniResult().success(
            Number(node.tok.value).durumBelirle(
                context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_degiskenAccessNode(self, node, context):
        res = calismaZamaniResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(zamanError(
                node.pos_start, node.pos_end,
                f"'{var_name}' tanimlanmadi.",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = calismaZamaniResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = calismaZamaniResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res
        #operatörlere göre ilgili işlemleri gerçekleştir ve sonuçlarını döndür
        if node.op_tok.type == TOKENARTI:#toplama
            result, error = left.toplama(right)
        elif node.op_tok.type == TOKENEKSI: #çıkarma
            result, error = left.cikarma(right)
        elif node.op_tok.type == TOKENCARPI:  #çarp
            result, error = left.carpma(right)
        elif node.op_tok.type == TOKENBOLU: #böl
            result, error = left.bolunme(right)
        elif node.op_tok.type == TOKENMOD: #mod
            result, error = left.mod(right)
        elif node.op_tok.type == TOKENUS: #üs
            result, error = left.usAl(right)
        elif node.op_tok.type == TOKENESITTIR:  #eşittir
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TOKENESITDEGILDIR: #eşitsizlik
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TOKENKUCUKTUR: #küçüktür
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TOKENBUYUKTUR: #büyüktür
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TOKENKUCUKESITTIR:  #küçük eşit
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TOKENBUYUKESITTIR:  #büyük eşit
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TOKENKEYWORD, 've'):  #ve işlemi
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TOKENKEYWORD, 'veya'):  #veya işlemi
            result, error = left.ored_by(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = calismaZamaniResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == TOKENEKSI:
            number, error = number.carpma(Number(-1))
        elif node.op_tok.matches(TOKENKEYWORD, 'not'):
            #node.op_tok TOKENKEYWORD türünde ve değeri 'not' ise, bir sayı nesnesinin  tersini alması gerçekleştirilir.
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = calismaZamaniResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = calismaZamaniResult()
        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res
        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res
        if node.step_value_node:
            step_value = res.register(
                self.visit(node.step_value_node, context))
            if res.error:
                return res
        else:
            step_value = Number(1)
        i = start_value.value
        if step_value.value >= 0:
            def condition(): return i < end_value.value
        else:
            def condition(): return i > end_value.value
        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value  #i değeri step_value.value kadar artırılır.
            res.register(self.visit(node.body_node, context))
            #visit metodu ilgili düğümü gezerek ilgili işlemleri gerçekleştirir. Bu işlemler sonucunda bir ParseResult nesnesi döner.
            if res.error:
                return res
        return res.success(None)
    
    def visit_WhileNode(self, node, context):
        res = calismaZamaniResult()
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res
            if not condition.is_true():
                break
            res.register(self.visit(node.body_node, context))
            if res.error:
                return res
        return res.success(None)
    

#Çalıştırmak için kullanacağımız kod
#Global Sembol Tablosu
global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0))
#Kontrol durumu sıfır dönüyorsa False yazdır
global_symbol_table.set("FALSE", Number(0))
#Kontrol durumu bir dönüyorsa True yazdır
global_symbol_table.set("TRUE", Number(1))
#Açıklama satırı yapısı
tokenTipi = {
    'yorum': r'#(.*)',
    'tanimlayici': r'[a-zA-Z_]\w*',
    'sembol': r'[+\-*/=()]',
    'sayi': r'\d+',
    'whiteSpace': r'\s+'
}

class YorumToken:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {self.value})'

class YorumLexer:
    def __init__(self, text):
        self.text = text
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        olustur = '|'.join(f'(?P<{type}>{yapi})' for type, yapi in tokenTipi.items()) #|ile birleşim sağla
        token_regex = re.compile(olustur)

        for match in re.finditer(token_regex, self.text):
            token_type = match.lastgroup
            token_value = match.group(token_type)
    
           
            token = YorumToken(token_type, token_value)
            tokens.append(token)

        return tokens

yorumKod = '''''
# yorum satırı
sayi1=10
sayi2=20
ifade=serkan
toplam = sayi1 + sayi2
''' 
yorumSatiriKontrol=False  #kontrol
if(yorumSatiriKontrol==True):
   lexer = YorumLexer(yorumKod)
   for token in lexer.tokens:
     print(token)     


#Çalıştırma kısmı
#Bu metot metin alıp çalıştıracak.
def run(fn, text): #fn:filename
    #Tokenlerı Üretmek için kullanacağımız kod kısmı
    #Yeni bir lexer oluşturuyoruz
    lexer = Lexer(fn, text)
    tokens, error = lexer.tokenOlustur()
    if error:
        return None, error

    # syntax ağacını oluşturuyoruz
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    #Programı Çalıştır
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error

