import tensorflow as tf
import numpy as np
from .process import Process
from sklearn.metrics import mean_squared_error
import time, os

class mlp:

    '''
        type: sell - buy (string)
        id: 19727, 24325, 24292, 24344, 24289 (string)
        input: number of previous instances (int)
        n: number of iterations (int)
        hidden_layer: number of hidden neurons (int)
        learning_rate: learning_rate (int)

        los valores para cada objeto y compra/venta está al final
    '''
    def __init__(self, type, id, input, n, hidden_layer, learning_rate):
        self.n_iterations = n
        self.input_size = input
        self.hidden_neurons = hidden_layer
        self.lr = learning_rate
        self.obj_type = type
        self.obj_id = id
        self.process = None
        self.path=""
        self.X = None
        self.memoria = [[]]
        self.sess = None

        self.train()

    # Initializes weights
    def init_weights(self, shape):
        return tf.Variable(tf.random_normal(shape, stddev=0.01))

    # Initializes a model with sigmoidal activation function
    def model(self, X, w_h, w_o):
        h = tf.nn.sigmoid(tf.matmul(X, w_h))
        return tf.matmul(h, w_o)

    #train de la red
    def train(self):
        #Training variables
        trX = []
        trY = []
        #Test variables
        teX = []
        teY = []

        # get data
        self.process = Process(int(self.input_size/2))
        self.process.setup_data()

        for instance in self.process.get_data(self.obj_type, 1, self.obj_id)['train']:
            trX.append(instance['inputs'])
            trY.append(instance['outputs'])

        trX = np.array(trX)
        trY = np.array(trY)

        for instance in self.process.get_data(self.obj_type, 1, self.obj_id)['test']:
            teX.append(instance['inputs'])
            teY.append(instance['outputs'])

        teX = np.array(teX)
        teY = np.array(teY)


        self.X = tf.placeholder("float", [None, self.input_size], "X") # network input (quantity and price)
        Y = tf.placeholder("float", [None, 1]) # output

        w_h = self.init_weights([self.input_size, self.hidden_neurons])  # first layer weights [input_neurons, hidden_neurons]
        w_o = self.init_weights([self.hidden_neurons, 1])  # second layer weights [hidden_neurons, output_neurons]

        py_x = self.model(self.X, w_h, w_o)

        cost = tf.reduce_mean(tf.contrib.losses.mean_squared_error(predictions=py_x, labels=Y)) # cost
        #cost = tf.reduce_mean(tf.nn.l2_loss(py_x)) # cost
        train_op = tf.train.GradientDescentOptimizer(self.lr).minimize(cost) # optimizer
        self.predict_op = py_x

        # Launch session
        self.sess = tf.InteractiveSession()
        # you need to initialize all variables
        tf.global_variables_initializer().run()

        # buy_iterations_
        #file_name = "%s_%s_%s_%s_%s_%s.txt" % (time.strftime("%Y%m%d_%H-%M-%S"), self.obj_type, self.n_iterations, self.hidden_neurons, self.lr, self.obj_id)
        #f = open('experiments/%s' % file_name, 'a')
        #f.write('iteration,train_error,test_error\n')

        #Ciclos de entrenamiento
        for i in range(self.n_iterations):
            self.sess.run(train_op, feed_dict={self.X: trX, Y: trY})
            #result = "%s, %s, %s\n" % (i, mean_squared_error(trY, sess.run(self.predict_op, feed_dict={self.X: trX})),
            #                           mean_squared_error(teY, sess.run(self.predict_op, feed_dict={self.X: teX})))
            #f.write(result)

        print("Error de %s" % mean_squared_error(teY, self.sess.run(self.predict_op, feed_dict={self.X: teX})))

        file_name = os.path.dirname(os.path.abspath(__file__))+"/modelos/%s_%s_v2model" % (self.obj_type, self.obj_id)
        self.path=tf.train.Saver().save(self.sess, file_name)

        #predicc=sess.run(self.predict_op, feed_dict={self.X: [[10,10,10,10,10,10,10,10,10,10]]})
        #print(self.process.denormalize_value(predicc, self.obj_id, self.obj_type))


    #N indica el número de horas a predecir. Ej: Precio dentro de 3h
    def predict(self, n):

        #Recupera el modelo para compra/venta del objeto
        restore_model = tf.train.import_meta_graph(os.path.dirname(os.path.abspath(__file__))+'/modelos/'+self.obj_type+'_'+self.obj_id+'_v2model.meta')
        restore_model.restore(self.sess, self.path)
        #Se carga el csv, que no cuesta na'
        import csv

        with open(os.path.dirname(os.path.abspath(__file__))+'/data/iao_gw') as csvfile:
            reader = csv.DictReader(csvfile)
            reader = list(reader)

            #hora = time.strptime(reader[len(reader)-1].get('date'), "%d/%m/%Y-%H:%M:%S")
            pos = {'19727': 5,
                    '24325': 4,
                    '24292': 3,
                    '24344': 2,
                    '24289': 1} #Orden inverso
            self.memoria[0].clear()
            #Se cargan los n datos de entrada iniciales
            for i in range(self.input_size):
                self.memoria[0].append(reader[len(reader)-(i*self.process.objects_size+pos[self.obj_id])].get(self.obj_type+'_price'))

        max_val = -float('Inf')
        min_val = float('Inf')

        for i in self.memoria[0]:
            if int(i) > max_val:
                max_val = int(i)
            if int(i) < min_val:
                min_val = int(i)
        for i in range(len(self.memoria[0])):
            self.memoria[0][i] = (int(self.memoria[0][i]) - min_val)/(max_val - min_val)

        predicc = 0
        ciclos = int(n/2) if n%2 == 0 else int(n/2) + 1
        for i in range(ciclos):
            #Se predice el nuevo valor
            predicc = self.sess.run(self.predict_op, feed_dict={self.X: self.memoria})
            #Se elimina el valor más viejo y se introduce el más nuevo
            self.memoria[0].insert(0,predicc[0][0])
            self.memoria[0].pop()

        return self.process.denormalize_value(predicc, self.obj_id, self.obj_type)[0][0]

#init de la red al construirla
def init(self):
    self.train(self.obj_type, self.obj_id, self.input_size, \
                self.n_iterations, self.hidden_neurons, self.lr)

#Aqui la creación de las clases
    #mlp('buy', '19727', 12, 700, 15, 0.01)
    #mlp('buy', '24325', 12, 700, 15, 0.01)
    #mlp('buy', '24292', 12, 700, 10, 0.01)
    #mlp('buy', '24344', 12, 500, 20, 0.015)
    #mlp('buy', '24289', 12, 700, 15, 0.1)

    #mlp('sell', '19727', 12, 1000, 12, 0.01)
    #mlp('sell', '24325', 12, 700, 20, 0.01)
    #mlp('sell', '24292', 12, 700, 15, 0.01)
    #mlp('sell', '24344', 12, 600, 12, 0.015)
    #mlp('sell', '24289', 12, 700, 15, 0.02)