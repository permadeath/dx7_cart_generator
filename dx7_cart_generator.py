from english_words import english_words_lower_alpha_set
import serial

#   Choose serial port.  If unknown, refer to TrueRNG V3
#   documentation and/or your OS documentation.
ser_port = ''

# Generate a list of 4096 7-letter English words
patch_name_list = []
words = list(english_words_lower_alpha_set)
for check in range(len(words)):
    if len(words[check]) == 7:
        patch_name_list.append(words[check])
with serial.Serial('COM5', 19200, timeout=1) as ser:
    x = ser.read(4117)
low_byte = list(x)
for i in range(21):
    del (patch_name_list[low_byte.index(min(low_byte))])
    del (low_byte[low_byte.index(min(low_byte))])


#   Construct bytes in the correct range
def byte_construct(rnd_num, rnd_low, rnd_high):
    rnd_bytes = []
    with serial.Serial(ser_port, 19200, timeout=1) as ser:
        x = ser.read(rnd_num)
        while True:
            if len(rnd_bytes) == rnd_num:
                break
            replace_bytes = 0
            for valid_byte in range(len(x)):
                if rnd_high >= int(x[valid_byte]) >= rnd_low:
                    rnd_bytes.append(int(x[valid_byte]))
                else:
                    replace_bytes += 1
            x = ser.read(replace_bytes)
        return rnd_bytes


#   Produce OP-specific parameters for the 6 OPs
def op_construct():
    op_bytes = []
    syx1 = byte_construct(13, 0, 99)
    for lvls in range(11):
        op_bytes.append(syx1[lvls])                 # OP EG RATE + LVLS, SCALING BREAK P., SCALING L/R DEPTH
    op_bytes.append(byte_construct(1, 0, 15)[0])    # SCALING R/L CURVE
    op_bytes.append(byte_construct(1, 0, 119)[0])   # OSCILLATOR DETUNE, RATE SCALING
    op_bytes.append(byte_construct(1, 0, 31)[0])    # KEY VELOCITY SENS., AMPLITUDE MOD. SENS.
    op_bytes.append(syx1[11])                       # OUTPUT LEVEL
    op_bytes.append(byte_construct(1, 0, 63)[0])    # FREQUENCY COARSE, OSCILLATOR MODE
    op_bytes.append(syx1[12])                       # FREQUENCY FINE
    return op_bytes


#   Construct a single named DX7 patch for a 32-patch cartridge
def patch_construct():
    one_patch = []
    for ops in range(6):
        current_op = op_construct()
        for op in range(len(current_op)):
            one_patch.append(current_op[op])
    syx1 = byte_construct(12, 0, 99)
    syx2 = byte_construct(3, 97, 122)
    patch_name = byte_construct(16, 0, 255)
    patch_name_count = 0
    for name_sel in range(16):
        patch_name_count += int(patch_name[name_sel])
    patch_name = patch_name_list[patch_name_count]
    print(patch_name)
    for param in range(8):
        one_patch.append(syx1[param])
    one_patch.append(byte_construct(1, 0, 31)[0])
    one_patch.append(byte_construct(1, 0, 15)[0])
    for param in range(8, 12):
        one_patch.append(syx1[param])
    one_patch.append(byte_construct(1, 0, 123)[0])
    one_patch.append(byte_construct(1, 0, 48)[0])
    one_patch.append(syx2[0])
    for name in range(7):
        one_patch.append(ord(patch_name[name]))
    one_patch.append(syx2[1])
    one_patch.append(syx2[2])
    return one_patch


#   Construct a 32-patch cartridge
def cart_construct():
    cart_list = [240,            # Start of System Exclusive
                 67,             # Yamaha Identification
                 0,              # Sub-status and channel
                 9,              # Format number
                 32,             # Byte count MSB
                 0               # Byte count LSB
                 ]
    for cart in range(32):
        patch = patch_construct()
        for patch_bytes in range(len(patch)):
            cart_list.append(patch[patch_bytes])
        print('Patch ' + str(cart + 1) + ' done.')
    checksum_bytes = bytearray(cart_list[6:])
    checksum = ~sum(checksum_bytes) + 1 & 0x7F
    cart_list.append(checksum)   # Checksum
    cart_list.append(247)        # End of System Exclusive
    return cart_list


print('Enter cartridge name: ')
syx_name = str(input()) + '.syx'
sysex = bytearray(cart_construct())
with open(syx_name, 'wb') as f:
    f.write(sysex)

