from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, \
    QVBoxLayout, QLabel, QApplication, QPushButton, \
    QMessageBox, QPlainTextEdit, QGroupBox, QFormLayout, QLineEdit
import os
import sys
from matplotlib.backends.backend_agg import FigureCanvasAgg
import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import simmm as project
import numpy as np
import matplotlib.pyplot as plt

        
class canvas(FigureCanvas):
    def __init__(self, parent, list_of_numbers):
        fig, self.ax = plt.subplots(figsize=(4, 3.5), dpi=200)
        super().__init__(fig)
        self.setParent(parent)
        self.cus_each_day = list_of_numbers
        self.ax.plot(range(1, len(self.cus_each_day) + 1), self.cus_each_day)
        self.ax.set(xlabel='Days', ylabel='Count of customers',
               title='# of customers per day')
        self.ax.grid()

class image_view(QWidget):
    def __init__(self, list_of_numbers):
        super().__init__()
        self.setWindowTitle('Chart')
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), 'icon.png')))
        chart = canvas(self, list_of_numbers)
        self.setMaximumSize(chart.width(), chart.height())
        self.setMinimumSize(chart.width(), chart.height())

class canvas2(FigureCanvas):
    def __init__(self, parent, *waiters):
        fig, self.ax = plt.subplots()
        super().__init__(fig)
        self.setParent(parent)
        ind = np.arange(len(waiters[0][0])) 
        width = 0.5
        print("canvas 2 started")
        # colors = ['r', 'g', 'b']
        # counter = 0
        # for waaiter in waiters:
        #     self.ax.bar(ind+width, waaiter, width, color=colors[counter])
        #     counter +=1
        print(len(waiters), '\n', len(waiters[0][0]))
        bar1 = self.ax.bar(ind+width, waiters[0][0], width, color='r')
        bar2 = self.ax.bar(ind+width, waiters[0][1], width, color='g')
        bar3 = self.ax.bar(ind+width, waiters[0][2], width, color='b')
        self.ax.set(xlabel='Days', ylabel='waiter load',
               title='# waiter services')
        # self.ax.xticks(ind+width,['1', '2', '3','4','5','6','7','8','9', '10', '11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30'])
        self.ax.legend( (bar1, bar2, bar3), ('waiter1', 'waiter2', 'waiter3') )
        # self.ax.show()
        self.ax.grid()

class image_view2(QWidget):
    def __init__(self, *waiters):
        super().__init__()
        print("img 2 started")
        self.setWindowTitle('loadChart')
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), 'icon.png')))
        chart = canvas2(self, *waiters)
        self.setMaximumSize(chart.width(), chart.height())
        self.setMinimumSize(chart.width(), chart.height())
        
        
        
        


class simulation(QtCore.QThread):
    def __init__(self, Waiter_salary,
                        Cooker_salary,
                        Restaurant_place,
                        num_of_months,
                        num_of_waiter,
                        num_of_cooker):
        super().__init__()
        self.Waiter_salary=Waiter_salary
        self.Cooker_salary=Cooker_salary
        self.Restaurant_place=Restaurant_place
        self.num_of_months=num_of_months
        self.num_of_waiter=num_of_waiter
        self.num_of_cooker=num_of_cooker
        self.total_selling=0.0
        self.total_cost=0.0
        self.cus_each_day = []
        self.total_cus = 0
        self.waiter1=[]
        self.waiter2=[]
        self.waiter3=[]
        self.flagw1=0
        self.flagw2=0
        self.flagw3=0

    text_signal = QtCore.pyqtSignal(object)
    final_chart = QtCore.pyqtSignal(object)
    loadChart = QtCore.pyqtSignal(object)
    
    def run(self):
        env1 = simpy.Environment()
        # waiter
        waiter_R = simpy.PriorityResource(env1, capacity=self.num_of_waiter)
        # cook
        cook_R = simpy.Resource(env1, capacity=self.num_of_cooker)
        # Customers
        env1.process(self.Customer_generator(env1, waiter_R,cook_R))
        env1.run(60*24*self.num_of_months*30)
        self.total_cost += (self.Waiter_salary*self.num_of_waiter*self.num_of_months)+(self.Cooker_salary*self.num_of_cooker*self.num_of_months)+(self.Restaurant_place*self.num_of_months)
        profit=self.total_selling - self.total_cost
        Taxes=(profit*14)/100
        earnings=profit /self.num_of_months
        self.text_signal.emit('%s:  total selling = %f'% (env1.now,self.total_selling))
        self.text_signal.emit('%s:  total cost = %f'% (env1.now,self.total_cost))
        self.text_signal.emit('%s:  total Taxes = %f'% (env1.now,Taxes))
        self.text_signal.emit('%s:  total profit = %f'% (env1.now,profit))
        self.text_signal.emit('%s:  total avreag = %f'% (env1.now,earnings))
        self.final_chart.emit(self.cus_each_day)
        self.loadChart.emit([self.waiter1, self.waiter2, self.waiter3])
    
    def Customer_generator(self, env, waiter_R,cook_R):
        i=1
        time_event=720
        flag_open=1
        while True:
            random1=random.randint(1,99)
            num_of_customer=0
            if  random1< 31:
                num_of_customer=1
            elif random1>30 and random1<71:
                num_of_customer=2
            elif random1>70 and random1<91:
                num_of_customer=3
            elif random1>90 and random1<100:
                num_of_customer=4
            if  flag_open :
                prio=0        
                ran=random.randint(1,99)
                if  ran< 76:
                    prio=1
                elif ran>75 and ran<100:
                    prio=0
                env.process(self.waiter_gen(i,num_of_customer,env, waiter_R,cook_R,prio))
                self.text_signal.emit('%s:  distribution %d entering queue'% (env.now,i))
                i=i+1
                yield env.timeout(random.randint(0,90)) #randint(0,90)
            else :
                self.cus_each_day.append(i-self.total_cus)
                self.total_cus=i

                self.waiter1.append(self.flagw1)
                self.flagw1=0

                self.waiter2.append(self.flagw2)
                self.flagw2=0

                self.waiter3.append(self.flagw3)
                self.flagw3=0

                self.text_signal.emit('%s:  Restaurant closesed order clock over 12'% (env.now))
                yield env.timeout(time_event-env.now)
        
            #yield env.timeout(random.randint(0,90)) #randint(0,90)
            if env.now>=time_event :
                time_event+=720
                flag_open=flag_open^1
                if  flag_open : 
                    self.text_signal.emit('%s:  Restaurant opened order'% (env.now))
    
    def cook_gen(self, type_of_item,env,cook_R):
        self.text_signal.emit('%s:  item_type %d arriving : '% (env.now,type_of_item))
        with cook_R.request() as req:
            yield req
            self.text_signal.emit('%s:  item %d start be cooked. number item in queue_cooker %s' % (env.now,type_of_item,len(cook_R.queue)))
            cost_of_item=0.0
            selling_of_item=0
            time_of_item=0
            if  type_of_item==1:
                selling_of_item=2
                time_of_item=random.randint(1,10)
            elif type_of_item==2:
                selling_of_item=4
                time_of_item=random.randint(10,15)
            elif type_of_item==3:
                selling_of_item=5
                time_of_item=random.randint(10,15)
            elif type_of_item==4:
                selling_of_item=8
                time_of_item=random.randint(20,30)
            elif type_of_item==5:
                selling_of_item=10
                time_of_item=random.randint(20,30)    
            self.total_selling+=selling_of_item
            cost_of_item=(selling_of_item*30)/100
            self.total_cost+=cost_of_item
            yield env.timeout(time_of_item)
            self.text_signal.emit('%s:  item_type %d leave cook : '% (env.now,type_of_item))
        
    def waiter_gen(self, i,num_of_customer,env, waiter_R,cook_R,prio):
        with waiter_R.request(priority=prio) as req:
            self.text_signal.emit('%s:  distribution %d requesting resource priority= %d' % (env.now,i,prio))
            
            yield req
            if(waiter_R.count==1):
                self.flagw1+=1
            elif(waiter_R.count==2):
        
                self.flagw2+=1 
            elif(waiter_R.count==3):
                self.flagw3+=1  
            
            self.text_signal.emit('%s:  distribution %d entering queue ,priority= %d' % (env.now,i,prio))
            #random= 43
            items=[]
            total_item=0
            for num in range(num_of_customer):
                random1 = random.randint(1,99)
                num_of_item=0
                if  random1< 26:
                    num_of_item=1
                elif random1>25 and random1<66:
                    num_of_item=2
                elif random1>65 and random1<91:
                    num_of_item=3
                elif random1>90 and random1<100:
                    num_of_item=4
        ##############################################
                total_item+=num_of_item
                for j in range(num_of_item):
                    random2=random.randint(1,99)
                    type_of_item=0
                    if  random2< 11:
                        type_of_item=1
                    elif random2>10 and random2<31:
                        type_of_item=2
                    elif random2>30 and random2<61:
                        type_of_item=3
                    elif random2>60 and random2<91:
                        type_of_item=4
                    elif random2>90 and random2<100:
                        type_of_item=5
                    items.append(type_of_item)
                self.text_signal.emit('%s:  distribution %d done order<%d items>. number customer in queue_waiter: %s' % (env.now,i,num_of_item,len(waiter_R.queue)))   
            yield env.timeout(random.randint(1,4))
            for k in (items):               
                env.process(self.cook_gen(k,env,cook_R))

            

class main_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 650, 200)
        self.setWindowTitle('Simulation')
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), 'icon.png')))
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        form_group_box = QGroupBox("Input:")
        self.waiter_salary = QLineEdit('1200')
        self.cooker_salary = QLineEdit('800')
        self.restaurant_place = QLineEdit('2200')
        self.num_of_months = QLineEdit('5')
        self.num_of_waiters = QLineEdit('3')
        self.num_of_cookes = QLineEdit('2')
        
        input_form1 = QFormLayout()
        input_form1.addRow(QLabel("Waiter Salary"), self.waiter_salary)
        input_form1.addRow(QLabel("Cooker Salary"), self.cooker_salary)
        input_form1.addRow(QLabel("Restaurant Place"), self.restaurant_place)
        input_form2 = QFormLayout()
        input_form2.addRow(QLabel("Number of months"), self.num_of_months)
        input_form2.addRow(QLabel("Number of waiters"), self.num_of_waiters)
        input_form2.addRow(QLabel("Number of cookes"), self.num_of_cookes)
        formhlayout = QHBoxLayout()
        formhlayout.addLayout(input_form1)
        formhlayout.addLayout(input_form2)
        form_group_box.setLayout(formhlayout)
        buttons_layout = QHBoxLayout()
        start_simulation = QPushButton("Start Simuliation")
        start_simulation.clicked.connect(lambda: self.start_simulation_func())
        buttons_layout.addWidget(start_simulation)

        stop_simulation = QPushButton("Stop Simuliation")
        stop_simulation.clicked.connect(lambda: self.stop_simulation_func())
        buttons_layout.addWidget(stop_simulation) 
        # FOR READ ONLY IN OUTPUT
        self.text_box = QPlainTextEdit()
        self.text_box.setReadOnly(True)

        
        self.main_layout.addWidget(form_group_box)
        self.main_layout.addLayout(buttons_layout)
        self.main_layout.addWidget(self.text_box)
        self.setLayout(self.main_layout)
        self.show()

    def stop_simulation_func(self):
        sys.exit()
        # sys.stdout.flush()
     #   try:
      #      self.thread.quit()
       # except:
        #    pass
    
    def start_simulation_func(self):
        try:
            waiter_salary = int(self.waiter_salary.text())
            cooker_salary = int(self.cooker_salary.text())
            restaurant_place = int(self.restaurant_place.text())
            num_of_months = int(self.num_of_months.text())
            num_of_waiters = int(self.num_of_waiters.text())
            num_of_cookes = int(self.num_of_cookes.text())
        except:
            QMessageBox.warning(self, "Error", "Please enter valid numbers !!")
            return
        self.text_box.clear()
        self.thread = simulation(waiter_salary,
                                     cooker_salary,
                                     restaurant_place,
                                     num_of_months,
                                     num_of_waiters,
                                     num_of_cookes)
        self.thread.text_signal.connect(self.print_text)
        self.thread.final_chart.connect(self.show_images)
        self.thread.loadChart.connect(self.show_images2)
        self.thread.start()
        self.resize(650, 600)
        self.setLayout(self.main_layout)
    
    def print_text(self, text):
        self.text_box.appendPlainText(text)
    
    def show_images2(self, *waiters):
        print("show_images2")
        self.loadChart = image_view2(*waiters)
        self.loadChart.show()



    def show_images(self, data):
        self.image_view = image_view(data)
        self.image_view.show()

        # last Chart
        
        


def main():
    app = QApplication(sys.argv)
    m = main_window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    
    



    # N = 30
# ind = np.arange(len(waiter1)) 
# width = 0.7
  
# xvals = waiter1
# bar1 = plt.bar(ind, xvals, width, color = 'r')
  
# yvals = waiter2
# bar2 = plt.bar(ind+width, yvals, width, color='g')
  
# zvals = waiter3
# bar3 = plt.bar(ind+width*2, zvals, width, color = 'b')
  
# plt.xlabel("Days")
# plt.ylabel('waiter load')
# plt.title("waiter services")
# plt.xticks(ind+width,['1', '2', '3','4','5','6','7','8','9', '10', '11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30'])
# plt.legend( (bar1, bar2, bar3), ('waiter1', 'waiter2', 'waiter3') )
# plt.show()