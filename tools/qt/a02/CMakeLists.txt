# A02 探针的构建脚本。
# 用 Qt 6.12 的 mingw_64 + Qt 自带的 MinGW 13.1，CMake + Ninja。
# 另外链接本机自建的 HarfBuzz 14.6.0（D:/libs/harfbuzz-mingw），
# 用来实测「路线 B：自己调 HB」与「路线 A：QTextLayout」的差别。
cmake_minimum_required(VERSION 3.21)
project(a02_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Gui)

# 本机自建的 HarfBuzz（静态库）。要换机器就改这一行。
set(HB_ROOT "D:/libs/harfbuzz-mingw")

add_executable(a02_probe main.cpp)
target_link_libraries(a02_probe PRIVATE Qt6::Gui)

if(EXISTS "${HB_ROOT}/lib/libharfbuzz.a")
  target_include_directories(a02_probe PRIVATE "${HB_ROOT}/include/harfbuzz")
  target_link_directories(a02_probe PRIVATE "${HB_ROOT}/lib")
  target_link_libraries(a02_probe PRIVATE harfbuzz)
  target_compile_definitions(a02_probe PRIVATE HAVE_HARFBUZZ=1)
  message(STATUS "HarfBuzz: ${HB_ROOT}（路线 B 可用）")
else()
  message(STATUS "HarfBuzz: 未找到 ${HB_ROOT}/lib/libharfbuzz.a（路线 B 跳过）")
endif()
