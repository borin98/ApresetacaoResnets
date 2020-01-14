from keras.layers import Input, Add, Dense, Activation, ZeroPadding2D, BatchNormalization, Flatten, Conv2D, AveragePooling2D, MaxPooling2D
from keras.models import Model
from keras.initializers import glorot_uniform

def resNet50(input_shape=(64, 64, 3), classes=6, funcActivation = "relu", kernelActivation = glorot_uniform(seed=0)):

    # Define the input as a tensor with shape input_shape
    X_input = Input(input_shape)

    # Zero-Padding
    X = ZeroPadding2D((3, 3))(X_input)

    # Stage 1
    X = Conv2D(64, (7, 7), strides=(2, 2), name='conv1', kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name='bn_conv1')(X)
    X = Activation(funcActivation)(X)
    X = MaxPooling2D((3, 3), strides=(2, 2))(X)

    # Stage 2
    X = _convolutional_block(X, f=3, filters=[64, 64, 256], stage=2, block='a', s=1, funcActivation = funcActivation)
    X = _identity_block(X, 3, [64, 64, 256], stage=2, block='b', funcActivation = funcActivation)
    X = _identity_block(X, 3, [64, 64, 256], stage=2, block='c', funcActivation = funcActivation)

    # Stage 3
    X = _convolutional_block(X, f=3, filters=[128, 128, 512], stage=3, block='a', s=2, funcActivation = funcActivation)
    X = _identity_block(X, 3, [128, 128, 512], stage=3, block='b', funcActivation = funcActivation)
    X = _identity_block(X, 3, [128, 128, 512], stage=3, block='c', funcActivation = funcActivation)
    X = _identity_block(X, 3, [128, 128, 512], stage=3, block='d', funcActivation = funcActivation)

    # Stage 4
    X = _convolutional_block(X, f=3, filters=[256, 256, 1024], stage=4, block='a', s=2, funcActivation = funcActivation)
    X = _identity_block(X, 3, [256, 256, 1024], stage=4, block='b', funcActivation = funcActivation)
    X = _identity_block(X, 3, [256, 256, 1024], stage=4, block='c', funcActivation = funcActivation)
    X = _identity_block(X, 3, [256, 256, 1024], stage=4, block='d', funcActivation = funcActivation)
    X = _identity_block(X, 3, [256, 256, 1024], stage=4, block='e', funcActivation = funcActivation)
    X = _identity_block(X, 3, [256, 256, 1024], stage=4, block='f', funcActivation = funcActivation)

    # Stage 5
    X = _convolutional_block(X, f=3, filters=[512, 512, 2048], stage=5, block='a', s=2, funcActivation = funcActivation)
    X = _identity_block(X, 3, [512, 512, 2048], stage=5, block='b', funcActivation = funcActivation)
    X = _identity_block(X, 3, [512, 512, 2048], stage=5, block='c', funcActivation = funcActivation)

    # AVGPOOL
    X = AveragePooling2D(pool_size=(2, 2), padding='same')(X)

    # Output layer
    X = Flatten()(X)
    X = Dense(classes, activation='softmax', name='fc' + str(classes), kernel_initializer = kernelActivation)(X)

    # Create model
    model = Model(inputs=X_input, outputs=X, name='ResNet50')

    return model

def _identity_block(X, f, filters, stage, block, funcActivation = "relu", kernelActivation = glorot_uniform(seed=0)):
    # Defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    # Retrieve Filters
    F1, F2, F3 = filters

    # Save the input value
    X_shortcut = X

    # First component of main path
    X = Conv2D(filters=F1, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2a',
                   kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2a')(X)
    X = Activation(funcActivation)(X)

    # Second component of main path
    X = Conv2D(filters=F2, kernel_size=(f, f), strides=(1, 1), padding='same', name=conv_name_base + '2b',
                   kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2b')(X)
    X = Activation(funcActivation)(X)

    # Third component of main path
    X = Conv2D(filters=F3, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2c',
                   kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2c')(X)

    # Final step: Add shortcut value to main path, and pass it through a RELU funcActivation
    X = Add()([X, X_shortcut])
    X = Activation(funcActivation)(X)

    return X

def _convolutional_block(X, f, filters, stage, block, s=2, funcActivation = "relu", kernelActivation = glorot_uniform(seed=0)):

    # Defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

     # Retrieve Filters
    F1, F2, F3 = filters

    # Save the input value
    X_shortcut = X

    ##### MAIN PATH #####
    # First component of main path
    X = Conv2D(filters=F1, kernel_size=(1, 1), strides=(s, s), padding='valid', name=conv_name_base + '2a',
                   kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2a')(X)
    X = Activation(funcActivation)(X)

    # Second component of main path
    X = Conv2D(filters=F2, kernel_size=(f, f), strides=(1, 1), padding='same', name=conv_name_base + '2b',
                   kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2b')(X)
    X = Activation(funcActivation)(X)

    # Third component of main path
    X = Conv2D(filters=F3, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2c',
                   kernel_initializer = kernelActivation)(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2c')(X)

    ##### SHORTCUT PATH ####
    X_shortcut = Conv2D(filters=F3, kernel_size=(1, 1), strides=(s, s), padding='valid', name=conv_name_base + '1',
                            kernel_initializer = kernelActivation)(X_shortcut)
    X_shortcut = BatchNormalization(axis=3, name=bn_name_base + '1')(X_shortcut)

    # Final step: Add shortcut value to main path, and pass it through a RELU funcActivation
    X = Add()([X, X_shortcut])
    X = Activation(funcActivation)(X)

    return X