

from PyQt5.uic import loadUi
import sys
from PyQt5.QtGui import QIcon,QPixmap,QPainter,QPen,QColor,QBrush
from PyQt5.QtCore import Qt,QPoint
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QAbstractItemView,QVBoxLayout,QMessageBox,QInputDialog,QFileDialog,QMainWindow
import os
import scipy.io as sio
from scipy.io import loadmat
import json
import base64
import h5py

from Frame import Ui_MainWindow

# 用python代码模拟键盘输入。原本想解决的问题是QListWidget会使键盘监听失败，按一下Alt键会恢复监听。这里的作用就是模拟键盘按下Alt键   https://cloud.tencent.com/developer/article/1566445
# import win32api  
# import win32con
# win32api.keybd_event(18,0,0,0)  # Alt的键号是18
# win32api.keybd_event(18,0,win32con.KEYEVENTF_KEYUP,0)


class MyMainForm(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MyMainForm,self).__init__()
        self.setupUi(self)
        #loadUi("./ui.ui", self)  #加载UI文件到self

        

        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle('关键点标注工具')

        
        # 获取电脑屏幕的尺寸
        desktop_height = QApplication.desktop().screenGeometry().height()
        desktop_width = QApplication.desktop().screenGeometry().width()

        # self.setFixedSize(desktop_width, desktop_height )   # 固定大小
        # self.setStyleSheet('background-color:#2C3E50;')    # 背景颜色填充
        self.layout_width = desktop_width-220
        self.layout_height = desktop_height-80


        # 坑：如果是建立的界面是QWidget类的，就只需要加下面的第三句，就可以实现鼠标不按下也能跟随 ； 如果是建立的界面是QMainWindow类的，只用第三句没有效果，需要用下面的三条语句在一块才可以
        # setCentralWidget是函数，centralwidget可以在ui文件里找到。     
        # https://www.codeleading.com/article/20072274463/
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setMouseTracking(True)
        self.setMouseTracking(True)   

          


        # 坑：当Qt的控件QListWidget或QTableView嵌入到主窗口之后，他本身也会接受按键事件，所以获得焦点时，按键点击并不会触发主窗口的keyPressEvent()函数，也就是说监听冲突了    #
        # 解决方法就是添加下面这一句，让其不处理按键事件。也可以在qtdesigner中设置，选中这个这个控件后，右侧的属性编辑器里面有一项是focusPolicy，选择NoFocus即可    
        # https://blog.csdn.net/u010189457/article/details/53149805
        self.listWidget.setFocusPolicy(Qt.NoFocus)   


        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 设置之后可以通过【Ctrl+鼠标】左键实现QListWidget的多选
        self.listWidget.clicked.connect(self.Preview)       # clicked:当双击某项时，信号被发射
        self.listWidget.doubleClicked.connect(self.Delete)  # doubleClicked:当双击某项时，信号被发射


        # 三个按钮的触发函数
        self.format.clicked.connect(self.get_format)
        self.format.setToolTip('<b>json</b>：生成的格式同labelme<hr>     <b>txt </b>：每行的坐标用逗号隔开')   # 鼠标停留时显示提示性文字
        self.input.clicked.connect(self.open_input_dir)
        self.output.clicked.connect(self.open_output_dir)

        # 关于页码的触发函数
        self.Prev.clicked.connect(self.prevImage)
        self.Next.clicked.connect(self.nextImage)
        self.go.clicked.connect(self.gotoImage)


        # 菜单栏的触发函数
        self.actioninstructions.triggered.connect(self.instructions)   # 这里用triggered，而不是clicked   详情：https://www.cnblogs.com/unixcs/p/14272631.html
        self.actionabout.triggered.connect(self.about)
        


        self.pos_xy=[]
        self.preview_flag=False
        self.img = None
        self.labelpath = ''
        self.imagepath = ''
        self.imageDir = ''
        self.outDir = ''
        self.cur = 0
        self.total=0
        self.label_format = 'mat'

        


    def instructions(self):
        QMessageBox.information(self,"Infomation","1. 选择标签格式（默认为mat）\n2. 选择图片的输入目录\n3. 选择标签的输出目录")
    def about(self):
        QMessageBox.information(self,"Infomation","作者:hsy 版权所有 请勿商业使用")


    def img_resize(self):
        if self.img.width()< self.layout_width and self.img.height()< self.layout_height: 
            self.img_width = self.img.width()
            self.img_height = self.img.height()
            self.ori_scale = 1
           
        elif self.img.width()< self.layout_width and self.img.height()>= self.layout_height: 
            self.ori_scale = (self.layout_height)/self.img.height()
            self.img_width = int(self.img.width()*self.ori_scale)
            self.img_height = self.layout_height
           
            
        elif self.img.width()>= self.layout_width and self.img.height()<self.layout_height: 
            self.ori_scale = (self.layout_width)/self.img.width()
            self.img_width = self.layout_width
            self.img_height = int(self.img.height()*self.ori_scale)
        else:
            x_ = self.img.width()- (self.layout_width)
            y_ = self.img.height()-(self.layout_height)
            if x_<y_:
                self.ori_scale = (self.layout_height)/self.img.height()
                self.img_width = int(self.img.width()*self.ori_scale)
                self.img_height = self.layout_height
            else:
                self.ori_scale = (self.layout_width)/self.img.width()
                self.img_width = self.layout_width
                self.img_height = int(self.img.height()*self.ori_scale)
        self.x_y_scale = self.img_width/self.img_height
        self.scaled_img = self.img.scaled(self.img_width, self.img_height)
        self.img = self.scaled_img
      
        self.ratio=1
  

    def open_input_dir(self):
        self.imageDir = QFileDialog.getExistingDirectory(self,'Please select a folder','./')
    
        if self.imageDir == '':
            QMessageBox.information(self,"Tips","Please select a folder",QMessageBox.Yes)
            return
      

        self.imageList = os.listdir(self.imageDir)
        self.imageList = [ f for f in self.imageList if f.endswith(('.jpg','.png','bmp','jpeg'))]  #得到文件夹下指定后缀的所有文件路径
        self.imageList.sort()

        if len(self.imageList) == 0:
            QMessageBox.information(self,"Tips","There are no picture files in this directory",QMessageBox.Yes)
            return
        self.cur = 0
        self.total = len(self.imageList)


    def open_output_dir(self):
        self.outDir = QFileDialog.getExistingDirectory(self,'Please select a folder','./')
        if self.outDir == '':
            QMessageBox.information(self,"Tips","Please select a folder",QMessageBox.Yes)
            return
      
        self.Load()

    def get_format(self): 
        items=('mat', 'json', 'h5', 'txt')
        item, ok=QInputDialog.getItem(self, "Select label format", 'Format List', items, 0, False)
        if ok and item:
            self.label_format = item
            if  self.imageDir != '' and  self.outDir != '':
                self.Load()

   

    def Load(self):
        # 判断（防止只选择输出文件夹不选择输入文件夹）
        if self.imageDir == '':
            QMessageBox.information(self,"Tips","Please select an input folder",QMessageBox.Yes)
            return
        if self.outDir == '':
            QMessageBox.information(self,"Tips","Please select an output folder",QMessageBox.Yes)
            return
        
        # 预处理
        self.pos_xy=[]
        self.listWidget.clear()
        self.page.setAlignment(Qt.AlignCenter)
        self.page.setText("%03d/%03d" % (self.cur+1, self.total))
        self.imgName.setAlignment(Qt.AlignCenter)
        self.imgName.setText(self.imageList[self.cur])


        # 加载图片
        self.imagepath = self.imageDir +'/'+ self.imageList[self.cur ]
        #print(self.imagepath)
        self.img = QPixmap(self.imagepath)
        


        # 加载标签
        self.labelpath = self.outDir +'/'+ self.imageList[self.cur ].split('.')[0]+'.'+self.label_format
        if os.path.exists(self.labelpath):
            if self.label_format=='txt':   # txt的读取方式和其他有点不一样，先单拿出来
                txt = open(self.labelpath)
                for line in txt:
                    x,y = line.strip().split(',')  # strip()去除回车键
                    x = float(x)
                    y = float(y)
                    if 0<=x<=self.img.width() and 0<=y<=self.img.height():   # 过滤一下标注文件中越界的点
                        self.pos_xy.append((x,y))      # 保存的时候用真实的位置，不四舍五入
                        self.listWidget.insertItem(len(self.listWidget), '('+str(round(x,2))+','+str(round(y,2))+')')
            else:
                if self.label_format=='mat':
                    mat = loadmat(self.labelpath)
                    points = mat['annPoints']
                elif self.label_format=='h5':
                    h5 = h5py.File(self.labelpath,'r')  
                    points = h5['annPoints'] 
                elif self.label_format=='json':
                    f = open(self.labelpath, 'r')
                    content = f.read()
                    content = json.loads(content)
                    content  = content['shapes']
                    points = []
                    for p in content:
                        if p['points']!=[]:
                            points.append(p['points'][0])
                   
                for point in points:
                    x,y=point
                    if 0<=x<=self.img.width() and 0<=y<=self.img.height():   # 过滤一下标注文件中越界的点
                        self.pos_xy.append((x,y))      # 保存的时候用真实的位置，不四舍五入
                        self.listWidget.insertItem(len(self.listWidget), '('+str(round(x,2))+','+str(round(y,2))+')')
            

                        
        self.img_resize()  # 最后再resize，因为加载标签的时候用到了图的尺寸来过滤一部分越界的标注点
        self.update()




    def prevImage(self, event=None):
        success = self.Save()
        if success:
            if self.cur > 0:
                self.cur -= 1
                self.Load()
            else:
                QMessageBox.information(self,"Tips","TThe current is the first picture!",QMessageBox.Yes)
                return
       


            
    def nextImage(self, event=None):
        success = self.Save()
        if success:
            if self.cur < self.total-1:
                self.cur += 1
                self.Load()
            else:
                QMessageBox.information(self,"Tips","The current is the last picture!",QMessageBox.Yes)
                return



    def Save(self):
        if self.imageDir == '':
            QMessageBox.information(self,"Tips","Please select an input folder",QMessageBox.Yes)
            return False
        if self.outDir == '':
            QMessageBox.information(self,"Tips","Please select an output folder",QMessageBox.Yes)
            return False

        if self.label_format=='mat':
            sio.savemat(self.labelpath , {'annPoints':self.pos_xy,'num':len(self.pos_xy)})
        elif self.label_format=='h5':
            h5 = h5py.File(self.labelpath,'w')
            h5['annPoints'] = self.pos_xy
            h5['num'] = len(self.pos_xy)
        elif self.label_format=='json':
            pic = open(self.imagepath, 'rb')  # 以二进制读取图片
            data = pic.read()
            encodestr = base64.b64encode(data) # 得到 byte 编码的数据
            encodestr = str(encodestr,'utf-8')
           
            Dict = {}
            Dict['version']='4.5.7'
            Dict['flags']={}
            Dict['shapes']=[]
            Dict['imagePath']=self.imagepath
            Dict['imageData']=encodestr
            Dict['imageHeight']=int(self.img.height()/self.ori_scale)
            Dict['imageWidth']=int(self.img.width()/self.ori_scale)
            for xy in self.pos_xy:
                Dict['shapes'].append({
                    'label':'annPoints',
                    'points':[xy],
                    'group_id':None,
                    'shape_type':'point',
                    'flags':{}
                })
            f = open(self.labelpath, 'w') 
            json.dump(Dict,f,indent=2)
        elif self.label_format=='txt':
            txt = open(self.labelpath,"w")                                                
            for point in self.pos_xy:                      
                txt.write(str(point[0])+','+str(point[1])+'\n') 

        print('第 %d 张图片已保存' % (self.cur+1))
        return True


    def gotoImage(self):
        idx = self.jump.text()
        if idx=='':
            QMessageBox.information(self,"Tips","Value cannot be empty",QMessageBox.Yes)
            self.jump.clear()
            return
        idx = int(idx)
        if 1 <= idx and idx <= self.total:
            success = self.Save()
            if success:
                self.cur = idx-1
                self.Load()
        else:
            QMessageBox.information(self,"Tips","Invalid index value",QMessageBox.Yes)
            self.jump.clear()
            return


    def paintEvent(self, event):
        if self.img == None:
            return
        p1 = QPainter()
        p1.begin(self)
     
        p1.drawPixmap(QPoint(0, 0), self.scaled_img)
        p1.setPen(QPen(QColor(255,0,255), 5*self.ratio))
        for pos_tmp in self.pos_xy:
            p1.drawPoint(int(pos_tmp[0]*self.ratio*self.ori_scale) ,int(pos_tmp[1]*self.ratio*self.ori_scale))
        p1.end()


        if self.preview_flag:
            p2 = QPainter()
            p2.begin(self)
            
            p2.setBrush(QBrush(QColor(0, 128, 128,200),1))   # QColor里前三位是rgb值，第四位是透明度，越小越透明
            indexs = [x.row() for x in self.listWidget.selectedIndexes()]
            for idx in indexs:
                x = int((self.pos_xy[idx][0]-15)*self.ratio*self.ori_scale)
                y = int((self.pos_xy[idx][1]-15)*self.ratio*self.ori_scale)
                w = int(30*self.ratio*self.ori_scale)
                h = w
                p2.drawRect(x,y,w,h)
            p2.end()
            self.preview_flag=False








    def Preview(self, item):
        self.preview_flag=True
        self.update()





    def Delete(self):
        indexs = [x.row() for x in self.listWidget.selectedIndexes()]
        indexs.sort()  # 这个拍虚很关键
        if len(indexs)>0:
            for i in range(len(indexs)):
                self.pos_xy.pop(indexs[i]-i)
                self.listWidget.takeItem(indexs[i]-i)
            self.update()
   

 
   # 键盘点击事件
    def keyPressEvent(self, event):
        # 监听Esc键
        if event.key() == Qt.Key_Escape:
            self.scaled_img = self.img
            self.img_width = self.img.width()
            self.img_height = self.img.height()
            self.ratio = 1
            self.update()

        # 监听Delete键
        if event.key() == Qt.Key_Delete:
            self.Delete()
        # 监听D键
        if event.key() == Qt.Key_D:
            self.nextImage()
        # 监听A键
        if event.key() == Qt.Key_A:
            self.prevImage()
        # 监听S键
        if event.key() == Qt.Key_S:
            success = self.Save()

        # 监听Ctrl+Z键   https://www.pythonf.cn/read/93347
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Z:  
            if len(self.pos_xy)>1:
                self.pos_xy.pop()
                self.listWidget.takeItem(len(self.pos_xy))
                self.update()
      

    # 鼠标点击时间
    def mousePressEvent(self, event):
        if self.img==None:
            return
        if event.button() == Qt.LeftButton:   # 鼠标左键按下
            if 0<event.x()<self.img_width and 0<event.y()<self.img_height:   # 因为图片被放缩了，如果点击到图片之外的区域，不去处理
                self.listWidget.insertItem(len(self.listWidget), '('+str(round(event.x()/self.ratio/self.ori_scale,2))+','+str(round(event.y()/self.ratio/self.ori_scale,2))+')')
                self.pos_xy.append((event.x()/self.ratio/self.ori_scale, event.y()/self.ratio/self.ori_scale))
                self.update()
            # else:
            #     QMessageBox.information(self,"Tips","Invalid label position",QMessageBox.Yes)
    
    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.img==None:
            return
        new_x = event.x()/self.ratio
        new_y = event.y()/self.ratio
        if new_x<=self.img.width() and  new_y<=self.img.height():
            text = 'x:'+str(round(new_x/self.ori_scale,2))+'    |    y:'+str(round(new_y/self.ori_scale,2))
            self.location.setAlignment(Qt.AlignCenter)
            # self.location.setFont(QFont("微软雅黑",10))
            self.location.setText("<font color=%s>%s</font>" %('#8968CD', text))
        else:
            self.location.setAlignment(Qt.AlignCenter)
            # self.location.setFont(QFont("微软雅黑",10))
            self.location.setText("<font color=%s>%s</font>" %('#8968CD', '--    |   --'))

    # 鼠标滚动
    def wheelEvent(self, event):
        self.preview_flag=True
        if event.angleDelta().y() < 0:  # 下滚,缩小
            if self.img_width>25 and self.img_height>25:
                new_weight = self.img_width-25*self.x_y_scale
                new_height = self.img_height-25
                self.ratio = new_weight/self.img.width()
                self.img_width=new_weight
                self.img_height=new_height
                self.scaled_img = self.img.scaled(self.img_width, self.img_height)   

                self.repaint()
        elif event.angleDelta().y() > 0: # 上滚,放大
            new_weight = self.img_width+25*self.x_y_scale
            new_height = self.img_height+25
            self.ratio = new_weight/self.img.width()
            self.img_width=new_weight
            self.img_height=new_height
            self.scaled_img = self.img.scaled(self.img_width, self.img_height)   
            self.repaint()




if __name__=='__main__':
    app=QApplication(sys.argv)
    w=MyMainForm()
    #w.showFullScreen()
    w.show()
    sys.exit(app.exec_())