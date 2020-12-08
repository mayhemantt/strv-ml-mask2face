from tensorflow.keras.layers import *
from tensorflow.keras.models import Model

class UNet_segmentation:
    """ UNet architecture from following github notebook for image segmentation:
        https://github.com/nikhilroxtomar/UNet-Segmentation-in-Keras-TensorFlow/blob/master/unet-segmentation.ipynb
        
        1 963 043 parameters
    """
    
    def __init__(self, input_size=(256, 256, 3)):
        f = [16, 32, 64, 128, 256]
        inputs = Input(input_size)

        p0 = inputs
        c1, p1 = UNet_segmentation.down_block(p0, f[0]) #128 -> 64
        c2, p2 = UNet_segmentation.down_block(p1, f[1]) #64 -> 32
        c3, p3 = UNet_segmentation.down_block(p2, f[2]) #32 -> 16
        c4, p4 = UNet_segmentation.down_block(p3, f[3]) #16->8

        bn = UNet_segmentation.bottleneck(p4, f[4])

        u1 = UNet_segmentation.up_block(bn, c4, f[3]) #8 -> 16
        u2 = UNet_segmentation.up_block(u1, c3, f[2]) #16 -> 32
        u3 = UNet_segmentation.up_block(u2, c2, f[1]) #32 -> 64
        u4 = UNet_segmentation.up_block(u3, c1, f[0]) #64 -> 128

        outputs = Conv2D(3, (1, 1), padding="same", activation="sigmoid")(u4)
        self.model = Model(inputs, outputs)
    
    @staticmethod
    def down_block(x, filters, kernel_size=(3, 3), padding="same", strides=1):
        c = Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(x)
        c = Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(c)
        p = MaxPool2D((2, 2), (2, 2))(c)
        return c, p

    @staticmethod
    def up_block(x, skip, filters, kernel_size=(3, 3), padding="same", strides=1):
        us = UpSampling2D((2, 2))(x)
        concat = Concatenate()([us, skip])
        c = Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(concat)
        c = Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(c)
        return c

    @staticmethod
    def bottleneck(x, filters, kernel_size=(3, 3), padding="same", strides=1):
        c = Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(x)
        c = Conv2D(filters, kernel_size, padding=padding, strides=strides, activation="relu")(c)
        return c

    def get_model(self):
        return self.model

class UNet_polyp():
    """ Model from polyp segmentation github
        https://github.com/nikhilroxtomar/Polyp-Segmentation-using-UNET-in-TensorFlow-2.0
        
        414 435 parameters
    """
    
    def __init__(self, input_size=(256, 256, 3)):
        num_filters = [16, 32, 48, 64]
        inputs = Input(input_size)

        skip_x = []
        x = inputs
        
        ## Encoder
        for f in num_filters:
            x = UNet_polyp.conv_block(x, f)
            skip_x.append(x)
            x = MaxPool2D((2, 2))(x)

        ## Bridge
        x = UNet_polyp.conv_block(x, num_filters[-1])

        num_filters.reverse()
        skip_x.reverse()
        ## Decoder
        for i, f in enumerate(num_filters):
            x = UpSampling2D((2, 2))(x)
            xs = skip_x[i]
            x = Concatenate()([x, xs])
            x = UNet_polyp.conv_block(x, f)

        ## Output
        x = Conv2D(3, (1, 1), padding="same")(x)
        x = Activation("sigmoid")(x)

        self.model = Model(inputs, x)
    
    @staticmethod
    def conv_block(x, num_filters):
        x = Conv2D(num_filters, (3, 3), padding="same")(x)
        x = BatchNormalization()(x)
        x = Activation("relu")(x)

        x = Conv2D(num_filters, (3, 3), padding="same")(x)
        x = BatchNormalization()(x)
        x = Activation("relu")(x)
        return x
    
    def get_model(self):
        return self.model