import re

def compressed_fen(fen):
    """ From: 11111q1k/1111r111/111p1pQP/111P1P11/11prn1R1/11111111/111111P1/R11111K1
        To: 5q1k/4r3/3p1pQP/3P1P2/2prn1R1/8/6P1/R5K1
    """
    for length in reversed(range(2,9)):
        fen = fen.replace(length * '1', str(length))
    return fen

def uncompressed_fen(fen):
    for digit in re.findall(r'[2-8]', fen):
        fen = fen.replace(digit, int(digit) * '1')
    return fen
