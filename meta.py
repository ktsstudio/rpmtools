#!/usr/bin/env python
__author__ = 'grigory51'
import json, sys, argparse


def help():
    print('meta.py -f <input file> -q <query>')


class JsonParser(object):
    def __init__(self, txt):
        self.data = txt
        if isinstance(txt, str):
            self.data = json.loads(txt)

    def __parse_query(self, query, limit=0):
        result = []
        acc = ''
        i = 0
        count = 0
        flag = False
        for letter in query:
            i += 1
            if letter == '\\':
                flag = True
            elif letter == '.':
                if flag:
                    flag = False
                    acc += "\\" + letter
                    continue
                result.append(acc)
                count += 1
                acc = ''
                if limit > 0 and count >= limit:
                    acc = query[i:]
                    break
            else:
                acc += letter
        result.append(acc)
        for i in range(len(result)):
            result[i] = result[i].replace('\\.', '.')
        return result

    def get(self, query, data=None, hop=0):
        if hop == 0:
            data = self.data
            query = self.__parse_query(query)
        if data is None:
            return None

        key = query[0]
        if isinstance(data, dict):
            next_data = data.get(key, None)
        elif isinstance(data, list):
            next_data = data[int(key)]
        else:
            next_data = None

        if len(query) == 1:
            return next_data
        else:
            return self.get(query[1:], next_data, hop + 1)


if __name__ == '__main__':
    argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, required=True)
    parser.add_argument('--query', type=str, required=True)
    parser.add_argument('--keys', action='store_true')
    parser.add_argument('--escape', action='store_true')
    args = parser.parse_args()

    try:
        f = open(args.file, 'r')
    except IOError as e:
        sys.stderr.write(str(e.strerror) + '\n')
        exit(2)

    parser = JsonParser(f.read())
    f.close()

    value = parser.get(args.query)
    if value is not None:
        if isinstance(value, list):
            print('\n'.join(value))
        elif isinstance(value, dict):
            if args.keys:
                print(' '.join([i.replace('.', '\.') if args.escape else i for i in value.keys()]))
            else:
                print(value)
        elif isinstance(value, bool):
            print(str(value).lower())
        else:
            print(value)
