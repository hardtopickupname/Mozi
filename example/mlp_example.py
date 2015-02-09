import os

import theano
import theano.tensor as T
import numpy as np

from pynet.model import MLP
from pynet.layer import *
from pynet.learning_rule import LearningRule
from pynet.log import Log
from pynet.train_object import TrainObject
from pynet.cost import Cost
from pynet.datasets.preprocessor import *
from pynet.learning_method import SGD

def setenv():
    NNdir = os.path.dirname(os.path.realpath(__file__))
    NNdir = os.path.dirname(NNdir)

    if not os.getenv('PYNET_DATA_PATH'):
        os.environ['PYNET_DATA_PATH'] = NNdir + '/data'

    if not os.getenv('PYNET_DATABASE_PATH'):
        os.environ['PYNET_DATABASE_PATH'] = NNdir + '/database'

    if not os.getenv('PYNET_SAVE_PATH'):
        os.environ['PYNET_SAVE_PATH'] = NNdir + '/save'

    print('PYNET_DATA_PATH = ' + os.environ['PYNET_DATA_PATH'])
    print('PYNET_SAVE_PATH = ' + os.environ['PYNET_SAVE_PATH'])
    print('PYNET_DATABASE_PATH = ' + os.environ['PYNET_DATABASE_PATH'])


def mlp():

    # build dataset
    data = Mnist(preprocessor=None, train_valid_test_ratio=[5,1,1])

    # build mlp
    mlp = MLP(input_dim = data.feature_size())
    mlp.add_layer(Sigmoid(dim=1000, name='h1_layer', W=None, b=None, dropout_below=None))
    mlp.add_layer(Softmax(dim=data.target_size(), name='output_layer', W=None, b=None, dropout_below=None))

    # build learning method
    learning_method = SGD(learning_rate=0.1, momentum=0.9)

    # set the learning rules
    learning_rule = LearningRule(max_col_norm = 10,
                                L1_lambda = None,
                                L2_lambda = None,
                                training_cost = Cost(type='mse'),
                                learning_rate_decay_factor = None,
                                stopping_criteria = {'max_epoch' : 300,
                                                      'epoch_look_back' : 10,
                                                      'cost' : Cost(type='error'),
                                                      'percent_decrease' : 0.01}
                                )

    # (optional) build the logging object
    log = Log(experiment_name = 'mnist_example',
              description = 'This is tutorial example',
              save_outputs = False,
              save_learning_rule = False,
              save_model = False,
              save_epoch_error = False,
              save_to_database = {'name': 'Example.db',
                                  'records' : {'Dataset' : data.__class__.__name__,
                                  'max_col_norm'     : learning_rule.max_col_norm,
                                  'Weight_Init_Seed' : mlp.rand_seed,
                                  'Dropout_Below'    : str([layer.dropout_below for layer in mlp.layers]),
                                  'Batch_Size'       : data.batch_size,
                                  'Layer_Dim'        : str([layer.dim for layer in mlp.layers]),
                                  'Layer_Types'      : str([layer.__class__.__name__ for layer in mlp.layers]),
                                  'Preprocessor'     : data.preprocessor.__class__.__name__,
                                  'Learning_Rate'    : learning_method.learning_rate,
                                  'Momentum'         : learning_method.momentum,
                                  'Training_Cost'    : learning_rule.cost.type,
                                  'Stopping_Cost'    : learning_rule.stopping_criteria['cost'].type}}
              ) # end log

    # put everything into the train object
    train_object = TrainObject(model = mlp,
                               dataset = data,
                               learning_rule = learning_rule,
                               learning_method = learning_method
                               log = log)
    # finally run the code
    train_object.run()

if __name__ == '__main__':
    setenv()
    mlp()
