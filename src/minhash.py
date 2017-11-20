#! /usr/local/bin/python
#coding:gbk

import os, hashlib, math, random, sys
import re, gl
from simhash import SimhashBuilder, hamming_distance

class MinhashBuilder:
    def __init__(self, func_num=gl.gl_FUNCNUM, hashbits=gl.gl_HASHBIT):
        self.func_num = func_num
        self.hashbits = hashbits
        self.func_list = [self._generate_hash_func() for i in range(func_num)]
        print "MinhashBuilder finish"
        
    def _generate_prime(self, len):
      is_prime = [1] * (len + 1)
      for i in range(2, int(math.sqrt(len)) + 1):
        if is_prime[i] == 1:
          j = i
          for j in range(i, len):
            if i * j > len:
              break
            is_prime[i * j] = 0
    
      is_prime[0] = 0
      is_prime[1] = 0
      is_prime[2] = 0
      prime_list = []
      for i in range(len):
        if is_prime[i] == 1:
          prime_list.append(i)
      return prime_list

    def _generate_hash_func(self):
        prime_list = self._generate_prime(1000)
        prime_len = len(prime_list)
        random_a = random.randint(0,prime_len - 1)
        random_b = random.randint(0,prime_len - 1)
        while random_a == random_b:
            ndom_b = random.randint(0,prime_len - 1)
        def min_hash_func(x):
            return (prime_list[random_a] * x + prime_list[random_b])%self.hashbits
        #print prime_list[random_a],prime_list[random_b]
        return min_hash_func

    def min_hash(self, hash_data):
        cols = len(hash_data)
        sigmatrix = [1000000] * self.func_num
        
        for c in range(cols):
            if hash_data[c] == 0:
                continue
            hashvalue = map(lambda x: x(c), self.func_list)
            for i in range(self.func_num):
                if sigmatrix[i] > hashvalue[i]:
                    sigmatrix[i] = hashvalue[i]
        min_hash_str = ''
        for i in range(len(sigmatrix)):
            if i == 0:
                min_hash_str += str(sigmatrix[i])
            else:
                min_hash_str += "_" + str(sigmatrix[i])
        return min_hash_str

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print "Usage:\tcluser.py <word_dict_path> <feature_file> <finger_print_file>"
        exit(-1)
    word_list = []
    with open(sys.argv[1], 'r') as ins:
        for idx, line in enumerate(ins.readlines()):
            word_list.append(line.split()[1])
            #print '\rloading word', idx,
    sim_b = SimhashBuilder(word_list)
    min_b = MinhashBuilder()
    result_lines = []
    print ''
    with open(sys.argv[2], 'r') as ins:
        for idx, line in enumerate(ins.readlines()):
            #print '\rprocessing doc', idx,
            feature_vec = line.strip().split()
            feature_vec = [(int(item.split(':')[0]),float(item.split(':')[1])) for item in feature_vec]
            fingerprint, fingervec = sim_b.sim_hash_nonzero(feature_vec)
            min_hash= min_b.min_hash(fingervec);
            result_lines.append(min_hash+'|'+str(fingerprint)+os.linesep)
    with open(sys.argv[3], 'w') as outs:
        outs.writelines(result_lines)
    print "simhash+minhash finish"

