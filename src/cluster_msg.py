#!/usr/bin/env Python
# coding=utf-8
'''
Created on 2017-11-14
@author: neyson
@brief: incremental-version message cluster system
'''

import os,re,sys,gl
from tokens import JiebaTokenizer
from simhash import SimhashBuilder, hamming_distance
from minhash import MinhashBuilder
from features import FeatureBuilder, get_user_keywords
from workdict import WordDictBuilder
from cluster import Cluster

class FeatureContainer:
    def __init__(self, word_dict, keyword_dict=None):
        # Load word list
        self.word_list = []
        self.word_dict = {}
        l = [(value, key) for key, value in word_dict.items()]
        l = sorted(l, reverse=True)
        for idx, (value, key) in enumerate(l):
            self.word_list.append(key)
            self.word_dict[key.decode('utf8')] = idx
                
        self.fb = FeatureBuilder(self.word_dict, keyword_dict)
        self.smb = SimhashBuilder(self.word_list)
        self.mnb = MinhashBuilder()
        print 'FeatureContainer OK'

    def compute_feature(self, token_list):
        new_words = []
        for token in token_list:
            if not token in self.word_dict:
                new_words.append(token)
        if len(new_words) != 0:
            # Update word_list and word_dict
            self.fb.update_words(new_words)
            self.smb.update_words([word.encode('utf8') for word in new_words])
            self.word_dict = self.fb.word_dict
            self.word_list.extend([word.encode('utf8') for word in new_words])
        feature_vec = self.fb.compute(token_list)
        sim_hash, hash_vec = self.smb.sim_hash_nonzero(feature_vec)
        min_hash = self.mnb.min_hash(hash_vec)
        return feature_vec, sim_hash, min_hash

def token_message(jt, msg_fname):
    token_lines = []
    with open(msg_fname) as ins:
        for line in ins:
            line = line.strip().decode('utf8')
            tokens = jt.tokens(line)
            token_lines.append(u' '.join(tokens).encode('utf8'))
    print 'Token file: ', msg_fname
    return token_lines


def cluster_message(stop_words, user_dict, msg_fname, cluster_file, summary_file):
    # Init tokenizer
    jt = JiebaTokenizer(stop_words, user_dict, 'c')
    token_lines = token_message(jt, msg_fname)
    wdb = WordDictBuilder()
    wdb.add_tokens_list(token_lines)
    wdb.save('../data/word_dict.txt')
    keyword_dict = get_user_keywords(user_dict)
    
    cluser = Cluster(gl.gl_FUNCNUM)
    # Init feature_builder and simhash_builder 
    fc = FeatureContainer(wdb.word_dict, keyword_dict)
    with open(msg_fname, 'r') as ins:
        for lineidx, line in enumerate(ins.readlines()):
            if(lineidx % 100 == 0):
                print lineidx
            (time, number, sender, message) = line.strip().split('|')[0:4]
            if(number=='10658368'):
                continue
            #替换数字、字母，截取第一句
            short_msg = re.split(u'。'.encode('utf8'),message)[0]
            new_msg = re.sub(r'[0-9a-zA-Z+=\./:\"<>|_&#\s\*\-]', '', short_msg)
            #new_msg = re.split(u'。'.encode('utf8'), re.sub(r'[0-9a-zA-Z+=\./:\"<>|_&#\s\*\-]', '', message))[0]

            # Tokenize
            tokens = jt.tokens(new_msg.strip().decode('utf8'))
            feature_vec, sim_hash, min_hash = fc.compute_feature(tokens)
            cluser.add_one(min_hash, sim_hash, short_msg)
            
    cluser.save_cluster(cluster_file, summary_file)
    print "cluser finish"
            
   
if __name__=="__main__":
    if len(sys.argv) < 6:
        print "Usage:\tcluster_msg.py <stop_words_path> <user_dict_path> <message_path> <cluster_file_path> <summary_file_path>"
        exit(-1)
    cluster_message(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])    
           
