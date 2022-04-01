## 为什么做这个

自己经常遇到点标注的工作，目前网上比较好用的就是 [labelme](https://github.com/wkentaro/labelme)，但是它只能生成json格式的标签，想要别的格式只能来回地写转换脚本。
另外还有pprp开源的 [landmark_annotation](https://github.com/pprp/landmark_annotation)，介绍说标签格式转换可以在源码中修改，另外这份代码是基于tkinter实现的，由于自己使用pyqt5更多，所以打算换一个框架来实现自己的版本。

其次，我个人感觉这个软件还有一些功能没有很完善。主要有以下几点：

- **图片不能缩放**，这样对于比较密集的目标点或者比较小的图片就不太友好。虽说可以自定义尺寸，但是只能在导入文件夹时对全体图片设置，如果原图片大小不一致有大有小，也挺麻烦，并且为了拉伸不形变影响美观，宽高需要自己计算。
- 删除关键点时只能单选删除，方法是将鼠标放在右侧坐标点listbox中的某一项上，然后点击删除按钮。不支持多选删除，并且没有 `ctrl+z` 撤回快捷键。
- **没有预览功能**，就是说当鼠标放在右侧坐标点listbox中的某一项时，看不出这个坐标点指的是图片中具体的哪个点，这样就影响了删除功能，因为当关键点很多的时候，我们很难明确的知道图片中想要删除的点究竟是右侧坐标点集合中的第几个（作者的需求是一个图中只有一个关键点，所以没有做这个处理）。这个预览功能在[labelimg](https://github.com/tzutalin/labelImg)软件中是有的，这个软件是用来画矩形框的，感觉很有用，但是在点标注中也能实现并且也很有必要。
- 然后就是自定义标签格式，现在只能去修改源码来实现，比较麻烦。可以做一个下拉列表在前端，使用者可以更方便的选择，并且选择完以后要动态更新当前图片的标注状态。









## 工具介绍

- 整体外观

  ![](https://z3.ax1x.com/2021/08/07/fKmq7n.png)




- 使用方法

  1.  选择标签格式（默认为mat）
  2.  选择输入目录（图标的存放路径）
  3.  选择输出目录（标签的存放路径）
  4.  自动加载输入目录中的图片，开始标注。**如果输出目录中已有标签，就自动加载出这些标签里已经有的关键点到图片中。**

  

- 快捷操作

  - `A`：上一张图片
  - `S`：保存当前图片
  - `D`：下一张图片
  - `Ctrl+Z`：撤回上一次标注动作
  - `Esc`：将缩放的图像复原回原本的尺寸

  

  

- 图片缩放

  使用 `鼠标滚轮` 可动态调节图片尺寸。图片放缩后，关键点的物理位置（关键点相对于屏幕的位置）发生改变，但逻辑位置（关键点相对于图片的位置）是恒定的，所以可以大胆的缩放，最后的生成的坐标是正确的。



- 预览

  将鼠标放在右侧输出集合中的任意一个坐标点上，就会有一个阴影框覆盖住这个点在图中的位置。如果多选，就有多个阴影框分别覆盖各自的关键点。



- 删除与保存
  - 单个删除：预览确定目标后，`鼠标双击` 即可删除想要删除的坐标点（左右键均可）
  - 多选删除：在右侧鼠标搭配Ctrl键选中想要删除的关键点，图像上会预览这多个点，确定误会后按 `Del键` 完成批量删除
  - 保存：按S键保存；按A、D键或者点击相应按钮切换到上一张下一张也会自动保存





- 自定义标签

  目前支持的有mat、json、h5、txt（默认是mat）。

  - 其中mat和h5将坐标点存放在`annPoints`的键名下。
  - txt的格式是每行一个坐标点，横坐标和纵坐标用英文逗号隔开
  - json的格式与labelme生成的json文件格式完全一致（标签文件内已经包含图片的base64编码）







录了一个视频来展示一操作的效果：https://www.bilibili.com/video/BV17o4y1D7d4/



**代码注释非常详细，过程不易，给个star~**

