#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: brett
"""
import xlrd
import os


class WritableObject(object):
    def _keys(self):
        keys = [k for k in self.__dict__ if not k.startswith('__')]
        return sorted(keys)

    def __repr__(self):
        s = list()
        for key in self._keys():
            s.append('{}: {}'.format(key, self.__dict__[key]))
        return ', '.join(s)


class PrimaryCareTrust(WritableObject):
    def __init__(self, name):
        self.name = name.split('(')[0].strip()
        self.code = name.split('(')[-1][:-1].strip()

    def __hash__(self):
        return self.code.__hash__()

    def __eq__(self, other):
        return self.code == other.code

    def __ne__(self, other):
        return not (self == other)


class PrimaryCareTrusts(WritableObject):
    def __init__(self):
        self._trusts = set()
    
    def add(self, trusts):
        assert isinstance(trusts, list)
        if len(trusts) == 0:
            return
        assert isinstance(trusts[0], PrimaryCareTrust)
        self._trusts |= set(trusts)

    def to_csv_string(self):
        headers = list()
        headers.append("name")
        headers.append("code")

        result = list()
        result.append(','.join(headers))
        for t in self._trusts:
            r = list()
            for h in headers:
                r.append('"{}"'.format(getattr(t, h, "")))
            result.append(','.join(r))
        return os.linesep.join(result)


class Surgery(WritableObject):
    def __init__(self, name, trust_code, total_gps, dispensing_gps, date):
        self.name = name.split(',')[0].strip()
        self.postcode = name.split(',')[-1].strip().replace('\n', ' ')
        self.trust_code = trust_code
        date = date.replace(' ', '_')
        self.date = date
        self.total_count = total_gps
        self.dispensing_count = dispensing_gps
    

class Surgeries(WritableObject):
    def __init__(self):
        self._surgeries = dict()
        self._dates = list()

    @staticmethod
    def _total_name(date):
        return "tot_" + str(date)

    @staticmethod
    def _dispensing_name(date):
        return "dis_" + str(date)

    def add(self, surgery_list):
        assert isinstance(surgery_list, list)
        for s in surgery_list:
            assert isinstance(s, Surgery)
            if s.date not in self._dates:
                self._dates.append(s.date)
            if s.name not in self._surgeries:
                d = dict()
                self._surgeries[s.name] = d
                d["name"] = s.name
                d["postcode"] = s.postcode
                d["trust_code"] = s.trust_code
            else:
                d = self._surgeries[s.name]
            assert d["name"] == s.name
            d[Surgeries._total_name(s.date)] = s.total_count
            d[Surgeries._dispensing_name(s.date)] = s.dispensing_count

    def to_csv_string(self):
        headers = list()
        headers.append("name")
        headers.append("postcode")
        headers.append("trust_code")
        headers.extend([Surgeries._total_name(d) for d in self._dates])
        headers.extend([Surgeries._dispensing_name(d) for d in self._dates])

        result = list()
        result.append(','.join(headers))
        for s in self._surgeries.itervalues():
            r = list()
            for h in headers:
                r.append('"{}"'.format(s.get(h, "")))
            result.append(','.join(r))
        return os.linesep.join(result)


def read_practices(fname):
    book = xlrd.open_workbook(fname)
    assert book.nsheets == 1

    sheet = book.sheets()[0]
    assert sheet.ncols == 8

    trusts = list()
    surgeries = list()
    date = None
    for i in range(sheet.nrows):
        row = sheet.row(i)
        if row[1].value == 'Dispensing Practices Address Details':
            current_trust = None
        elif row[1].value == 'Primary Care Trust:':
            current_trust = PrimaryCareTrust(row[2].value)
            trusts.append(current_trust)
        elif row[1].value == 'Report For:':
            date = row[2].value
        elif row[1].value == 'Practice Name and Address':
            pass  # do nothing
        else:
            assert current_trust is not None
            s = Surgery(row[1].value, current_trust.code, int(row[5].value), int(row[7].value), date)
            surgeries.append(s)

    return trusts, surgeries


def main():
    practice_docs = list()
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-01-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-02-28.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-03-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-04-30.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-05-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-06-30.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-07-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-08-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-09-30.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-10-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-11-30.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2014-12-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2015-01-31.xls'))
    practice_docs.append(os.path.join('raw_data', 'Disp Pracs Name and Address 2015-02-28.xls'))

    trusts = PrimaryCareTrusts()
    surgeries = Surgeries()
    for practice in practice_docs:
        t, s = read_practices(practice)
        trusts.add(t)
        surgeries.add(s)

    with open(os.path.join('data', 'nhs_trusts.csv'), 'w') as f:
        f.write(trusts.to_csv_string())

    with open(os.path.join('data', 'gp_surgeries.csv'), 'w') as f:
        f.write(surgeries.to_csv_string())


if __name__ == '__main__':
    main()

