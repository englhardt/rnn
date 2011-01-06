# -*- coding:utf-8 -*-

import sys
import re
import subprocess
import tempfile
import print_log

def plot_state(f, filename, epoch):
    params = print_log.read_parameter(f)
    c_state_size = int(params['c_state_size'])
    out_state_size = int(params['out_state_size'])
    tmp = tempfile.NamedTemporaryFile()
    sys.stdout = tmp
    print_log.print_state(f, epoch)
    sys.stdout.flush()
    type = {}
    type['Target'] = (out_state_size, lambda x: 2 * x + 2)
    type['Output'] = (out_state_size, lambda x: 2 * x + 3)
    type['Context'] = (c_state_size, lambda x: x + 2 * out_state_size + 2)
    for k,v in type.iteritems():
        p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
                shell=True)
        p.stdin.write("set nokey;")
        p.stdin.write("set title 'Type=%s  File=%s';" % (k, filename))
        p.stdin.write("set xlabel 'Time step';")
        p.stdin.write("set ylabel '%s';" % k)
        command = ["plot "]
        for i in xrange(v[0]):
            command.append("'%s' u 1:%d w l," % (tmp.name, v[1](i)))
        p.stdin.write(''.join(command)[:-1])
        p.stdin.write('\n')
        p.stdin.write('exit\n')
        p.wait()
    sys.stdout = sys.__stdout__

def plot_weight(f, filename):
    params = print_log.read_parameter(f)
    in_state_size = int(params['in_state_size'])
    c_state_size = int(params['c_state_size'])
    out_state_size = int(params['out_state_size'])
    index_i2c, index_c2c, index_c2o = [], [], []
    s = [x+2 for x in xrange(c_state_size *
        (in_state_size + c_state_size + out_state_size))]
    for i in xrange(c_state_size):
        index_i2c.extend(s[:in_state_size])
        s = s[in_state_size:]
        index_c2c.extend(s[:c_state_size])
        s = s[c_state_size:]
    for i in xrange(out_state_size):
        index_c2o.extend(s[:c_state_size])
        s = s[c_state_size:]
    type = {'Weight (input to context)':index_i2c,
            'Weight (context to context)':index_c2c,
            'Weight (context to output)':index_c2o}
    for k,v in type.iteritems():
        p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
                shell=True)
        p.stdin.write("set nokey;")
        p.stdin.write("set title 'Type=Weight  File=%s';" % filename)
        p.stdin.write("set xlabel 'Learning epoch';")
        p.stdin.write("set ylabel '%s';" % k)
        command = ["plot "]
        for i in v:
            command.append("'%s' u 1:%d w l," % (filename, i))
        p.stdin.write(''.join(command)[:-1])
        p.stdin.write('\n')

def plot_threshold(f, filename):
    params = print_log.read_parameter(f)
    c_state_size = int(params['c_state_size'])
    out_state_size = int(params['out_state_size'])
    type = {}
    type['Threshold (context)'] = (c_state_size, lambda x: x + 2)
    type['Threshold (output)'] = (out_state_size,
            lambda x: x + c_state_size + 2)
    for k,v in type.iteritems():
        p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
                shell=True)
        p.stdin.write("set nokey;")
        p.stdin.write("set title 'Type=Threshold  File=%s';" % filename)
        p.stdin.write("set xlabel 'Learning epoch';")
        p.stdin.write("set ylabel '%s';" % k)
        command = ["plot "]
        for i in xrange(v[0]):
            command.append("'%s' u 1:%d w l," % (filename, v[1](i)))
        p.stdin.write(''.join(command)[:-1])
        p.stdin.write('\n')

def plot_tau(f, filename):
    params = print_log.read_parameter(f)
    c_state_size = int(params['c_state_size'])
    p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
            shell=True)
    p.stdin.write("set nokey;")
    p.stdin.write("set title 'Type=Time-constant  File=%s';" % filename)
    p.stdin.write("set xlabel 'Learning epoch';")
    p.stdin.write("set ylabel 'Time constant';")
    command = ["plot "]
    for i in xrange(c_state_size):
        command.append("'%s' u 1:%d w l," % (filename, i+2))
    p.stdin.write(''.join(command)[:-1])
    p.stdin.write('\n')

def plot_sigma(f, filename):
    p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
            shell=True)
    p.stdin.write("set nokey;")
    p.stdin.write("set title 'Type=Variance  File=%s';" % filename)
    p.stdin.write("set xlabel 'Learning epoch';")
    p.stdin.write("set ylabel 'Variance';")
    p.stdin.write("plot '%s' u 1:3 w l" % filename)
    p.stdin.write('\n')

def plot_init(f, filename, epoch):
    params = print_log.read_parameter(f)
    in_state_size = int(params['in_state_size'])
    c_state_size = int(params['c_state_size'])
    delay_length = int(params['delay_length'])
    dimension = in_state_size * delay_length + c_state_size
    tmp = tempfile.NamedTemporaryFile()
    sys.stdout = tmp
    print_log.print_init(f, epoch)
    sys.stdout.flush()
    p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
            shell=True)
    p.stdin.write("set nokey;")
    p.stdin.write("set title 'Type=Init  File=%s';" % filename)
    p.stdin.write("set xlabel 'Time step';")
    p.stdin.write("set ylabel 'Initial state';")
    p.stdin.write("set pointsize 3;")
    command = ["plot "]
    index = [(2*x,(2*x+1)%dimension) for x in xrange(dimension) if 2*x <
            dimension]
    for x in index:
        command.append("'%s' u %d:%d w p," % (tmp.name, x[0]+2, x[1]+2))
    p.stdin.write(''.join(command)[:-1])
    p.stdin.write('\n')
    p.stdin.write('exit\n')
    p.wait()
    sys.stdout = sys.__stdout__

def plot_adapt_lr(f, filename):
    p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
            shell=True)
    p.stdin.write("set nokey;")
    p.stdin.write("set logscale y;")
    p.stdin.write("set title 'Type=Learning-rate  File=%s';" % filename)
    p.stdin.write("set xlabel 'Learning epoch';")
    p.stdin.write("set ylabel 'Adaptive learning rate';")
    p.stdin.write("plot '%s' u 1:2 w l" % filename)
    p.stdin.write('\n')

def plot_error(f, filename):
    params = print_log.read_parameter(f)
    target_num = int(params['target_num'])
    p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
            shell=True)
    p.stdin.write("set nokey;")
    p.stdin.write("set logscale y;")
    p.stdin.write("set title 'Type=Error  File=%s';" % filename)
    p.stdin.write("set xlabel 'Learning epoch';")
    p.stdin.write("set ylabel 'Error / Length';")
    command = ["plot "]
    for i in xrange(target_num):
        command.append("'%s' u 1:%d w l," % (filename, i+2))
    p.stdin.write(''.join(command)[:-1])
    p.stdin.write('\n')

def plot_lyapunov(f, filename):
    params = print_log.read_parameter(f)
    target_num = int(params['target_num'])
    ls_num = int(params['lyapunov_spectrum_num'])
    for i in xrange(ls_num):
        p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
                shell=True)
        p.stdin.write("set nokey;")
        p.stdin.write("set title 'Type=Lyapunov  File=%s';" % filename)
        p.stdin.write("set xlabel 'Learning epoch';")
        p.stdin.write("set ylabel 'Lyapunov[%d]';" % i)
        command = ["plot 0 w l lt 0"]
        for j in xrange(target_num):
            command.append("'%s' u 1:%d w l" % (filename, i+j*ls_num+2))
        p.stdin.write(','.join(command))
        p.stdin.write('\n')

def plot_entropy(f, filename):
    params = print_log.read_parameter(f)
    target_num = int(params['target_num'])
    type = ['KL-divergence', 'generation-rate', 'entropy(target)',
            'entropy(out)']
    for i in [0, 1, 3]:
        p = subprocess.Popen(['gnuplot -persist'], stdin=subprocess.PIPE,
                shell=True)
        p.stdin.write("set nokey;")
        p.stdin.write("set title 'Type=%s  File=%s';" % (type[i], filename))
        p.stdin.write("set xlabel 'Learning epoch';")
        p.stdin.write("set ylabel '%s';" % type[i])
        command = ["plot "]
        for j in xrange(target_num):
            command.append("'%s' u 1:%d w l," % (filename, i+j*4+2))
        p.stdin.write(''.join(command)[:-1])
        p.stdin.write('\n')

def main():
    epoch = None
    if str.isdigit(sys.argv[1]):
        epoch = int(sys.argv[1])
    args = sys.argv[2:]
    for arg in args:
        f = open(arg, 'r')
        line = f.readline()
        if (re.compile(r'^# STATE FILE').match(line)):
            plot_state(f, arg, epoch)
        elif (re.compile(r'^# WEIGHT FILE').match(line)):
            plot_weight(f, arg)
        elif (re.compile(r'^# THRESHOLD FILE').match(line)):
            plot_threshold(f, arg)
        elif (re.compile(r'^# TAU FILE').match(line)):
            plot_tau(f, arg)
        elif (re.compile(r'^# SIGMA FILE').match(line)):
            plot_sigma(f, arg)
        elif (re.compile(r'^# INIT FILE').match(line)):
            plot_init(f, arg, epoch)
        elif (re.compile(r'^# ADAPT_LR FILE').match(line)):
            plot_adapt_lr(f, arg)
        elif (re.compile(r'^# ERROR FILE').match(line)):
            plot_error(f, arg)
        elif (re.compile(r'^# LYAPUNOV FILE').match(line)):
            plot_lyapunov(f, arg)
        elif (re.compile(r'^# ENTROPY FILE').match(line)):
            plot_entropy(f, arg)
        f.close()


if __name__ == "__main__":
    main()

