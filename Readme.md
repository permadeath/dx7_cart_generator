# Random DX7 Cart Generator

## Overview
Python program to randomly generate DX7 cartridges.  For now, it uses bits taken directly from the TrueRNG V3 hardware random number generator to generate a Sysex file compatible with the Yamaha DX7 (and any other hardware or software synthesizer that can read DX7 catridge Sysex files) containing 32 truly random patches.

I will be further developing this in the future to provide other ways to generate the catridges as most people do not have the hardware necessary to generate the random bits with the method in this program.

## Dependencies
`PySerial`

`english_words`
