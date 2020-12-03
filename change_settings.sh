#!/bin/bash

venv/bin/simulaqron set max-qubits 1000
venv/bin/simulaqron set noisy-qubits off
venv/bin/simulaqron set t1 1.0
venv/bin/simulaqron set backend stabilizer
venv/bin/simulaqron set log-level 40
venv/bin/simulaqron set recv-timeout 10000
venv/bin/simulaqron set recv-retry-time 0.05



