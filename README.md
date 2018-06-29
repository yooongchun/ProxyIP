# ProxyIP
抓取代理IP

`v0.1` `2018-06-29` 

---

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
  - 对保存在数据库表`all_ip_table`中的IP地址进行定时校验，有效的添加到`ip_table` 中，无效的删除
  - 对保存在`ip_table`中的IP地址进行定期校验，无效的删除

- 基本逻辑：

  程序包含了两个类，`Crawl` 类用来抓取IP，使用多线程模式抓取，`Validation` 类用来校验IP，其中`multiple_filter` 函数用来从`all_ip_table` 中筛选有效IP，而`multiple_validation` 用来从`ip_table`中定时校验IP，无效删除

- 用法：

  启动main函数即可启用抓取进程和验证进程（双进程模式）。

  ```python
  main()
  ```

  如果只想启用抓取进程，则运行

  ```python
  crawl=Crawl(paras)
  crawl.run()
  ```

  如果只想启用验证进程，则运行：

  ```python
  validation=Validation(paras)
  validation.run()
  ```

- 获得帮助与建议反馈：

  任何时候，欢迎联系作者`yooongchun` :

  - `Email:yooongchun@foxmail.com`

- 更多有趣/实用内容，关注我：

  - `微信公众号: yooongchun小屋`
  - `CSDN: https://blog.csdn.net/zyc121561`
  - `github: https://github.com/yooongchun`

