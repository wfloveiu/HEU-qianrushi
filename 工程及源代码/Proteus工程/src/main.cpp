#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <DHT.h>
#include<Adafruit_BMP085.h>
#include<Arduino_FreeRTOS.h>

String comdata = "";

#define DHTPIN 2     //设定2号引脚为数据输入
#define DHTTYPE DHT11   // DHT 11
DHT dht(DHTPIN, DHTTYPE);

const int LDR_PIN = A0;   //设定电压输出位A0口
float var;                //暂存电压变量
bool MYBOOL=true;            //手动自动，默认自动

Adafruit_BMP085 bmp;


int led_pin[] = {8, 9, 10, 11, 12, 13, 7, 6};  //LED灯的连接的数据引脚
//8、9、10、11 分别表示温度、湿度、光照、气压的警示灯，数据不正常时，警示灯亮起
//12、13、7、6 依次模拟风机，除湿器，照明，气泵设备。
int led_cnt = 8;          //led灯的数量


TaskHandle_t StartTask_Handler;
TaskHandle_t ZongTask_Handler;

void start_task(void* pvParameters);
void zong_task(void* pvParameters);

void setup() {
  dht.begin();
  for (int i = 0; i < led_cnt; i++)
  {
    pinMode(led_pin[i], OUTPUT);
    digitalWrite(led_pin[i], LOW);
  }
  Serial.begin(9600);
  bmp.begin();
  if (!bmp.begin()) {
	  Serial.println("找不到bmp传感器!");
	  while (1) {}
  }
  xTaskCreate(              // 创建开始任务
    start_task,
    "start_task",
    128,
    NULL,
    1,
    &StartTask_Handler);
  vTaskStartScheduler();    // 开启任务调度
}

void loop() {  
}


void start_task(void* pvParameters) {
  taskENTER_CRITICAL();   // 进入临界区
  xTaskCreate(            // 创建总任务
    zong_task,
    "zong_task",
    128,
    NULL,
    2,
    &ZongTask_Handler);

  vTaskDelete(StartTask_Handler);  //删除start_task
  taskEXIT_CRITICAL();    // 退出临界区
}



void zong_task(void* pvParameters) {
  for(;;) {
    //Serial.available()判断是否有数据从COM2串口传到COM1，如果有的话，说明网页中启动了对设备的打开或关闭操作
    while (Serial.available())  
    {
        comdata += char(Serial.read());
        if(comdata == "1" && !MYBOOL)  //打开风机
        {
          digitalWrite(led_pin[4], HIGH);
        }
        else if (comdata == "2" && !MYBOOL) //关闭风机
        {
          digitalWrite(led_pin[4], LOW);
        }   
        else if(comdata == "3" && !MYBOOL)  //打开除湿
        {
          digitalWrite(led_pin[5], HIGH);
          
        }
        else if (comdata == "4" && !MYBOOL)  //关闭除湿
        {
          digitalWrite(led_pin[5], LOW);
        }      
        else if(comdata == "5" && !MYBOOL)  //打开灯光
        {
          digitalWrite(led_pin[6], HIGH);
        }
        else if (comdata == "6" && !MYBOOL)  //关闭灯光
        {
          digitalWrite(led_pin[6], LOW);
        }
        else if(comdata == "7" && !MYBOOL)  //打开饲料机
        {
          digitalWrite(led_pin[7], HIGH);
        }  
        else if (comdata == "8" && !MYBOOL)  //关闭饲料机
        {
          digitalWrite(led_pin[7], LOW);
        }
        else if(comdata == "9" && MYBOOL)  //关闭自动
        {
        	MYBOOL=false;
        }
        else if(comdata == "0" && !MYBOOL) //打开自动
        {
        	MYBOOL=true;
        }
        
        comdata = "";
    }
   
    float h = dht.readHumidity();    //湿度,h
    float t = dht.readTemperature(); //温度,t
    // 计算热指数（利用摄氏温度）
    Serial.print(F("T:"));
    Serial.print(t);
    Serial.print(",");
    Serial.print(F("H:"));
    Serial.print(h);
    Serial.print(",");
    //读取光照强度
    var = analogRead(LDR_PIN);
    Serial.print(F("L:"));
    Serial.print(var);
    Serial.print(",");
    //读取饲料量
    Serial.print(F("P:"));
    Serial.print(bmp.readSealevelPressure());
    Serial.print(",");
    

    if (t > 35 || t < 5)  //当温度不合适时，LED0亮起
    {
      digitalWrite(led_pin[0], HIGH);
    }
    else
    {
      digitalWrite(led_pin[0], LOW);
    }
    if (h > 70 || h < 30) //湿度过高或过低，LED1亮起
    {
      digitalWrite(led_pin[1], HIGH);
    }
    else
    {
      digitalWrite(led_pin[1], LOW);
    }
    if (var > 200 || var < 100)  //当光照不合适时，LED2亮起
    {
      digitalWrite(led_pin[2], HIGH);
    }
    else
    {
      digitalWrite(led_pin[2], LOW);
    }
    //当气压值不合适时，LED3亮起
    if (bmp.readSealevelPressure() > 101300 || bmp.readSealevelPressure() < 100000)
    {
      digitalWrite(led_pin[3], HIGH);
    }
    else
    {
      digitalWrite(led_pin[3], LOW);
    }

    //在自动模式下，风机，除湿器，照明，气泵设备的打开和关闭需要根据参数值大小自行判断
    //在手动模式下，这些设备的打开和关闭由管理员自行控制
    if(MYBOOL){
    	if(t>35){
    		digitalWrite(led_pin[4],HIGH);
    	}
    	else{
    		digitalWrite(led_pin[4],LOW);
    	}
    	if(h>70){
    		digitalWrite(led_pin[5],HIGH);
    	}
    	else{
    		digitalWrite(led_pin[5],LOW);
    	}
    	if(var>200){
    		digitalWrite(led_pin[6],HIGH);
    	}
    	else{
    		digitalWrite(led_pin[6],LOW);
    	}
    	if(bmp.readSealevelPressure()>101300){
    		digitalWrite(led_pin[7],HIGH);
    	}
    	else{
    		digitalWrite(led_pin[7],LOW);
    	}
      Serial.print(1);   //自动控制的模式下，model参数为1
      Serial.print(",");
    }
    else{
      Serial.print(0);  //手动控制模式下，model参数为0
      Serial.print(",");
    }
    
    Serial.print(digitalRead(led_pin[4]));
    Serial.print(",");
    Serial.print(digitalRead(led_pin[5]));
    Serial.print(",");
    Serial.print(digitalRead(led_pin[6]));
    Serial.print(",");
    Serial.print(digitalRead(led_pin[7]));
  }
}

// void press_task(void* pvParameters) {
//   for(;;) {
   
//     //读取气压值
//     Serial.print("P:");
//     Serial.print(bmp.readSealevelPressure());
//     if (bmp.readSealevelPressure() > 101300 || bmp.readSealevelPressure() < 100000)
//     {
//       digitalWrite(led_pin[3], HIGH);
//     }
//     else
//     {
//       digitalWrite(led_pin[3], LOW);
//     }
//      vTaskDelay(5000);
//   }
// }
