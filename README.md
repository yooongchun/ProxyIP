# ProxyIP
抓取代理IP

`author:yooongchun`  `version:v0.1`  `date:2018-06-29`  

---

很多时候，需要用到代理IP。比如在开发爬虫程序的时候，为了反爬，需要使用代理IP。

---
首先给出程序实现的功能，然后再来说明开发思路：

 - 完整代码下载地址：
    https://github.com/yooongchun/ProxyIP

 - 功能：

     - 从指定的网站抓取代理IP地址并存入数据库`all_ip_table`中，当前抓取的地址包括：
        - 西刺网站
        - 快代理网站
        - 66代理网站
        - 89代理网站
        - 秘密代理网站
        - data5u网站
        - 免费代理IP网站
        - 云代理网站
        - 全网代理网站
     - 对保存在数据库表`all_ip_table`中的IP地址进行定时筛选，有效的添加到`ip_table` 中，无效的删除
     - 对保存在`ip_table`中的IP地址进行定期校验，无效的删除

- 基本逻辑：

  - 程序包含了4个`.py`文件，各个模块功能如下：

    - `config` 模块用来配置程序信息打印级别和打印位置你只需要在该位置的`config` 函数中指定参数然后在别的模块中这样调用：

      ```python
      import config
      config.config()
      ```

    - `database` 模块用来提供存储数据库操作，包括：添加到数据库、从数据库中获取和删除操作，你只需要这样调用：

      ```python
      from database import IP_Pool
      pool=IP_Pool(database_name,ip_table_name)
      pool.push(ip_list)# 存入
      pool.pull(random_flag)# 取出,random_flag 为True时随机取一个
      pool.delete(ip) # 删除，ip为None时删除所有记录
      ```

    - `UA`模块用来提供网络请求头，主要是UA和referer，该模块用来模拟不同的浏览器请求头，这样调用：

      ```python
      from UA import FakeUserAgent
      headers=FakeUserAgent().random_headers()
      ```

    - `ProxyIP` 模块是程序的核心模块，包含了两个类，`Crawl` 类用来抓取IP，使用多线程模式抓取，`Validation` 类用来校验IP，其中`multiple_filter` 函数用来从`all_ip_table` 中筛选有效IP，而`multiple_validation` 用来从`ip_table`中定时校验IP，无效删除，启用该模块即可运行抓取和校验进程，用法：

      启动main函数即可启用抓取进程和验证进程（双进程模式）。

      ```python
      main()
      ```

      如果只想启用抓取IP的进程，则运行:

      ```python
      crawl=Crawl()
      crawl.run()
      ```

      如果只想启用验证进程，则运行：

      ```python
      validation=Validation()
      validation.run()
      ```

---

以下简要说明开发的思路：

- 首先需要到提供代理IP的网站去抓取代理IP，使用的网站已经列举在文章开头。这里涉及两个主要内容：去网站上请求网页，然后解析网页获取IP地址。请求网页使用`requests` 库，最简单的请求方式为：

  ```python
  response = requests.get(url)
  ```

  有时，请求次数过多，也会被网站禁止访问，因而可以使用代理IP去请求：

  ```python
  response = requests.get(url=url, headers=headers,proxies=proxies,timeout=5)
  ```

  这里，`headers` 是请求头，`proxies`是代理IP，代理IP构造方式为：

  ```python
  proxies={"http": "http://" + IP+":"+PORT,"https":"https://"+IP+":"+PORT} # IP地址+端口
  ```

  获得请求的网页之后，判断返回是否正确：

  ```python
  response.status_code==200
  ```

  若返回正确，则可进行网页解析。网页解析使用`BeautifulSoup` 库，`Python3` 和`Windows10` 环境下使用`pip3` 命令安装：

  ```python
  pip3 install bs4
  ```

  要获取解析内容，先要知道返回的网页结构，可以通过`Google` 浏览器查看网页结构：

  ```
  打开网页--按下F12--选择Elements
  ```

  经过查看，发现IP地址均储存在`td` 标签下，使用正则表达式来提取：

  ```python
  all_ip = []
  soup = BeautifulSoup(html, "lxml")
  tds = soup.find_all("td")
  for index, td in enumerate(tds):
      if not re.match(r"^\d+\.\d+\.\d+\.\d+$",re.sub(r"\s+|\n+|\t+", "", td.text)):
          pass
      all_ip.append(re.sub(r"\s+|\n+|\t+", "", td.text))
  ```

  这里用到一个`lxml`解析库，没有的话需要单独安装：

  ```powershell
  pip3 install lxml
  ```

- 接下来需要把IP地址储存到数据库中，方便使用，储存用到的数据库是`SQLite`，基本操作包括：

  加入数据库：

  ```python
  def push(self, IP_list):
      '''存储IP，传入一个列表，格式为[[IP,PORT,ADDRESS,TYPE,PROTOCOL],...]'''
      logging.info(u"写入数据库表：%s..." % (self.__table_name))
      try:
          conn = sqlite3.connect(self.__database_name, isolation_level=None)
          conn.execute(
              "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER,ADDRESS CHAR(50),TYPE CHAR(50),PROTOCOL CHAR(50))"
              % self.__table_name)
          except Exception:
              logging.error("连接数据库出错,退出：{}".format(self.__database_name))
              return
          for one in IP_list:
              if len(one) < 5:
                  logging.error("IP格式不正确：{}，跳过！".format(one))
                  continue
                  conn.execute(
                      "insert or ignore into %s(IP,PORT,ADDRESS,TYPE,PROTOCOL) values (?,?,?,?,?)"
                      % (self.__table_name),
                      (one[0], one[1], one[2], one[3], one[4]))
                  conn.commit()
                  conn.close()
  
  ```

  从数据库中提取：

  ```python
  
  def pull(self, random_flag=False):
      '''获取IP，返回一个列表'''
      try:
          conn = sqlite3.connect(self.__database_name, isolation_level=None)
          conn.execute(
              "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER,ADDRESS CHAR(50),TYPE CHAR(50),PROTOCOL CHAR(50))"
              % self.__table_name)
          except Exception:
              logging.error("连接数据库出错：{}".format(self.__database_name))
              return
          cur = conn.cursor()
          if random_flag:
              cur.execute("select * from %s order by random() limit 1" %
                          self.__table_name)
              response = cur.fetchone()
              else:
                  cur.execute("select * from %s" % self.__table_name)
                  response = cur.fetchall()
                  cur.close()
                  conn.close()
                  return response
  
  ```

  以及删除：

  ```python
  
  def delete(self, IP=None):
      '''删除指定的记录'''
      try:
          conn = sqlite3.connect(self.__database_name, isolation_level=None)
          conn.execute(
              "create table if not exists %s(IP CHAR(20) UNIQUE, PORT INTEGER,ADDRESS CHAR(50),TYPE CHAR(50),PROTOCOL CHAR(50))"
              % self.__table_name)
          except Exception:
              logging.error("连接数据库出错：{}".format(self.__database_name))
              return
          cur = conn.cursor()
          if IP is not None:
              logging.info(u"删除记录：{}\t{}".format(self.__table_name, IP[0]))
              cur.execute("delete from %s where IP=?" % self.__table_name,
                          (IP[0], ))
              else:
                  logging.info(u"删除所有记录:{}".format(self.__table_name))
                  cur.execute("delete from %s" % self.__table_name)
                  cur.close()
                  conn.close()
  ```

- 然后需要对数据进行校验。包括从抓取到的IP中进行筛选有效IP和对有效IP进行定期校验，校验用到的网址为：`http://httpbin.org/get` 校验的思路就是用获得的IP构造代理IP，使用随机请求头取访问该网址，如果访问正常，说明该IP有效，则添加到数据库中，校验函数：

  ```python
  def __check_ip_validation(self, ip):
          '''校验IP地址有效性'''
          try:
              IP = str(ip[0]) + ":" + str(ip[1])
          except Exception:
              return None
          re_conn_time = 2
          cnt = 0
          while cnt < re_conn_time:
              cnt += 1
              try:
                  proxies = {"http": "http://" + IP}
                  response = requests.get(
                      url=self.__URL,
                      headers=FakeUserAgent().get_random_headers(),
                      proxies=proxies,
                      timeout=5)
              except Exception:
                  time.sleep(2 * random.random())
                  response = None
          if response is None:
              return
          if int(response.status_code) == 200 and IP.split(
                  ":")[0] in response.text:
              return True
          else:
              return False
  ```

  注意：从网站上获取到的IP有的是非高匿的（虽然用了代理，但是网站仍能够知道你的真实IP），因而还需要校验IP地址是否高匿，方法非常简单，因为抓取的时候保存了此信息，只需要判断一下即可：

  ```python
  def __check_ip_anonumous(self, ip):
          '''检验IP是否高匿名'''
          if "高匿" in str(ip):
              return True
          else:
              return False
  ```

- 接下来就是一些琐碎的处理，包括信息打印，异常处理等等。另外，上面给出的代码都是核心语句，并不是完整代码，完整代码请到`github` 下载，地址：https://github.com/yooongchun/ProxyIP。

---

最后，联系信息：


- 获得帮助与建议反馈：

  任何时候，欢迎联系作者`yooongchun` :`Email:yooongchun@foxmail.com`

- 更多有趣/实用内容，关注我：

  - `微信公众号: yooongchun小屋`
  - `CSDN: https://blog.csdn.net/zyc121561`
  - `github: https://github.com/yooongchun`




