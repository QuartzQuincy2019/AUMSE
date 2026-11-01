#pragma once

#include <QCursor>
#include <QIcon>

/* 工具栏图标：没有图标资源，全部用 QPainter 现画，
   这样缩放、深浅色都不会糊。 */
namespace UmeIcons {

QIcon bold();
QIcon italic();
QIcon underline();
QIcon strikeOut();
QIcon superscript();
QIcon subscript();
QIcon fontFamily();
QIcon flipHorizontal();
QIcon flipVertical();

/* 旋转手柄用的光标（Qt 没有内置旋转光标，现画一个） */
QCursor rotateCursor();

/* 竖排正文的鼠标光标：横着的 I 形。Qt 只有竖的 IBeam，直排里方向是错的。 */
QCursor textIBeam();

} // namespace UmeIcons
