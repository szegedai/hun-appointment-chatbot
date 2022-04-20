#!/bin/bash

autossh -4 -L 0.0.0.0:8000:localhost:8080 -i /.ssh/id_rsa -o "StrictHostKeyChecking no" -p 5022 ubuntu@rgai2.inf.u-szeged.hu sleep infinity

