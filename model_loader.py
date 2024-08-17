
import tensorflow as tf

def load_model(model_path):
    
    model = tf.keras.models.load_model('C:/Users/edanu/python-apis/fast-api/models/my_model2.h5')
    return model
