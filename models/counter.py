# -*- coding: utf-8 -*-

__revision__ = '$Id$'

from google.appengine.api import memcache
from google.appengine.ext import ndb as db


NUM_SHARDS = 4


class CounterShardConfig(db.Model):
    name = db.StringProperty()
    num_shards = db.IntegerProperty(default=NUM_SHARDS)


class CounterShard(db.Model):
    name = db.StringProperty()
    count = db.IntegerProperty(default=0)


def get_count(name):
    total = memcache.get(name)
    if total is None:
        total = 0
        for counter in CounterShard.query(CounterShard.name==name).fetch(NUM_SHARDS):
            total = total + counter.count
        memcache.add(name, total, 60)
    return total

def increment(name):
    config = CounterShardConfig.get_or_insert(name, name=name)
    def txn():
        index = random.randint(0, config.num_shards - 1)
        shard_name = name + str(index)
        counter = CounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = CounterShard(key_name=shard_name, name=name)
        counter.count += 1
        counter.put()
