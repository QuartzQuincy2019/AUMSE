# UME 编辑器（Qt / QWidget）
#
# 工具链与 tools/qt/a02 一致：Qt 6.12.0 mingw_64 + Qt 自带 MinGW 13.1 + Ninja。
#   cmake -S app -B app/build -G Ninja ^
#     -DCMAKE_BUILD_TYPE=Release ^
#     -DCMAKE_PREFIX_PATH=D:/Qt/6.12.0/mingw_64 ^
#     -DCMAKE_CXX_COMPILER=D:/Qt/Tools/mingw1310_64/bin/g++.exe ^
#     -DCMAKE_MAKE_PROGRAM=D:/Qt/Tools/Ninja/ninja.exe
#   ninja -C app/build
cmake_minimum_required(VERSION 3.21)
project(ume_editor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets)

# 内置字体所在目录（仓库里的 font/），运行时拼出绝对路径
get_filename_component(UME_FONT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../font" ABSOLUTE)

add_executable(ume
    src/main.cpp
    src/mainwindow.cpp
    src/umelayoutbar.cpp
    src/umeformatbar.cpp
    src/umeformat.h
    src/umeview.cpp
    src/umelayout.cpp
    src/umesettings.h
)

target_link_libraries(ume PRIVATE Qt6::Widgets)
target_compile_definitions(ume PRIVATE UME_FONT_DIR="${UME_FONT_DIR}")

if(WIN32)
    set_target_properties(ume PROPERTIES WIN32_EXECUTABLE FALSE)
endif()
