#!/bin/bash
p=$(pidof nginx)
kill $p
