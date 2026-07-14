import numpy as np
from bitarray import bitarray

# ====== Your outputs from the challenge ======
outputs = [
    11329270341625800450, 14683377949987450496, 11656037499566818711,
    14613944493490807838, 370532313626579329, 5006729399082841610,
    8072429272270319226, 3035866339305997883, 8753420467487863273,
    15606411394407853524, 5092825474622599933, 6483262783952989294,
    15380511644426948242, 13769333495965053018, 5620127072433438895,
    6809804883045878003, 1965081297255415258, 2519823891124920624,
    8990634037671460127, 3616252826436676639, 1455424466699459058,
    2836976688807481485, 11291016575083277338, 1603466311071935653,
    14629944881049387748, 3844587940332157570, 584252637567556589,
    10739738025866331065, 11650614949586184265, 1828791347803497022,
    9101164617572571488, 16034652114565169975, 13629596693592688618,
    17837636002790364294, 10619900844581377650, 15079130325914713229,
    5515526762186744782, 1211604266555550739, 11543408140362566331,
    18425294270126030355, 2629175584127737886, 6074824578506719227,
    6900475985494339491, 3263181255912585281, 12421969688110544830,
    10785482337735433711, 10286647144557317983, 15284226677373655118,
    9365502412429803694, 4248763523766770934, 13642948918986007294,
    3512868807899248227, 14810275182048896102, 1674341743043240380,
    28462467602860499, 1060872896572731679, 13208674648176077254,
    14702937631401007104, 5386638277617718038, 8935128661284199759
]

SIZE = 32  # PRNG state size
BITS = SIZE * 64  # 2048 bits

# ====== Helper functions ======
def int_to_bits(n):
    b = bitarray(endian='big')
    b.frombytes(n.to_bytes(8, 'big'))
    return b

def rotl64(x, r):
    return ((x << r) | (x >> (64 - r))) & 0xFFFFFFFFFFFFFFFF

def rotr64(x, r):
    return ((x >> r) | (x << (64 - r))) & 0xFFFFFFFFFFFFFFFF

# ====== Convert outputs to bitarray ======
output_bits = bitarray(endian='big')
for o in outputs:
    output_bits.extend(int_to_bits(o))

# ====== Build linear system ======
# Each initial state bit corresponds to a column
# Each output bit corresponds to a row
# We'll simulate each initial bit individually to fill matrix
matrix = np.zeros((len(output_bits), BITS), dtype=np.uint8)

print("[*] Building linear system, this may take ~1-2 minutes...")

for bit_idx in range(BITS):
    # Start with all-zero state
    state_words = [0]*SIZE
    # Set only current bit
    word_idx = bit_idx // 64
    bit_in_word = 63 - (bit_idx % 64)
    state_words[word_idx] = 1 << bit_in_word
    
    # Simulate PRNG for the number of outputs we have
    current_state = state_words.copy()
    bit_output = bitarray(endian='big')
    
    for _ in outputs:
        # Compute next value
        taps = [0, 1, 3, 7, 13, 22, 28, 31]
        new_val = 0
        for i in taps:
            val = current_state[i]
            mixed = val ^ ((val << 11) & 0xFFFFFFFFFFFFFFFF) ^ (val >> 7)
            rot = (i*3) % 64
            mixed = rotl64(mixed, rot)
            new_val ^= mixed
        new_val ^= ((current_state[-1] << 5) & 0xFFFFFFFFFFFFFFFF) ^ (current_state[-1] >> 13)
        new_val &= 0xFFFFFFFFFFFFFFFF
        current_state = current_state[1:] + [new_val]
        
        # Compute output
        out = 0
        for i, w in enumerate(current_state):
            if i % 2 == 0:
                out ^= w
            else:
                out ^= rotr64(w, 2)
        # Add bits to bit_output
        b = int_to_bits(out)
        bit_output.extend(b)
    
    # Fill matrix column
    matrix[:, bit_idx] = np.array(bit_output.tolist(), dtype=np.uint8)

print("[*] Solving linear system mod 2...")

# Gaussian elimination mod 2
def gaussian_elim_mod2(A, b):
    A = A.copy()
    b = b.copy()
    n_rows, n_cols = A.shape
    row = 0
    for col in range(n_cols):
        pivot = None
        for r in range(row, n_rows):
            if A[r, col]:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
            b[[row, pivot]] = b[[pivot, row]]
        for r in range(n_rows):
            if r != row and A[r, col]:
                A[r] ^= A[row]
                b[r] ^= b[row]
        row += 1
    x = np.zeros(n_cols, dtype=np.uint8)
    for r in range(row):
        first_one = np.where(A[r])[0][0]
        x[first_one] = b[r]
    return x

b_vec = np.array(output_bits.tolist(), dtype=np.uint8)
solution_bits = gaussian_elim_mod2(matrix, b_vec)

# Convert solution bits back to bytes -> flag
flag_bits = bitarray(endian='big')
flag_bits.extend(solution_bits.tolist())
flag_bytes = flag_bits.tobytes()
flag = flag_bytes.rstrip(b'\x00').decode(errors='ignore')
print("[+] Recovered flag:", flag)
