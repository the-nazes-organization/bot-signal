#!/bin/bash

signal-cli link > link & 
sleep 1
qrencode -t ansiutf8 < link
