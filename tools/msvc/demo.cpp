// 最小演示：三种导出，看导出表里名字长什么样
//
// 编译：cl /LD /nologo /EHsc /utf-8 demo.cpp
// 查看：dumpbin /exports demo.dll
//
// 预期（导出表里）：
//   PlainAdd         —— extern "C"，**不被修饰**，原样就是 PlainAdd
//   ?CppFunc@@YAHHH@Z —— C++ 重载，返回 int，参数 (int,int)
//   ?CppFunc@@YANNN@Z —— C++ 重载，返回 double，参数 (double,double)
//
// 注意：没有 __declspec(dllexport) 就没有导出，
//       dumpbin 只会打出 Summary，一个名字都没有，而且不报错。

extern "C" __declspec(dllexport)
int PlainAdd(int a, int b) { return a + b; }

__declspec(dllexport) int    CppFunc(int a, int b)       { return a + b; }
__declspec(dllexport) double CppFunc(double a, double b) { return a + b; }
