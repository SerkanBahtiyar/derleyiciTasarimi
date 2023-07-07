#sadece hatanın nereden geldiğini gösteren okları görüntüleme sağlayacağız
def hatalar(text, pos_start, pos_end):
    result = ''

      #İndexleri hesaplayacağımız kısım
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    #Her satırı oluşturacağımız kısım
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        #Satır ve sutünları hesaplayacağımız kısım
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        #Sonucu nereye ekleyeceğimiz kısım
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

       #İndexleri yeniden hesaplayacağımız kısım
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

#replace() yöntemi, bir dize içinde belirli bir alt dizeyi başka bir alt dizeyle değiştirmek için kullanılan bir yöntemdir.