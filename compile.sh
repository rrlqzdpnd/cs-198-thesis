#! /bin/bash

gcc newcode.c /usr/include/nfc/utils/mifare.c -o newcode -lnfc
