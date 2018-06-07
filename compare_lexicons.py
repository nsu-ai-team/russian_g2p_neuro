#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import copy
import os

from Levenshtein import editops

from prepare_dict import load_lexicon


def prepare_transcriptions_for_levenshtein(first_transcription, second_transcription):
    start_code = 128
    phonecodes = dict()
    for cur in set(first_transcription.split()) | set(second_transcription.split()):
        phonecodes[cur] = start_code
        start_code += 1
    try:
        int_to_chr = unichr
    except:
        int_to_chr = chr
    return u''.join([int_to_chr(phonecodes[cur1]) for cur1 in first_transcription.split()]), \
           u''.join([int_to_chr(phonecodes[cur2]) for cur2 in second_transcription.split()])


def prepare_ops(ops):
    n_substitutions = 0
    n_deletions = 0
    n_insertions = 0
    for cur in ops:
        if cur[0] == 'delete':
            n_deletions += 1
        elif cur[0] == 'replace':
            n_substitutions += 1
        else:
            n_insertions += 1
    return {'replace': n_substitutions, 'delete': n_deletions, 'insert': n_insertions}


def find_best_pair(left_transcriptions, right_transcriptions):
    prep_left, prep_right = prepare_transcriptions_for_levenshtein(left_transcriptions[0], right_transcriptions[0])
    best_ops = prepare_ops(editops(prep_left, prep_right))
    best_phone_error_rate = (best_ops['replace'] + best_ops['delete'] + best_ops['insert']) / float(len(prep_left))
    best_pair = (left_transcriptions[0], right_transcriptions[0])
    for cur_left in left_transcriptions:
        for cur_right in right_transcriptions:
            prep_left, prep_right = prepare_transcriptions_for_levenshtein(cur_left, cur_right)
            cur_ops = prepare_ops(editops(prep_left, prep_right))
            cur_phone_error_rate = (cur_ops['replace'] + cur_ops['delete'] + cur_ops['insert']) / float(len(prep_left))
            if cur_phone_error_rate < best_phone_error_rate:
                best_phone_error_rate = cur_phone_error_rate
                best_ops = copy.copy(cur_ops)
                best_pair = (cur_left, cur_right)
    return best_pair, best_ops


def compare_lexicons(true_lexicon_name, predicted_lexicon_name):
    true_lexicon = load_lexicon(true_lexicon_name)
    predicted_lexicon = load_lexicon(predicted_lexicon_name)
    assert set(true_lexicon.keys()) == set(predicted_lexicon.keys()), \
        'File "{0}" does not correspond to file "{1}": word lists are not equal!'.format(true_lexicon_name,
                                                                                         predicted_lexicon_name)
    all_words = sorted(list(true_lexicon))
    n_substitutions = 0
    n_deletions = 0
    n_insertions = 0
    n_all = 0
    word_errors = 0
    for cur_word in all_words:
        best_pair, ops = find_best_pair(true_lexicon[cur_word], predicted_lexicon[cur_word])
        n_all += len(best_pair[0].split())
        n_deletions += ops['delete']
        n_insertions += ops['insert']
        n_substitutions += ops['replace']
        if (ops['delete'] > 0) or (ops['insert'] > 0) or (ops['replace'] > 0):
            word_errors += 1
    return word_errors / float(len(all_words)), (n_substitutions + n_deletions + n_insertions) / float(n_all)


def main():
    parser = ArgumentParser()
    parser.add_argument('-t', '--true', dest='true_lexicon_name', type=str, required=True,
                        help=u'Name of true phonetical dictionary.')
    parser.add_argument('-p', '--predicted', dest='predicted_lexicon_name', type=str, required=True,
                        help=u'Name of predicted phonetical dictionary.')
    args = parser.parse_args()

    true_file_name = os.path.normpath(args.true_lexicon_name)
    assert os.path.isfile(true_file_name), 'File "{0}" does not exist!'.format(true_file_name)

    predicted_file_name = os.path.normpath(args.predicted_lexicon_name)
    assert os.path.isfile(predicted_file_name), 'File "{0}" does not exist!'.format(predicted_file_name)

    wer, per = compare_lexicons(true_file_name, predicted_file_name)
    print(u'')
    print(u'Word error rate: {0:.2%}'.format(wer))
    print(u'Phone error rate: {0:.2%}'.format(per))


if __name__ == '__main__':
    main()
