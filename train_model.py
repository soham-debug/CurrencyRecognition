import cv2
import os
import torch
from PIL import Image
from io import BytesIO
import pickle

one = [ "", "one ", "two ", "three ", "four ",
        "five ", "six ", "seven ", "eight ",
        "nine ", "ten ", "eleven ", "twelve ",
        "thirteen ", "fourteen ", "fifteen ",
        "sixteen ", "seventeen ", "eighteen ",
        "nineteen "]
 
ten = [ "", "", "twenty ", "thirty ", "forty ",
        "fifty ", "sixty ", "seventy ", "eighty ",
        "ninety "]

class CurrencyNotesDetection:
    """
    Class implements Yolo5 model to make inferences on a source provided/youtube video using Opencv2.
    """

    def __init__(self, model_name):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        self.model = self.load_model(model_name)
        # similar to coco.names contains ['10Rupees','20Rupees',...]
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def load_model(self, model_name):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Customed Trained Pytorch model.
        """
        # Custom Model
        # model = torch.hub.load('ultralytics/yolov5', 'custom', path='path/to/best.pt',force_reload=True)  # default
        # model = torch.hub.load('ultralytics/yolov5','custom', path=model_name, force_reload=True, device='cpu')
        model = torch.hub.load('./yolov5', 'custom', path=model_name, source='local')  # local repo
        
        # Yolo Model from Web
        # for file/URI/PIL/cv2/np inputs and NMS
        # model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

        return model

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def numToWords(self,n, s):
 
        str = ""
        
        # if n is more than 19, divide it
        if (n > 19):
            str += ten[n // 10] + one[n % 10]
        else:
            str += one[n]
    
        # if n is non-zero
        if(n != 0):
            str += s
    
        return str

    def convertToWords(self,n):
        # stores word representation of given
        # number n
        out = ""

        # handles digits at ten millions and
        # hundred millions places (if any)
        out += self.numToWords((n // 10000000),"crore ")

        # handles digits at hundred thousands
        # and one millions places (if any)
        out += self.numToWords(((n // 100000) % 100),"lakh ")

        # handles digits at thousands and tens
        # thousands places (if any)
        out += self.numToWords(((n // 1000) % 100),"thousand ")

        # handles digit at hundreds places (if any)
        out += self.numToWords(((n // 100) % 10),"hundred ")

        if (n > 100 and n % 100):
            out += "and "

        # handles digits at ones and tens
        # places (if any)
        out += self.numToWords((n % 100), "")

        return out

    def get_text(self,labelCnt):
        text = "Image contains"
        noOfLabels,counter = len(labelCnt),0
        for k,v in labelCnt.items():
            text += " {}{} {} ".format(self.convertToWords(v),k,"Notes" if v>1 else "Note")
            if(counter != noOfLabels-1):
                text += 'and'
            counter += 1

        return text


    def get_detected_image(self,img):
        # Images
        imgs = [img]  # batched list of images

        # Inference
        results = self.model(imgs, size=416)  # includes NMS

        # Results
        # results.print()  # print results to screen
        # results.show()  # display results
        # results.save()  # save as results1.jpg, results2.jpg... etc. in runs directory
        # print(results)  # models.common.Detections object, used for debugging

        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        n = len(labels)
        labelCnt = {}
        for i in range(n):
            classLabel = self.classes[int(labels[i])]
            row = cord[i]
            # row[4] is conf score
            print("{} is detected with {} probability.".format(classLabel, row[4]))
            if classLabel in labelCnt:
                labelCnt[classLabel] += 1
            else:
                labelCnt[classLabel] = 1

        text = self.get_text(labelCnt)
        
        # Transform images with predictions from numpy arrays to base64 encoded images
        # array of original images (as np array) passed to model for inference
        results.imgs
        results.render()  # updates results.imgs with boxes and labels, returns nothing
        
        return results.imgs[0],text


def train():
    model = CurrencyNotesDetection(
        model_name='./yolov5/runs/train/exp/weights/best.pt'
    )
    with open('model.pkl','wb') as io:
        pickle.dump(model, io)

if __name__ == '__main__':
    train()