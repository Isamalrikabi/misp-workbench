#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This code reuse the project of Brian Wallace: https://github.com/bwall/ssdc


from redis import StrictRedis
from config import redis_socket
from struct import unpack
import base64
import re
import pydeep
import argparse


class SSDC(object):

    def __init__(self):
        self.r = StrictRedis(unix_socket_path=redis_socket, decode_responses=True)

    def __get_all_7_char_chunks(self, h):
        return set((unpack("<Q", base64.b64decode(h[i:i + 7] + "=") + b"\x00\x00\x00")[0] for i in range(len(h) - 6)))

    def __preprocess_hash(self, h):
        block_size, block_data, double_block_data = h.split(':')

        # Reduce any sequence of the same char greater than 3 to 3
        re.sub(r'(\w)\1\1\1(\1+)', r'\1\1\1', block_data)
        re.sub(r'(\w)\1\1\1(\1+)', r'\1\1\1', double_block_data)

        return block_size, self.__get_all_7_char_chunks(block_data), self.__get_all_7_char_chunks(double_block_data)

    def __add_chunks_db(self, p, block_size, chunk, sha256):
        for i in chunk:
            chunk = 'ssdeep:{}:{}'.format(block_size, i)
            p.sadd(chunk, sha256)
            p.sadd('ssdeep:chunks', chunk)

    def update_chunks_db(self, sha256, deephash):
        block_size, chunk, double_chunk = self.__preprocess_hash(deephash)
        p = self.r.pipeline(False)
        self.__add_chunks_db(p, block_size, chunk, sha256)
        self.__add_chunks_db(p, block_size, double_chunk, sha256)
        p.execute()

    def generate_all_chunks(self):
        for sha256 in self.r.smembers('hashes_sha256'):
            self.update_chunks_db(sha256, self.r.hget(sha256, 'ssdeep'))

    def find_matches(self, key):
        similar_hashes = self.r.smembers(key)
        if len(similar_hashes) > 1:
            cur_hash = similar_hashes.pop()
            cur_ssdeep = self.r.hget(cur_hash, 'ssdeep')
            p = self.r.pipeline(False)
            for sha256 in similar_hashes:
                score = pydeep.compare(cur_ssdeep.encode('utf-8'), self.r.hget(sha256, 'ssdeep').encode('utf-8'))
                if score > 0:
                    key1 = 'ssdeep:matches_{}'.format(cur_hash)
                    key2 = 'ssdeep:matches_{}'.format(sha256)
                    p.zadd(key1, score, sha256)
                    p.zadd(key2, score, cur_hash)
                    p.sadd('ssdeep:all_matches', key1)
                    p.sadd('ssdeep:all_matches', key2)
            p.execute()

    def compare_similar_chunks(self):
        for key in self.r.smembers('ssdeep:chunks'):
            self.find_matches(key)

    def make_groups(self):
        all_hashes = self.r.smembers('hashes_sha256')
        while all_hashes:
            cur_hash = all_hashes.pop()
            matches = self.r.zrange('ssdeep:matches_{}'.format(cur_hash), 0, -1)
            if matches:
                if isinstance(matches, list):
                    matches = set(matches)
                else:
                    matches = set([matches])
                all_hashes -= matches
                matches |= set([cur_hash])
            else:
                # NOTE: Should we make a group?
                # matches = set([cur_hash])
                self.r.sadd('ssdeep:no_matches', cur_hash)
                continue
            key = 'ssdeep:group_{}'.format(self.r.scard('ssdeep:groups'))
            self.r.sadd('ssdeep:groups', key)
            self.r.sadd(key, *matches)

    def clean_groups(self):
        self.r.delete(*self.r.smembers('ssdeep:groups'))
        self.r.delete(*self.r.smembers('ssdeep:all_matches'))
        self.r.delete('ssdeep:groups')
        self.r.delete('ssdeep:all_matches')
        self.r.delete('ssdeep:no_matches')

    # ########## Querying ##########

    def get_all_groups(self):
        return [(g, self.r.smembers(g)) for g in self.r.smembers('ssdeep:groups')]

    def get_group_samples(self, group):
        return self.r.smembers(group)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cluster based on SSDeep data.")
    parser.add_argument('-g', '--generate', default=False, required=False, action='store_true', help='Generate clusters.')
    parser.add_argument('-c', '--clean', default=False, required=False, action='store_true', help='Clean all ssdeep cluster keys.')
    args = parser.parse_args()

    ssdc = SSDC()

    if args.generate:
        ssdc.generate_all_chunks()
        ssdc.compare_similar_chunks()
        ssdc.make_groups()
    elif args.clean:
        ssdc.clean_groups()
