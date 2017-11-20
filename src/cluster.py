#!/usr/bin/env python
'''
Created on 2017-11-13
@author neyson
@brief utils for cluster
'''
import os, sys, gl
from simhash import SimhashBuilder, hamming_distance
from minhash import MinhashBuilder     

class Cluster(dict):
    """
    @brief init, update and save word dictionary
    """
    def __init__(self, threshold, cluser_path=None):
        self.threshold = float(threshold)
        if cluser_path is not None:
            self.load_cluser(cluser_path)
            
    def load_cluser(self, cluser_path):
        self.cluser_path = cluser_path
        print 'Cluster Loading cluser info from %s...' % cluser_path
        self.clear()
        with open(cluser_path, 'r') as ins:
            for line in ins.readlines():
                min_hash,center,sim_hash, content = line.strip().split('|')
                class_list = [(sim_hash, content)]
                if not min_hash in self:
                    self.setdefault(min_hash, {center, class_list})
                elif not center in self[min_hash]:
                    self[min_hash][center]==class_list
                else:
                    self[min_hash][center].append((sim_hash, content))
        return self
    
    def add_one(self, min_hash, sim_hash, content):
        if not min_hash in self:
            class_list = [(sim_hash, content)]
            self[min_hash]={}
            self[min_hash][sim_hash]=class_list
            
        else:
            joinclass = 0
            for center, class_list in self[min_hash].items():
                if hamming_distance(sim_hash, center)<self.threshold :
                    class_list.append((sim_hash, content))
                    joinclass = 1
                    break
            if(not joinclass):
                self[min_hash][sim_hash]=[(sim_hash, content)] 
                
        return self
    
    def save_cluster(self, cluser_path, summary_path=None):
        if cluser_path is None:
            return

        print 'Saving cluser info to %s...' % cluser_path
        num_list=[]
        center_list = []
        for min_hash,class_dict in self.items():
            for center,class_list in class_dict.items():
                length = len(class_list)
                num_list.append((length,min_hash,center,class_list))
            
        with open(cluser_path, 'w') as outs:
            #for center, class_list in sorted(minhash_dict):
            for (length,min_hash,center,class_list) in sorted(num_list, key = lambda num:num[0],reverse=True):
                for (sim_hash, content) in sorted(class_list, key = lambda kv:kv[0],reverse=True):
                    outs.write(min_hash+"|"+str(center)+"|"+str(sim_hash)+"|"+ content+"\n")  #sim_hash, content 
                    #print min_hash+"|"+center+"|"+class_list[j][0]+"|"+ class_list[j][1]+"\n"  #sim_hash, content
                if length > 10:
                    center_list.append(min_hash+"|"+str(center)+"|"+str(length)+'|'+class_list[0][1])
                    #print min_hash + "|" +center + "|" + str(length)
                    
        if cluser_path is not None:
            with open(summary_path, 'w') as outs:
                for  line in center_list:
                    outs.write("%s\n" % line)
    
    #def __del__(self):
    #    self.save_cluster(self.cluser_path)
       
if __name__ == '__main__':

    if len(sys.argv) < 4:
        print "Usage:\tcluser.py <word_dict_path> <feature_file> <cluster_file> <summary_file>"
        exit(-1)
    word_list = []
    with open(sys.argv[1], 'r') as ins:
        for idx, line in enumerate(ins.readlines()):
            word_list.append(line.split()[1])
            #print '\rloading word', idx,
    sim_b = SimhashBuilder(word_list)
    min_b = MinhashBuilder()
    cluser = Cluster(gl.gl_THRESHOLD)
    result_lines = []
    print ''
    with open(sys.argv[2], 'r') as ins:
        for idx, line in enumerate(ins.readlines()):
            print '\rprocessing doc', idx,
            feature_vec = line.strip().split()
            feature_vec = [(int(item.split(':')[0]),float(item.split(':')[1])) for item in feature_vec]
            sim_hash, hashvec = sim_b.sim_hash_nonzero(feature_vec)
            min_hash= min_b.min_hash(hashvec);
            cluser.add_one(min_hash, sim_hash, line)

    cluser.save_cluster(sys.argv[3], sys.argv[4])
    print "cluser finish"


    
