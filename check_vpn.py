#!/usr/bin/env python3
import subprocess,time,threading,os

hk_hosts = ['a.hkgjsq.com', 'b.hkgjsq.com', 'c.hkgjsq.com']
hk_confs = {'a.hkgjsq.com' : 'China-HongKong-01', 'b.hkgjsq.com' : 'China-HongKong-02', 'c.hkgjsq.com' : 'China-HongKong-03'}
ping_values = {}
for host in hk_hosts:
    ping_values[host] = None
best_host = ''
best_ping_value = None

def global_ping_host(host, num):
    global ping_values
    with subprocess.Popen(["ping", host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
        ping_times = []
        lines_count = 0
        while True:
            line = proc.stdout.readline().strip()
            lines_count += 1
            if line.endswith(b' ms') and line.startswith(b'64 bytes from'):
                ping_times.append(float(line[line.find(b'time=') + 5 : line.find(b' ms')]))
            if len(ping_times) >= num:
                break
            if lines_count >= num + 5:
                break
    print(host, ping_times)
    ping_values[host] = sum(ping_times) / len(ping_times)

def ping_host(host, num):
    with subprocess.Popen(["ping", host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
        ping_times = []
        lines_count = 0
        while True:
            line = proc.stdout.readline().strip()
            lines_count += 1
            if line.endswith(b' ms') and line.startswith(b'64 bytes from'):
                ping_times.append(float(line[line.find(b'time=') + 5 : line.find(b' ms')]))
            if len(ping_times) >= num:
                break
            if lines_count >= num + 5:
                break
    print(host, ping_times, sum(ping_times) / len(ping_times))

def get_best_host(hosts):
    global ping_values
    global best_host
    global best_ping_value
    threads = []
    for host in hosts:
        threads.append(threading.Thread(target = global_ping_host, args=(host, 6)))
    start_time = time.time()
    for thread in threads:
        thread.start()
    while True:
        if time.time() - start_time >= 20:
            break
        BREAK = True
        for thread in threads:
            if thread.is_alive():
                BREAK = BREAK and False
            else:
                BREAK = BREAK and True
        if BREAK:
            break
    for value in ping_values:
        if best_host == '' and ping_values[value] is not None:
            best_host = value
            best_ping_value = ping_values[value]
        if ping_values[value] is not None and ping_values[value] < best_ping_value:
            best_host = value
            best_ping_value = ping_values[value]

def ping_host_ok(host):
    start_time = time.time()
    thread = threading.Thread(target = ping_host, args = (host, 3))
    thread.daemon = True
    thread.start()
    while True:
        if time.time() - start_time >= 10:
            return False
        if not thread.is_alive():
            return True

if not ping_host_ok('www.google.com'):
    print("ping google error")
    get_best_host(hk_hosts)
    print(best_host)
    print(best_ping_value)
    if best_host != '':
        with open('/etc/default/openvpn', mode='w') as w:
            w.write('AUTOSTART=' + '"' + hk_confs[best_host] + '"\nOPTARGS=""\nOMIT_SENDSIGS=0')
        os.system('service openvpn restart')
else:
    print('ping google ok')