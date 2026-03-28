    #include <iostream>
#include <cmath>
using namespace std;

class TriangleArea {
public:
    int B, H, a, b, c;

    TriangleArea(int B, int H) {
        this->B = B;
        this->H = H;
        a = b = c = 0;
    }

    TriangleArea(int a, int b, int c) {
        this->a = a;
        this->b = b;
        this->c = c;
        B = H = 0;
    }

    void getArea() {
        // pythagorean - ans is 0.5*B*H, but we print 2*ans so its just B*H
        cout << B * H << endl;

        // herons - ans is sqrt(s(s-a)(s-b)(s-c)), we print ans*ans so skip the sqrt
        int s = (a + b + c) / 2;
        cout << s * (s - a) * (s - b) * (s - c) << endl;
    }
};

int main() {
    int H, B, a, b, c;
    cin >> H >> B >> a >> b >> c;

    TriangleArea t1(B, H);
    t1.a = a;
    t1.b = b;
    t1.c = c;
    t1.getArea();

    return 0;
}
