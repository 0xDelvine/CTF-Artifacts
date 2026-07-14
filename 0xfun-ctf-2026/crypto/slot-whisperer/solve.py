M = 2147483647
A = 48271
C = 12345

outputs = [11, 17, 56, 21, 10, 81, 41, 38, 54, 13]

def next_state(state):
    return (A * state + C) % M

# brute force possible first state
for k in range(M // 100 + 1):
    state = 100 * k + outputs[0]
    valid = True
    
    test_state = state
    
    for i in range(1, len(outputs)):
        test_state = next_state(test_state)
        if test_state % 100 != outputs[i]:
            valid = False
            break
    
    if valid:
        print("Found state:", state)
        
        # advance to after last known output
        final_state = test_state
        
        # predict next 5
        predictions = []
        for _ in range(5):
            final_state = next_state(final_state)
            predictions.append(final_state % 100)
        
        print("Next 5 spins:", predictions)
        break
