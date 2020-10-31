#!/bin/bash

#python3 network_start.py &
#simulaqron start --keep --nodes 'Alice, Bob, Charlie' --topology '{"Alice": ["Charlie"], "Bob": ["Charlie"], "Charlie": ["Alice", "Bob"]}'
simulaqron start --keep
python3 charlieNode.py &
python3 aliceNode.py
simulaqron stop