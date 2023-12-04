import pymysql
import time

def connect_db():
    database_info={
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'passwd': 'wf140039',
        'charset': 'utf8mb4' 
    }
    try:
        conn = pymysql.connect(**database_info)
    except Exception as e:
        print("database_connection is failure!")
        print(e)
        return False
    else:
        print("database_connection is ok!")
        return conn

def connect_BigPeng():
    database_info={
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'db': 'BigPeng',
        'passwd': 'wf140039',
        'charset': 'utf8mb4' 
    }
    try:
        conn = pymysql.connect(**database_info)
    except Exception as e:
        print("dapeng_connection is failure!")
        print(e)
        return False
    else:
        print("大棚数据库连接成功!")
        return conn

def create_db():
    conn=connect_db()
    cur=conn.cursor()
    try:
        cur.execute("create database BigPeng;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("database_create_failure!")
        print(e)
        return False
    else:
        conn.close()
        print("database_create_success!")
        return True

def create_table():
    conn=connect_BigPeng()
    cur=conn.cursor()
    try:
        cur.execute("""
        create table `users`(
            `user_id` int(11) unsigned unique NOT NULL AUTO_INCREMENT,
            `nickname` char(20) unique NOT NULL,
            `password` char(20) NOT NULL,
            `level` tinyint(1) default 3,
            PRIMARY KEY (`user_id`),
            index id(user_id)
        )DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=1;""")
        #id,nickname,password,level
        cur.execute("""
        create table `logs`(
            `log_id` int(11) unsigned unique NOT NULL AUTO_INCREMENT,
            `time` char(20) not null,
            `temperature` float(2),
            `humidity` float(2),
            `light` float(2),
            `pressure` float(2),
            PRIMARY KEY(`log_id`),
            index id(log_id)
        )DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=1;""")
        cur.execute("""
        create table `e_logs`(
            `log_id` int(11) unsigned unique NOT NULL AUTO_INCREMENT,
            `time` char(20) not null,
            `model` int(2) not null,
            `temperature` int(2),
            `humidity` int(2),
            `light` int(2),
            `pressure` int(2),
            PRIMARY KEY(`log_id`),
            index id(log_id)
        )DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=1;""")
        #初始化用户
        cur.execute("""
        insert into users (`nickname`,`password`) values ("root","123456");
        """)
        cur.execute("""
        insert into e_logs (`time`,`model`,`temperature`,`humidity`,`light`,`pressure`) values ("1592892440",1,0,0,0,0);
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("table_create_failure")
        print(e)
        return False
    else:
        conn.close()
        print("users,logs,e_logs,table_create_success")
        return True

#删库跑路
def drop_db():
    conn=connect_db()
    cur=conn.cursor()
    try:
        cur.execute("drop database if exists BigPeng;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("删库失败！")
        print(e)
    else:
        conn.close()
        print("数据库已删除，快跑路...")

def find_db():
    conn=connect_db() #连接local
    cur=conn.cursor()
    try:
        cur.execute("show databases;")
        results=cur.fetchall()
        conn.commit()
        #print(results)
    except Exception as e:
        conn.close()
        print("database_find_failure!")
        print(e)
    else:
        conn.close() #关闭local
        for db in results:
            if 'bigpeng' in db:
                print("find dapeng database!begin connecting!")
                return True
        print("cannot find dapeng database!begin create!")
        return False

def insert_user(nickname,passwd):
    conn=connect_BigPeng()
    cur=conn.cursor()
    try:
        cur.execute(f"""
        insert into users
        (`nickname`,`password`)
        values
        ('{nickname}','{passwd}');
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("用户创建失败！")
        print(e)
        return False
    else:
        conn.close()
        return True

def insert_log(time,temperature,humidity,light,pressure):
    conn=connect_BigPeng()
    cur=conn.cursor()
    try:
        cur.execute(f"""
        insert into logs
        (`time`,`temperature`,`humidity`,`light`,`pressure`)
        values
        ('{time}','{temperature}','{humidity}','{light}','{pressure}');
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("数据记录失败！")
        print(e)
        return False
    else:
        conn.close()
        print("数据记录成功！")
        return True

def insert_elog(time,model,temperature,humidity,light,pressure):
    conn=connect_BigPeng()
    cur=conn.cursor()
    try:
        cur.execute(f"""
        insert into e_logs
        (`time`,`model`,`temperature`,`humidity`,`light`,`pressure`)
        values
        ('{time}','{model}','{temperature}','{humidity}','{light}','{pressure}');
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        print("设备数据记录失败！")
        print(e)
        return False
    else:
        conn.close()
        print("设备数据记录成功！")
        return True

def select_logs(timestamp):
    conn=connect_BigPeng()
    cur=conn.cursor()
    sql=f"select * from logs where time>={timestamp};"  #该语句从名为 logs 的表中选择时间大于等于指定时间戳的记录。
    try:
        ans=cur.fetchmany(cur.execute(sql))
    except Exception as e:
        conn.close()
        print("数据查找失败！")
        print(e)
        return False
    else:
        conn.close()
        print("数据查找成功")
        return ans

def select_elogs(timestamp):
    conn=connect_BigPeng()
    cur=conn.cursor()
    sql=f"select * from e_logs where time>={timestamp};"
    try:
        ans=cur.fetchmany(cur.execute(sql))
    except Exception as e:
        conn.close()
        print("设备数据查找失败！")
        print(e)
        return False
    else:
        conn.close()
        print("设备数据查找成功")
        return ans

def select_newlogs(index):  #从数据库中按时间降序查找最新的日志记录。
    conn=connect_BigPeng()
    cur=conn.cursor()
    sql=f"select * from logs order by time desc limit 0,{index};"   #创建查询语句：从名为 logs 的表中按时间降序选择最新的 index 条记录。
    try:
        ans=cur.fetchmany(cur.execute(sql))
    except Exception as e:
        conn.close()
        print("数据查找失败！")
        print(e)
        return False
    else:
        conn.close()
        print("数据查找成功")
        return ans

def select_newelogs(index):
    conn=connect_BigPeng()
    cur=conn.cursor()
    sql=f"select * from e_logs order by time desc limit 0,{index};"
    try:
        ans=cur.fetchmany(cur.execute(sql))
    except Exception as e:
        conn.close()
        print("设备数据查找失败！")
        print(e)
        return False
    else:
        conn.close()
        print("设备数据查找成功")
        return ans

def select_users(nickname,passwd):
    conn=connect_BigPeng()
    cur=conn.cursor()
    sql=f"select password from `users` where `nickname`='{nickname}';"
    try:
        ans=cur.fetchmany(cur.execute(sql))
    except Exception as e:
        conn.close()
        print("用户查找失败！")
        print(e)
        return False
    else:
        conn.close()
        #print(ans[0][0])
        if(ans[0][0]==passwd):
            print("用户查找成功！")
            return True
        else:
            print("用户密码不正确！")
            return False

def check():
    print("Connecting...")
    f=find_db()
    if(f==False):
        if(create_db()):
            create_table()

if __name__ == "__main__":
    check()
