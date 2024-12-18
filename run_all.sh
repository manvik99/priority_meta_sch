#!/bin/bash
> main.log
rm test/w0.txt
rm test/w1.txt
rm test/w2.txt
rm test/w3.txt
sleep 0.1

python w0.py &
sleep 0.1
python w1.py &
sleep 0.5
python w3.py &
sleep 0.5
python w0.py &
wait
