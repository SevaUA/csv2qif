#!/usr/bin/env python
# coding: utf8
'''
CSV2QIF
=======

This script converts the CSV provided by homemoney.ua to a QIF format.

'''
import sys
import csv
from datetime import datetime

def read_csv(statement_file, output):
    ''' reads a csv statement file and returns the converted data
    '''
    default_currency = 'UAH'
    csv_reader = csv.reader(statement_file, delimiter=';')
    temp_data = []
    for row in csv_reader:
        try:
            date, account, category, total, currency, description, transfer = row[:7]
            date = datetime.strptime(date, '%d.%m.%Y')

            account = 'Активы:Текущие активы:' + account

            total = total.replace('.', '')
            total = total.replace(',', '.')
            if total:
                total = float(total)
            else:
                total = 0

            category = category.replace('\\', ':')
            if total >= 0:
                category = 'Доходы:' + category
            else:
                category = 'Расходы:' + category

            if currency != default_currency:
                account = account + ' - ' + currency
                category = category + ' - ' + currency

            if transfer != '':
                if temp_data == []:
                    temp_data = [date, account, category, total, currency, description, transfer, ]
                    continue
            if temp_data == []:
                trans = simple_trans(date, account, category, total, description)
                write_to_qif(trans, output)
            else:
                currency_temp = temp_data[4]
                account_temp = temp_data[1]
                total_temp = temp_data[3]
                if currency == currency_temp:
                    trans = simple_trans(date, account, account_temp, total, description)
                    write_to_qif(trans, output)
                else:
                    trans = multi_trans(date, account_temp, account, total_temp, total, description)
                    write_to_qif(trans, output)
                temp_data = []
            #print csv_reader.line_num
        except Exception, e:
            print csv_reader.line_num
            print row
            raise

def simple_trans(date, account, category, total, description):
    ret = '''!Account
N{}
TCash
^
!Type:Cash
D{}
T{}
M{}
L[{}]
^
'''.format(str(account),date.strftime("%d/%m/%Y"),str(total),str(description),str(category))
    return ret

def multi_trans(date, account_from, account_to, total_from, total_to, description):
    ret = '''!Account
N{0}
TCash
^
!Type:Cash
D{1}
T{2}
M{3}
L[Собственные средства:Обмен]
^
!Account
NСобственные средства:Обмен
TCash
^
!Type:Cash
D{1}
T{5}
M{3}
L[{4}]
^
'''.format(
    str(account_from),
    date.strftime("%d/%m/%Y"),
    str(total_from),
    str(description),
    str(account_to),
    str(total_to)
    )
    return ret

def write_to_qif(data, outputfile):
    outputfile.write(data)
    
def main(statement_file):
    ''' driver function
    '''

    try:
        statement = open(statement_file)
    except IOError, error:
        print 'could not open statement file: %s\n\t%s' % \
            (statement_file, str(error), )
        sys.exit(1)

    try:
        output = file(statement.name.replace('csv', 'qif'), 'w')
    except IOError, error:
        print 'could not open output file: %s\n\t%s' % \
            (statement.name.replace('csv', 'qif'), str(error), )

    read_csv(statement, output)

    print 'converted data saved to %s file' % \
            (statement.name.replace('csv', 'qif'), )

    statement.close()
    output.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print './cvs2qif.py statement.csv'
        sys.exit(1)
    else:
        main(sys.argv[1])
