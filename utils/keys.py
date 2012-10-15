# -*- coding: utf-8 -*-


def key(*parts):
	return ':'.join([x.encode('utf-8') for x in parts])