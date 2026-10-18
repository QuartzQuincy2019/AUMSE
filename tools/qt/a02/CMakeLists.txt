# A02 探针的构建脚本。
# 用 Qt 6.12 的 mingw_64 + Qt 自带的 MinGW 13.1，CMake + Ninja。
# 只为了跑出真实数字，不进项目产物。
cmake_minimum_required(VERSION 3.21)
project(a02_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Gui)

add_executable(a02_probe main.cpp)
target_link_libraries(a02_probe PRIVATE Qt6::Gui)
