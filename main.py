#from fastapi import FastAPI, File, UploadFile, HTTPException
#from PIL import Image
#import numpy as np
#import io
#from model_loader import load_model
#
#app = FastAPI()
#
## Modeli yükleyin
#model = load_model("C:/Users/edanu/python-apis/fast-api/models/my_model2.h5")
#
#model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#
#@app.post("/predict/")
#async def predict(file: UploadFile = File(...)):
#    try:
#        contents = await file.read()
#        if not contents:
#            raise HTTPException(status_code=400, detail="Dosya yüklenemedi veya boş")
#        
#        if len(contents) < 1000:
#            raise HTTPException(status_code=400, detail="Dosya çok küçük, geçerli bir görüntü olmayabilir")
#        
#        try:
#            image = Image.open(io.BytesIO(contents)).convert("RGB")
#        except Exception as e:
#            raise HTTPException(status_code=400, detail=f"Görüntü işlenemedi: {str(e)}")
#        
#        image = image.resize((224, 224))
#        image = np.array(image) / 255.0
#        image = np.expand_dims(image, axis=0)
#        
#        prediction = model.predict(image)
#        result = "Pneumonia" if prediction[0][0] > 0.7 else "Normal"
#        
#        return {"prediction": result}
#    except HTTPException as e:
#        return {"error": e.detail}
#    except Exception as e:
#        return {"error": str(e)}
#
#@app.get('/api/greet')
#def greet():
#    return {"message": "Hello, fast api!"}
#
#if __name__ == '__main__':
#    import uvicorn
#    uvicorn.run(app, host="localhost", port=8000)

from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import numpy as np
import io
import cv2
from model_loader import load_model
import tempfile
import mimetypes

app = FastAPI()

# Modeli yükleyin
model = load_model("C:/Users/edanu/python-apis/fast-api/models/my_model2.h5")
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Dosya yüklenemedi veya boş")

        # `content_type` kontrolü ve yedekleme
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if not content_type:
            raise HTTPException(status_code=400, detail="Dosya türü belirlenemedi")

        if content_type.startswith('image/'):
            return await predict_image(contents)
        elif content_type.startswith('video/'):
            return await predict_video(contents)
        else:
            raise HTTPException(status_code=400, detail="Dosya türü desteklenmiyor")

    except HTTPException as e:
        return {"error": e.detail}
    except Exception as e:
        return {"error": str(e)}

async def predict_image(contents):
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)
        
        prediction = model.predict(image)
        result = "Pneumonia" if prediction[0][0] > 0.7 else "Normal"
        
        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Görüntü işlenemedi: {str(e)}")

async def predict_video(contents):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(contents)
            temp_video_path = temp_video.name

        cap = cv2.VideoCapture(temp_video_path)
        frame_count = 0
        predictions = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % 30 == 0:
                frame = cv2.resize(frame, (224, 224))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.array(frame) / 255.0
                frame = np.expand_dims(frame, axis=0)
                
                prediction = model.predict(frame)
                predictions.append(prediction[0][0])

            frame_count += 1

        cap.release()
        
        avg_prediction = np.mean(predictions)
        result = "Pneumonia" if avg_prediction > 0.7 else "Normal"
        
        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video işlenemedi: {str(e)}")

@app.get('/api/greet')
def greet():
    return {"message": "Hello, fast api!"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
