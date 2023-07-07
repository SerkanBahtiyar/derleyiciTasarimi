import derle

#derle classından bilgileri kullanmak için gerekli olan kısımı içe aktarıyoruz
#Bu dosya, terminal penceresinden girdiyi okuyacak ve while ile sonsuz bir döngüye sahip olacak
while True:
    al = input('testGerceklestir > ')

    sonuc, hata = derle.run('<stdin>', al)  #standart input

    print(sonuc)

    if hata: print(hata.as_string())

    elif sonuc: print(sonuc)

#Döngü her döndüğünde kullanıcıdan bir metin girişi istenir.


