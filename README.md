### 一 接口规范

#### 1.0 报头

服务器只支持POST, template如下:

```http
POST \<target> HTTP/1.1\r\n
Content-Type: text/json;charset=utf-8\r\n
Connection: keep-alive\r\n
Content-Length: <length>\r\n\r\n'
```

#### 1.1 注册

* target: \register

* request body:

  ```json
  {
  	"username": <username>,
  	"password": <password>
  }
  ```
  用户名密码只支持 r'[\w]{1,10}' 类型(client处理)
* response body:

  ```json
  {
      "code": <code>,
      "msg": <message>,
      "type": "register"
  }
  ```

  服务器返回信息至少包含上述三项, 其中"type"总与target相同

  | code | msg                 |
  | ---- | ------------------- |
  | 0    | register successful |
  | 1    | duplicate username  |

#### 1.2 登录

* target: \login

* request body: same as 1.1

* response body: 

  ```json
  {
      "code": <code>,
      "msg": <message>,
      "type": "login",
      "token": <token>
  }
  ```

  token为u_int_32类型
  
  | code | msg                |
  | ---- | ------------------ |
  | 0    | login successful   |
  | 1    | nonexist username  |
  | 2    | incorrect password |
#### 1.3 添加好友

* target: \add-friend

* request body:

  ```json
  {	
      "token": <token>,
      "username": <username>,
      "who": <friendname>
  }
  ```

  登陆后任意操作都需要token

* response body:

  ```json
  {
      "code": <code>,
      "msg": <message>,
      "type": "add-friend"
  }
  ```
  
  | code | msg             |
| ---- | --------------- |
| 0    | send successful |
| 1    | invalid token   |
| 2    | already friends |
| 3    | nonexist name   |
| 4    | user is offline |


#### 1.4 添加好友结果

* target: \add-result

* request body:

  ```json
  {
      "token": <token>,
      "from": <username>,
      "to": <friendname>,
      "result": <boolean>
  }
  ```

* response body:

  ```json
  {
      "code": <code>,
      "msg": <message>,
      "type": "add-result"
  }
  ```

  | code | msg             |
  | ---- | --------------- |
  | 0    | send successful |
  | 1    | invalid token   |
  
#### 1.5 获取好友列表

* target: \friends-list

* request body:

  ```json
  {	
      "token": <token>,
      "username": <username>
  }
  ```
  
* response body:

  ```json
  {
      "code": <code>,
      "msg": <message>,
      "type": "friends-list",
      "list": ["a","b"...]
  }
  ```

  
  | code | msg            |
  | ---- | -------------- |
  | 0    | get successful |
  | 1    | invalid token  |

#### 1.6 发送消息

* target: \send-msg

* request body:

  ```json
  {
      "token": <token>,
      "username":<username>,
      "who": <username>,
      "msg": <message>
  }
  ```


* response body:

  ```json
  {
      "code": <code>,
      "msg": <message>,
      "type": "send-msg"
  }
  ```
  | code | msg             |
  | ---- | --------------- |
| 0    | send successful |
| 1    | invalid token   |
| 2    | user is offline |

#### 1.7 离线

* target: \offline

* request body:

  ```json
  {
  	"username": <username>
  }
  ```
  

#### 1.8 发送消息 [服务器]

* target: \

* request body:

  ```json
  {
      "from": <username>,
      "msg": <message>
  }
  ```
