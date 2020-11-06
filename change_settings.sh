#!/bin/bash
#simulaqron set max-qubits 100
#simulaqron set noisy-qubits on
venv/bin/simulaqron set max-qubits 100
venv/bin/simulaqron set noisy-qubits off
venv/bin/simulaqron set t1 1.0
venv/bin/simulaqron set backend stabilizer
