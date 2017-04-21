import tensorflow as tf
from tensorflow.python.ops import rnn, rnn_cell
import numpy as np
from process import Process
from sklearn.metrics import mean_squared_error
import time
import sys, getopt


def main(argv):
    n_iterations = 100  # numer of iterations
    input_size = 12  # process instances * 2
    hidden_neurons = 10  # numer of hidden neurons
    n_steps = int(input_size / 2)
    n_inputs = 2
    lr = 0.01  # learning rate
    obj_type = 'sell'
    obj_id = '24344'

    try:
        opts, args = getopt.getopt(argv, "hi:p:n:l:t:d:")
    except getopt.GetoptError:
        print('Error parsing the command arguments. Check -h for more information.')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help = """Command sintaxis (described below): lstm.py [OPTION]...

    -i <n_iterations>       Expected a integer. Number of train iterations. Default 100
    -p <input size>         Expected a integer. Input's size. Default 12
    -n <hidden neurons>     Expected a integer. LSTM cell's size. Default 10
    -l <lr size>            Expected a double between 0 and 1. Learning rate. Default 0.01
    -t <obj type>           Expected a string. If predicted 'sell' or 'buy'. Default 'sell'
    -d <obj id>             Expected a string. Define the predicted object id. Default '24344'"""
            print(help)
            sys.exit()
        elif opt == '-i':
            if arg.isdigit():
                n_iterations = int(arg)
            else:
                print('Error parsing the command arguments. Check -h or --help for more information.')
                sys.exit(2)
        elif opt == '-p':
            if arg.isdigit():
                input_size = int(arg)
            else:
                print('Error parsing the command arguments. Check -h or --help for more information. tete')
                sys.exit(2)
        elif opt == '-n':
            if arg.isdigit():
                hidden_neurons = int(arg)
            else:
                print('Error parsing the command arguments. Check -h or --help for more information.')
                sys.exit(2)
        elif opt == '-d':
            obj_id = arg
        elif opt == '-t':
            obj_type = arg
        elif opt == '-l':
            try:
                lr = float(arg)
                if 0 <= lr <= 1:
                    lr = lr
                else:
                    raise ValueError
            except ValueError:
                print('Error parsing the command arguments. Check -h or --help for more information.')
                sys.exit(2)

    # Initializes a model with sigmoidal activation function
    def model(X, w_o, n_hidden, input_size):
        lstm_cell = rnn_cell.BasicLSTMCell(n_hidden, forget_bias=1.0)
        x = tf.split(0, n_steps, X)
        outputs, _ = rnn.rnn(lstm_cell, x, dtype=tf.float32)

        return tf.matmul(outputs[-1], w_o)

    #Training variables
    trX = []
    trY = []
    #Test variables
    teX = []
    teY = []

    # get data
    proc = Process(int(input_size/2))
    proc.setup_data()

    for instance in proc.get_data(obj_type, 1, obj_id)['train']:
        trX.append(instance['inputs'])
        trY.append(instance['outputs'])

    trX = np.array(proc.get_lstm_data(trX))
    trY = np.array(trY)

    for instance in proc.get_data(obj_type, 1, obj_id)['test']:
        teX.append(instance['inputs'])
        teY.append(instance['outputs'])

    teX = np.array(proc.get_lstm_data(teX))
    teY = np.array(teY)


    X = tf.placeholder("float", [None, int(input_size/n_steps)]) # network input (quantity and price)
    Y = tf.placeholder("float", [None, 1]) # output

    w_o = tf.Variable(tf.random_normal([hidden_neurons, 1]))  # second layer weights [hidden_neurons, output_neurons]

    py_x = model(X, w_o, hidden_neurons, input_size)

    cost = tf.reduce_mean(tf.contrib.losses.mean_squared_error(predictions=py_x, labels=Y)) # cost
    #cost = tf.reduce_mean(tf.nn.l2_loss(py_x)) # cost
    train_op = tf.train.AdamOptimizer(learning_rate=lr).minimize(cost) # optimizer
    predict_op = py_x

    # Launch session
    with tf.Session() as sess:
        # you need to initialize all variables
        tf.global_variables_initializer().run()
        # buy_iterations_
        file_name = "%s_%s_%s_%s_%s_%s.txt" % (time.strftime("%Y%m%d_%H-%M-%S"), obj_type, n_iterations, hidden_neurons, lr, obj_id)
        f = open('experiments/%s' % file_name, 'a')
        f.write('iteration,train_error,test_error\n')

        #Ciclos de entrenamiento
        for i in range(n_iterations):
            sess.run(train_op, feed_dict={X: trX, Y: trY})
            result = "%s, %s, %s\n" % (i, mean_squared_error(trY, sess.run(predict_op, feed_dict={X: trX})),
                                       mean_squared_error(teY, sess.run(predict_op, feed_dict={X: teX})))
            f.write(result)
            print(result)

if __name__ == "__main__":
    main(sys.argv[1:])
