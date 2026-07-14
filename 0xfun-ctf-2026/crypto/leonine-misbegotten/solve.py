from base64 import b16decode, b32decode, b64decode, b85decode
from hashlib import sha1

# Load the output
with open("output", "rb") as f:
    data = f.read()

# List of decoders
DECODERS = [b16decode, b32decode, b64decode, b85decode]

ROUNDS = 16
CHECKSUM_LEN = 20  # SHA1 produces 20 bytes

def reverse_round(encoded_with_checksum):
    """
    Attempt to reverse one round by checking all 4 decoders.
    Returns a list of possible previous states.
    """
    candidates = []
    # Last 20 bytes are checksum
    if len(encoded_with_checksum) < CHECKSUM_LEN:
        return []

    encoded = encoded_with_checksum[:-CHECKSUM_LEN]
    checksum = encoded_with_checksum[-CHECKSUM_LEN:]

    for decoder in DECODERS:
        try:
            decoded = decoder(encoded)
            if sha1(decoded).digest() == checksum:
                candidates.append(decoded)
        except Exception:
            continue

    return candidates

# We'll use a simple iterative approach
candidates = [data]

for round_num in range(ROUNDS):
    next_candidates = []
    print(f"Reversing round {ROUNDS - round_num}... possible candidates: {len(candidates)}")
    for c in candidates:
        reversed_round = reverse_round(c)
        next_candidates.extend(reversed_round)
    candidates = next_candidates
    if not candidates:
        print("No candidates found, something went wrong!")
        break

# After 16 rounds, candidates should contain the original flag
for i, flag_candidate in enumerate(candidates):
    try:
        print(f"Candidate {i+1}: {flag_candidate.decode()}")
    except Exception:
        print(f"Candidate {i+1}: (binary data, cannot decode)")
