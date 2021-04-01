#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import codecs
import os
import random
import tempfile

import numpy as np

from prepare_dict import load_lexicon
from compare_lexicons import compare_lexicons


def create_tmp_file_name():
    basedir = os.path.join(os.path.dirname(__file__), 'data', 'tmp')
    fp = tempfile.NamedTemporaryFile(mode='w', dir=basedir, delete=False)
    filename = fp.name
    fp.close()
    return filename


def split_words_and_transcriptions_for_cv(words_and_transcriptions, cv):
    assert len(words_and_transcriptions) > 0, 'List of texts is empty!'
    assert cv > 0, 'Number of folds for crossvalidation must be a positive integer value!'
    assert len(words_and_transcriptions) >= cv, '{0} > {1}. Number of folds for crossvalidation is too large!'.format(
        cv, len(words_and_transcriptions)
    )
    folds = list()
    fold_size = len(words_and_transcriptions) // cv
    words = sorted(list(words_and_transcriptions.keys()))
    random.shuffle(words)
    for fold_ind in range(cv):
        start_text_idx = fold_ind * fold_size
        end_text_idx = (fold_ind + 1) * fold_size
        words_for_training = list()
        for cur_word in sorted(words[:start_text_idx] + words[end_text_idx:]):
            for cur_transcription in words_and_transcriptions[cur_word]:
                words_for_training.append(u'{0}\t{1}\n'.format(cur_word, cur_transcription))
        words_for_testing = list()
        for cur_word in sorted(words[start_text_idx:end_text_idx]):
            for cur_transcription in words_and_transcriptions[cur_word]:
                words_for_testing.append(u'{0}\t{1}\n'.format(cur_word, cur_transcription))
        folds.append((tuple(words_for_training), tuple(words_for_testing)))
    return folds


def main():
    parser = ArgumentParser()
    parser.add_argument('-s', '--src', dest='word_list', required=True, type=str,
                        help='Source file with words without their phonetical transcriptions.')
    parser.add_argument('-t', '--train', dest='lexicon_for_training', type=str, required=False,
                        default=os.path.join(os.path.dirname(__file__), 'data', 'ru_training.dic'),
                        help='File with source vocabulary for training.')
    parser.add_argument('-d', '--dst', dest='destination_lexicon', type=str, required=True,
                        help='Destination file into which the creating phonetic transcriptions shall be written.')
    parser.add_argument('--cv', dest='cv', type=int, required=False, default=None,
                        help='Fold number for crossvalidation (if it is not '
                             'specified, then cross-validation will not be '
                             'executed, and final training will be started '
                             'right away).')
    parser.add_argument('-n', '--ngram', dest='ngram', type=int, required=False, default=5, help='Maximal N-gram size.')
    parser.add_argument('-p', '--pmass', dest='pmass', type=float, required=False, default=0.85,
                        help='% of total probability mass constraint for transcriptions generating.')
    parser.add_argument('--seed', dest='seed', type=int, required=False, default=0, help='Random seed.')
    args = parser.parse_args()

    src_wordlist_name = os.path.normpath(args.word_list)
    assert os.path.isfile(src_wordlist_name), u'File "{0}" does not exist!'.format(src_wordlist_name)
    dst_vocabulary_name = os.path.normpath(args.destination_lexicon)
    dst_vocabulary_dir = os.path.dirname(dst_vocabulary_name)
    assert os.path.isdir(dst_vocabulary_dir), u'Directory "{0}" does not exist!'.format(dst_vocabulary_dir)
    training_vocabulary_name = os.path.normpath(args.lexicon_for_training)
    assert os.path.isfile(training_vocabulary_name), u'File "{0}" does not exist!'.format(training_vocabulary_name)
    cv = args.cv
    if cv is not None:
        assert cv > 1, u'Fold number for crossvalidation is too small!'
    ngram = args.ngram
    assert ngram > 1, u'Maximal N-gram size is too small!'
    pmass = args.pmass
    assert (pmass > 0.0) and (pmass <= 1.0), u'% of total probability mass constraint is wrong!'

    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    random.seed(args.seed)
    words_and_transcriptions = load_lexicon(training_vocabulary_name)
    if cv is not None:
        folds = split_words_and_transcriptions_for_cv(words_and_transcriptions, cv)
        WERs = list()
        PERs = list()
        for cur_fold in folds:
            tmp_file_for_training = create_tmp_file_name()
            tmp_file_for_testing = create_tmp_file_name()
            tmp_file_for_wordlist = create_tmp_file_name()
            tmp_file_for_result = create_tmp_file_name()
            try:
                with codecs.open(tmp_file_for_training, mode='w',
                                 encoding='utf-8', errors='ignore') as fp:
                    for cur in cur_fold[0]:
                        fp.write(cur)
                with codecs.open(tmp_file_for_testing, mode='w',
                                 encoding='utf-8', errors='ignore') as fp:
                    for cur in cur_fold[1]:
                        fp.write(cur)
                with codecs.open(tmp_file_for_wordlist, mode='w',
                                 encoding='utf-8', errors='ignore') as fp:
                    for cur in cur_fold[1]:
                        fp.write(cur.split()[0] + '\n')
                cmd = u'phonetisaurus-train --lexicon "{0}" --dir_prefix "{1}" --model_prefix russian_g2p ' \
                      u'--ngram_order {2} --seq2_del'.format(
                    tmp_file_for_training, model_dir, ngram)
                os.system(cmd)
                cmd = u'phonetisaurus-apply --model "{0}" --word_list "{1}" -p {2} -a > "{3}"'.format(
                    os.path.join(model_dir, 'russian_g2p.fst'),
                    tmp_file_for_wordlist, pmass, tmp_file_for_result
                )
                os.system(cmd)
                word_error_rate, phone_error_rate = compare_lexicons(
                    tmp_file_for_testing, tmp_file_for_result)
                WERs.append(word_error_rate)
                PERs.append(phone_error_rate)
            finally:
                if os.path.isfile(tmp_file_for_training):
                    os.remove(tmp_file_for_training)
                if os.path.isfile(tmp_file_for_testing):
                    os.remove(tmp_file_for_testing)
                if os.path.isfile(tmp_file_for_wordlist):
                    os.remove(tmp_file_for_wordlist)
                if os.path.isfile(tmp_file_for_result):
                    os.remove(tmp_file_for_result)
                for cur in filter(lambda it: it.startswith(u'russian_g2p'),
                                  os.listdir(model_dir)):
                    os.remove(os.path.join(model_dir, cur))
        WERs = np.array(WERs, dtype=np.float64)
        PERs = np.array(PERs, dtype=np.float64)
        print(u'')
        print(u'Word error rate is {0:.2%} +- {1:.2%}'.format(WERs.mean(), WERs.std()))
        print(u'Phone error rate is {0:.2%} +- {1:.2%}'.format(PERs.mean(), PERs.std()))
        print(u'')
        print(u'Crossvalidation is finised...')

    tmp_file_for_training = create_tmp_file_name()
    tmp_file_for_result = create_tmp_file_name()
    try:
        with codecs.open(tmp_file_for_training, mode='w', encoding='utf-8', errors='ignore') as fp:
            for cur_word in sorted(list(words_and_transcriptions.keys())):
                for cur_transcription in words_and_transcriptions[cur_word]:
                    fp.write(u'{0}\t{1}\n'.format(cur_word, cur_transcription))
        print(u'')
        print(u'Final training is started...')
        cmd = u'phonetisaurus-train --lexicon "{0}" --dir_prefix "{1}" --model_prefix russian_g2p ' \
              u'--ngram_order {2} --seq2_del'.format(tmp_file_for_training, model_dir, ngram)
        os.system(cmd)
        print(u'')
        print(u'Final training is finished...')
        print(u'')
        print(u'Final recognition of transcriptions for words is started...')
        cmd = u'phonetisaurus-apply --model "{0}" --word_list "{1}" -p {2} -a > "{3}"'.format(
            os.path.join(model_dir, 'russian_g2p.fst'), src_wordlist_name, pmass, tmp_file_for_result
        )
        os.system(cmd)
        print(u'')
        print(u'Final recognition of transcriptions for words is finished...')
        predicted_phonetic_dictionary = load_lexicon(tmp_file_for_result)
    finally:
        if os.path.isfile(tmp_file_for_training):
            os.remove(tmp_file_for_training)
        if os.path.isfile(tmp_file_for_result):
            os.remove(tmp_file_for_result)

    for cur_word in predicted_phonetic_dictionary:
        if cur_word in words_and_transcriptions:
            for cur_transcription in predicted_phonetic_dictionary[cur_word]:
                if cur_transcription not in words_and_transcriptions[cur_word]:
                    words_and_transcriptions[cur_word].append(cur_transcription)
        else:
            words_and_transcriptions[cur_word] = predicted_phonetic_dictionary[cur_word]
    with codecs.open(dst_vocabulary_name, mode='w', encoding='utf-8', errors='ignore') as fp:
        for cur_word in sorted(list(words_and_transcriptions.keys())):
            fp.write(u'{0} {1}\n'.format(cur_word, words_and_transcriptions[cur_word][0]))
            for ind in range(1, len(words_and_transcriptions[cur_word])):
                fp.write(u'{0}({1}) {2}\n'.format(cur_word, ind + 1, words_and_transcriptions[cur_word][ind]))


if __name__ == '__main__':
    main()
