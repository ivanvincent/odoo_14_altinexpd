dic = {
    'to_19' : ('Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'),
    'tens'  : ('Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'),
    'denom' : ('', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion'),
    'to_19_id' : ('Nol', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Sepuluh', 'Sebelas', 'Dua Belas', 'Tiga Belas', 'Empat Belas', 'Lima Belas', 'Enam Belas', 'Tujuh Belas', 'Delapan Belas', 'Sembilan Belas'),
    'to_09_id_desimal' : ('Nol', 'Nol Satu', 'Nol Dua', 'Nol Tiga', 'Nol Empat', 'Nol Lima', 'Nol Enam', 'Nol Tujuh', 'Nol Delapan', 'Nol Sembilan'),
    'to_19_id_desimal' : ('Nol', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Satu', 'Sebelas', 'Dua Belas', 'Tiga Belas', 'Empat Belas', 'Lima Belas', 'Enam Belas', 'Tujuh Belas', 'Delapan Belas', 'Sembilan Belas'),
    # 'to_19_id_desimal' : ('Nol', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Satu', 'Satu Satu', 'Satu Dua', 'Satu Tiga', 'Satu Empat', 'Satu Lima', 'Satu Enam', 'Satu Tujuh', 'Satu Delapan', 'Satu Sembilan'),
    'tens_id'  : ('Dua Puluh', 'Tiga Puluh', 'Empat Puluh', 'Lima Puluh', 'Enam Puluh', 'Tujuh Puluh', 'Delapan Puluh', 'Sembilan Puluh'),
    'tens_id_desimal'  : ('Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan'),
    'denom_id' : ('', 'Ribu', 'Juta', 'Miliar', 'Triliun', 'Biliun')
}
 
def terbilang(number, currency, bhs):
    number = '%.2f' % number
    units_name = ' ' + cur_name(currency) + ' '
    lis = str(number).split('.')
    start_word = english_number(int(lis[0]), bhs)
    # end_word = english_number(int(lis[1]), bhs)
    end_word = english_number_des(int(lis[1]), bhs)
    cents_number = int(lis[1])
    # cents_name = (cents_number > 1) and 'Sen' or 'sen'
    cents_name = (cents_number > 1) and 'Koma' or 'koma'
    # final_result_sen = start_word + units_name + end_word +' '+cents_name
    final_result_sen = start_word +' '+cents_name+' ' + end_word + units_name 
    final_result = start_word + units_name
    if end_word == 'Nol' or end_word == 'Zero' or end_word == '':
        final_result = final_result
    else:
        final_result = final_result_sen

    return final_result[:1].upper()+final_result[1:]
 
def _convert_nn(val, bhs):
    if bhs == 'id':
        tens = dic['tens_id']
        to_19 = dic['to_19_id']
    elif bhs == 'en':
        tens = dic['tens']
        to_19 = dic['to_19']
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' ' + to_19[val % 10]
            return dcap

def _convert_n_desimal(val, bhs):
    if bhs == 'id':
        tens = dic['tens_id_desimal']
        to_9 = dic['to_09_id_desimal']

    if val < 20:
        return to_9[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' ' + to_9[val % 10]
            return dcap

def _convert_nn_desimal(val, bhs):
    if bhs == 'id':
        tens = dic['tens_id_desimal']
        to_19 = dic['to_19_id_desimal']
    elif bhs == 'en':
        tens = dic['tens']
        to_19 = dic['to_19']
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' ' + to_19[val % 10]
            return dcap

def _convert_nnn(val, bhs):
    if bhs == 'id':
        word = ''; rat = ' Ratus'; to_19 = dic['to_19_id']
    elif bhs == 'en':
        word = ''
        rat = ' Hundred'
        to_19 = dic['to_19']

    (mod, rem) = (val % 100, val // 100)
    if rem == 1:
        word = 'Seratus'
        if mod > 0:
            word = word + ' '   
    elif rem > 1:
        word = to_19[rem] + rat
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn(mod, bhs)
    return word
 
def english_number(val, bhs):
    if bhs == 'id':
        denom = dic['denom_id']
    elif bhs == 'en':
        denom = dic['denom']
    if val < 100:
        return _convert_nn(val, bhs)
    if val < 1000:
        return _convert_nnn(val, bhs)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l, bhs) + ' ' + denom[didx]
            if r > 0:
                ret = ret + ' ' + english_number(r, bhs)
            if bhs == 'id':
                if val < 2000:
                    ret = ret.replace("Satu Ribu", "Seribu")
                return ret

def english_number_des(val, bhs):
    if bhs == 'id':
        denom = dic['denom_id']
    elif bhs == 'en':
        denom = dic['denom']
    if val < 10:
        return _convert_n_desimal(val, bhs)

    if val < 100:
        return _convert_nn_desimal(val, bhs)

    if val < 1000:
        return _convert_nnn(val, bhs)

    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l, bhs) + ' ' + denom[didx]
            if r > 0:
                ret = ret + ' ' + english_number_des(r, bhs)

            # if bhs == 'id':
            #     if val < 2000:
            #         ret = ret.replace("Satu Ribu", "Seribu")
            #     return ret

def cur_name(cur="idr"):
    cur = cur.lower()
    if cur=="usd":
        return "Dollars"
    elif cur=="aud":
        return "Dollars"
    elif cur=="idr":
        return "Rupiah"
    elif cur=="jpy":
        return "Yen"
    elif cur=="sgd":
        return "Dollars"
    elif cur=="usd":
        return "Dollars"
    elif cur=="eur":
        return "Euro"
    else:
        return cur