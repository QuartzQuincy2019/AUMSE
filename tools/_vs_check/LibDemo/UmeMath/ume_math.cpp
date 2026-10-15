// ume_math.cpp —— 静态库的实现
#include "ume_math.h"

int ume_add(int a, int b) {
    return a + b;
}

int ume_mul(int a, int b) {
    return a * b;
}

int ume_clamp(int v, int lo, int hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}
