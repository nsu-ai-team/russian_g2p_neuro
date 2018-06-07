#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import codecs
import os


def check_transcription(phones_list):
    if len(phones_list) == 0:
        return False
    ok = True
    admissible_characters = set(u'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    for cur_phone in phones_list:
        if len(cur_phone) == 0:
            ok = False
            break
        if cur_phone[0].isdigit():
            ok = False
            break
        if not(set(cur_phone) <= admissible_characters):
            ok = False
            break
        if not cur_phone[0].isupper():
            ok = False
            break
    return ok


def check_token(checked):
    if len(checked) == 0:
        return False
    if checked.isalpha():
        return True
    if u'\'' not in checked:
        return False
    return all(filter(lambda it: (len(it) > 0) and it.isalpha(), checked.split(u'\'')))


def get_token(source_word):
    found_idx1 = source_word.find(u'(')
    found_idx2 = source_word.find(u')')
    if (found_idx1 < 0) and (found_idx2 < 0):
        cleaned_word = source_word
    else:
        if (found_idx1 >= 0) and (found_idx2 >= 0):
            if (found_idx1 > 0) and (found_idx2 == len(source_word) - 1):
                if source_word[(found_idx1 + 1):found_idx2].isdigit():
                    cleaned_word = source_word[:found_idx1]
                else:
                    cleaned_word = u''
            else:
                cleaned_word = u''
        else:
            cleaned_word = u''
    if len(cleaned_word) > 0:
        if u'-' in cleaned_word:
            if not all(filter(lambda it: check_token(it), cleaned_word.split(u'-'))):
                cleaned_word = u''
        else:
            if not check_token(cleaned_word):
                cleaned_word = u''
    return cleaned_word


def load_lexicon(file_name):
    line_idx = 1
    words = dict()
    with codecs.open(file_name, mode='r', encoding='utf-8', errors='ignore') as fp:
        cur = fp.readline()
        while len(cur) > 0:
            prep = cur.strip()
            if len(prep) > 0:
                parts = prep.split()
                assert len(parts) >= 2, 'File "{0}": line {1} is wrong!'.format(file_name, line_idx)
                assert check_transcription(parts[1:]), u'File "{0}": line {1} is wrong!'.format(file_name, line_idx)
                new_token = get_token(parts[0])
                assert len(new_token) > 0, u'File "{0}": line {1} is wrong!'.format(file_name, line_idx)
                new_transcription = ' '.join(parts[1:])
                if new_token in words:
                    words[new_token].append(new_transcription)
                else:
                    words[new_token] = [new_transcription]
            cur = fp.readline()
            line_idx += 1
    return words


def main():
    parser = ArgumentParser()
    parser.add_argument('-s', '--src', dest='src', type=str, required=True, help=u'Source name of dictionary.')
    parser.add_argument('-d', '--dst', dest='dst', type=str, required=True,
                        help=u'Destination name of dictionary (after its formatting).')
    args = parser.parse_args()

    src_name = os.path.normpath(args.src)
    dst_name = os.path.normpath(args.dst)

    assert os.path.isfile(src_name), u'File "{0}" does not exist!'.format(src_name)
    dst_dir = os.path.dirname(dst_name)
    assert os.path.isdir(dst_dir), u'Directory "{0}" does not exist!'.format(dst_dir)

    words_and_transcriptions = load_lexicon(src_name)
    with codecs.open(dst_name, mode='w', encoding='utf-8', errors='ignore') as fp:
        for cur_word in sorted(list(words_and_transcriptions.keys())):
            for cur_transcirption in words_and_transcriptions[cur_word]:
                fp.write(u'{0}\t{1}\n'.format(cur_word, cur_transcirption))


if __name__ == '__main__':
    main()
