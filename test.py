class TriangleArea:
    def __init__(self, *args):
        self.B = 0
        self.H = 0
        self.a = 0
        self.b = 0
        self.c = 0
        if len(args) == 2:
            self.B = args[0]
            self.H = args[1]
        elif len(args) == 3:
            self.a = args[0]
            self.b = args[1]
            self.c = args[2]

    def getArea(self):
        # Pythagorean: ans = 0.5 * B * H, print 2*ans = B*H
        print(self.B * self.H)
        # Heron's: ans = sqrt(s(s-a)(s-b)(s-c)), print ans*ans = s(s-a)(s-b)(s-c)
        s = (self.a + self.b + self.c) // 2
        print(s * (s - self.a) * (s - self.b) * (s - self.c))

if __name__ == '__main__':
    H = int(input())
    B = int(input())
    a = int(input())
    b = int(input())
    c = int(input())
    t = TriangleArea(B, H)
    t.a, t.b, t.c = a, b, c
    t.getArea()
