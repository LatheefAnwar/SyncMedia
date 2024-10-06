Before running the Django server install "redis server" 

run the redis server by typing "redis-server" on the terminal

[12588] 12 Jun 13:48:28.832 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[12588] 12 Jun 13:48:28.832 # Redis version=5.0.14.1, bits=64, commit=ec77f72d, modified=0, pid=12588, just started
[12588] 12 Jun 13:48:28.832 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
[12588] 12 Jun 13:48:28.834 # Could not create server TCP listening socket *:6379: bind: An operation was attempted on something that is not a socket.

If you come up with the above error force run the server to run in a separate port in the Django settings I configured the redis server to run on port 6380 

To run on a new port type "redis-server --port 6380" this will run the server on a new port for the redis finally if success you will see a success message

[13964] 12 Jun 13:50:33.078 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[13964] 12 Jun 13:50:33.078 # Redis version=5.0.14.1, bits=64, commit=ec77f72d, modified=0, pid=13964, just started
[13964] 12 Jun 13:50:33.078 # Configuration loaded
                _._
           _.-``__ ''-._
      _.-``    `.  `_.  ''-._           Redis 5.0.14.1 (ec77f72d/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6380
 |    `-._   `._    /     _.-'    |     PID: 13964
  `-._    `-._  `-./  _.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |           http://redis.io
  `-._    `-._`-.__.-'_.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |
  `-._    `-._`-.__.-'_.-'    _.-'
      `-._    `-.__.-'    _.-'
          `-._        _.-'
              `-.__.-'

[13964] 12 Jun 13:50:33.082 # Server initialized
[13964] 12 Jun 13:50:33.082 * Ready to accept connections


without closing the server get to the virtual environment and open three new terminal for celery server and Django server and react server 

Django run server
react run server 
 
and for celery make sure the terminal is using the virtual environment and type "celery -A backend.celery worker -l info -P threads --loglevel=info" if success you will see a 

 
 -------------- celery@DESKTOP-54BH9KF v5.4.0 (opalescent)
--- ***** -----
-- ******* ---- Windows-11-10.0.22621-SP0 2024-06-12 22:45:15
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         backend:0x197fe6fbda0
- ** ---------- .> transport:   redis://localhost:6380/0
- ** ---------- .> results:     redis://localhost:6380/0
- *** --- * --- .> concurrency: 12 (thread)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . backend.celery.debug_task
  . marketing.tasks.send_email_campaign_mass_mail
  . marketing.tasks.send_single_email


