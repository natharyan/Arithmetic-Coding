from math import log2
import numpy as np
import random

class ArithmeticCoder:
    def __init__(self, symbols, probabilities):
        self.symbols = symbols
        self.probabilities = probabilities

        if abs(sum(probabilities) - 1.0) > 1e-10:
            raise ValueError("Probabilities must sum to 1")
        self.max_bits = 40
        self.cdf = [0.0]
        cumulative = 0.0
        for p in probabilities:
            cumulative += p
            self.cdf.append(cumulative)
        self.probs_dict = {symbols[i]: probabilities[i] for i in range(len(symbols))}
        self.cdf_dict = {}
        cumulative_sum = 0
        for s in symbols:
            idx = symbols.index(s)
            cumulative_sum += probabilities[idx]
            self.cdf_dict[s] = cumulative_sum
    

    def encode(self,message, symbols):
        L, U = 0.0, 1.0
        encoding = []
        #e3_count = 0
        print(f"Original Interval: [{L}, {U})")
        input()
        for i,s in enumerate(message):
            if len(encoding) == 0:
                print("Encoding first symbol")
            else:
                print("Current encoding:",''.join(encoding))
            print("Current symbol:", s)
            diff_UL = U - L
            lower_cdf = (self.cdf_dict[s] - self.probs_dict[s])
            upper_cdf = (self.cdf_dict[s])

            print(f"L_({i+1}) = {L} + ({U} - {L})*{lower_cdf}")
            print(f"U_({i+1}) = {L} + ({U} - {L})*{upper_cdf}")
            U = L + diff_UL * upper_cdf
            L = L + diff_UL * lower_cdf
            print(f"Updated Interval: [{L}, {U})")
            input()
            while True:
                if U <= 0.5:
                    print("\nE1 Scaling")
                    print(f"L_({i+1}) = 2*{L}")
                    print(f"U_({i+1}) = 2*{U}")
                    L, U = 2 * L, 2 * U
                    print("Adding 0 to the encoding")
                    encoding.append("0")
                    print("Current encoding:", ''.join(encoding))
                    # if e3_count > 0:
                    #    encoding.append("1" * e3_count)
                    #    e3_count = 0
                    print(f"Scaled Interval: [{L}, {U})")
                    # print("Tag:",self.get_tag(encoding))
                    input()
                elif L >= 0.5:
                    print("\nE2 Scaling")
                    print(f"L_({i+1}) = 2*({L} - 0.5)")
                    print(f"U_({i+1}) = 2*({U} - 0.5)")
                    print("Adding 1 to the encoding")
                    encoding.append("1")
                    print("Current encoding:", ''.join(encoding))
                    L, U = 2 * (L - 0.5), 2 * (U - 0.5)
                    # if e3_count > 0:
                    #    encoding.append("0" * e3_count)
                    #    e3_count = 0
                # elif (L >= 0.25 and U < 0.75):
                #     L, U = 2 * (L - 0.25), 2 * (U - 0.25)
                #     e3_count += 1
                    print(f"Scaled Interval: [{L}, {U})")
                    # print("Tag:",self.get_tag(encoding))
                    input()
                else:
                    break
            print("Current Tag:",self.get_tag(encoding))
            input()
        print("Generated tag:", self.get_tag(encoding))
        input()
        encoding = ''.join(encoding)
        return encoding
    
    def get_tag(self,bits):
        tag = 0.0
        power = 1/2
        for i in bits:
            if i == '1':
                tag += power
            power *= 1/2
        return tag  
    def decode(self,message_encoding, word_length=40, message_len=0):

        L = 0.0
        U = 1
        tag_bit = message_encoding[0: word_length]
        tag = self.get_tag(tag_bit)
        bit_index = 0
        decoded = []
        print(f"Original Interval: [{L}, {U})")
        # continue decoding until the message length is reached
        i = 0
        print("Word length:",word_length)
        if word_length > len(message_encoding):
            print(f"Padding tag with {word_length - len(message_encoding)} 0s on the right")
            print("Orignal tag encoding:", tag_bit)
            tag_bit = tag_bit.ljust(word_length, '0')
            print("Padded:", tag_bit)

        while len(decoded) < message_len:
            diff_UL = U - L
            # find the symbol such that the tag is contained the updated interval
            print("\nCurrent tag:", tag)
            for s, cdf_s in self.cdf_dict.items():
                lower_cdf = cdf_s - self.probs_dict[s]
                upper_cdf = cdf_s
                if L + diff_UL * lower_cdf <= tag < L + diff_UL * upper_cdf:
                    decoded.append(s)
                    print(f"L_({i+1}) = {L} + ({U} - {L})*{lower_cdf}")
                    print(f"U_({i+1}) = {L} + ({U} - {L})*{upper_cdf}")
                    U = L + diff_UL * upper_cdf
                    L = L + diff_UL * lower_cdf

                    if len(decoded) == 1:
                        print("Decoded first symbol:", s)
                    else:
                        print(f"Decoded symbol: {s}")
                    print(f"Updated Interval: [{L},{U})")
                    break
            print("Current decoded message",decoded)
            while True:
                if U <= 0.5:
                    print("\nE1 Scaling")
                    print(f"L_({i+1}) = 2*{L}")
                    print(f"U_({i+1}) = 2*{U}")
                    L, U = 2 * L, 2 * U
                    bit_index += 1
                    print("Removing MSB from the tag and retaining the word length")
                    tag_bit = message_encoding[bit_index: bit_index + word_length]
                    # pad tag with 0s on the right
                    tag_bit = tag_bit.ljust(word_length, '0')
                    tag = self.get_tag(tag_bit)
                    print("Current tag encoding:", tag_bit)
                    # if e3_count > 0:
                        #  bit_index += e3_count
                        #  e3_count = 0
                        #  tag_bit = encoding[bit_index: bit_index + win_size]
                        #  tag = get_tag(tag_bit)
                    print(f"Scaled Interval: [{L}, {U})")
                    input()
                elif L >= 0.5:
                    print("\nE2 Scaling")
                    print(f"L_({i+1}) = 2*({L} - 0.5)")
                    print(f"U_({i+1}) = 2*({U} - 0.5)")
                    L, U = 2 * (L - 0.5), 2 * (U - 0.5)
                    bit_index += 1
                    print("Removing MSB from the tag and retaining the word length")
                    tag_bit = message_encoding[bit_index: bit_index + word_length]
                    tag_bit = tag_bit.ljust(word_length, '0')
                    tag = self.get_tag(tag_bit)
                    print("Current tag encoding:", tag_bit)
                    # if e3_count > 0:
                        #  bit_index += e3_count
                        #  e3_count = 0
                        #  tag_bit = encoding[bit_index: bit_index + win_size]
                        #  tag = get_tag(tag_bit)
                    print(f"Scaled Interval: [{L}, {U})")
                    input()
                # elif L >= 0.25 and U < 0.75:
                #     L, U = 2 * (L - 0.25), 2 * (U - 0.25)
                #     e3_count += 1
                else:
                    break
            i+=1
            input()
        return decoded
    
    def bits_required(self, f):
            if f == 0.0:
                return 1
            res = np.binary_repr(np.float64(f).view(np.int64), width=64)
            res = res.rstrip("0")
            print("interval limit in binary:", res)
            return len(res) - 1

if __name__ == "__main__":
    symbols = [1, 2, 3, 4, 5]
    probabilities = [1/2, 1/4, 1/8, 1/16, 1/16]

    coder = ArithmeticCoder(symbols, probabilities)
    print("Source:")
    print("Symbols:", coder.symbols)
    print("Probabilities:", coder.probs_dict)
    print("\nCumulative distribution function:", coder.cdf_dict)
    input()
    for i in range(1):
        test_messages = [
            random.choices(symbols, weights=probabilities, k=length)
            # for length in [10, 100, 1000, 10000, 100000]
            for length in [15]
        ]
        # test_messages = [[3, 1, 4, 3]]
        # test_messages = [[1, 4, 3, 1, 5, 1, 1, 1, 3, 1]]
        for message in test_messages:
            print("\nMessage generated by the source:", message)
            print(f"Message length: {len(message)}")
            input()
            print("Encoding message...")
            encoded = coder.encode(message, symbols)
            print("\n\nEncoded message:", encoded)
            input()
            print("\n\nDecoding message...")
            decoded = coder.decode(encoded, word_length=40, message_len=len(message))
            print("Decoded message:", decoded)
            print("Original message:", message)
            if message != decoded:
                print("Original message:", message)
                print("Decoded message:", decoded)
            assert message == decoded, "Decoding failed"
            print("\nEncoding and decoding successful!\n")
            
            # original_bits = len(message) * 3
            # compressed_bits = len(encoded)
            print(f"Avg bits per symbol from arithmetic coding: {len(encoded)/len(message)}")
            print("Source Entropy:", sum([-p * log2(p) for p in probabilities]))
            # print percentage of the entropy that is achieved
            print("Percentage difference:", (len(encoded)/len(message) - sum([-p * log2(p) for p in probabilities])) / (sum([-p * log2(p) for p in probabilities]))*100)