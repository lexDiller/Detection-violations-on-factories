import time
import shutil
from PIL import Image
from datetime import datetime
from threading import Thread
import cv2
import schedule
from ultralytics import YOLO
from load_rtsp import LoadStreams
from config import *
from tools import send_mail_moroz, clear_folder
import numpy as np

class YOLOModel:
    def __init__(self, weights: str):
        self.model = YOLO(weights)
        self.class_names = self.model.names
    def run_model(self):
        print('Model start')
        # Get class names
        class_names = self.class_names

        # Load the rtsp link
        dataset = LoadStreams(cam_rtsp2, imgsz=1280)

        # Initialize last screenshot times  (TEMP)
        last_screenshot_time = 0
        last_screenshot_time_1 = 0

        # Обработка набора данных
        for cam_name, path, im, im0s, _ in dataset:
            predict = self.model(im, conf=0.70, classes=predict_classes, verbose=False, imgsz=1280)

            # Iterate over predictions
            for idx, results in enumerate(predict):
                # Make the plot
                annotated_frame = predict[int(idx)].plot(line_width=2, masks=False)

                # Process results
                for result in results.boxes:
                    x1, y1, x2, y2 = result.xyxy[0].tolist()
                    probability_ = round((result.conf[0].tolist()), 2)
                    class_found = class_names[int(result.cls)]

                    # Check the class and probability
                    if class_found == 'no_sleeves' and probability_ > 0.78:
                        current_time = time.time()

                        if current_time - last_screenshot_time >= 120:
                            last_screenshot_time = current_time
                            im = Image.fromarray(annotated_frame[..., ::-1])
                            date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            name_screen_save = f'{probability_}_{cam_name[idx]}_{class_found}_{date_and_time}.jpg'
                            im.save(folder_save_result + name_screen_save)

                    elif class_found == 'no_helmet' and probability_ > 0.87:

                        # Get roi and get hsv, but this is cockblock
                        roi = annotated_frame[int(y1):int(y2), int(x1):int(x2)]
                        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                        # h_mean = np.mean(hsv_roi[:, :, 0])
                        # s_mean = np.mean(hsv_roi[:, :, 1])
                        v_mean = np.mean(hsv_roi[:, :, 2])
                        if v_mean < 125:
                            current_time = time.time()
                            if current_time - last_screenshot_time_1 >= 120:
                                last_screenshot_time_1 = current_time
                                im = Image.fromarray(annotated_frame[..., ::-1])
                                date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                name_screen_save = f'{probability_}_{cam_name[idx]}_{class_found}_{date_and_time}.jpg'
                                im.save(folder_save_result + name_screen_save)

                # Create a named window and display the image
                cv2.namedWindow(f"morozovka {cam_name[int(idx)]}", cv2.WINDOW_NORMAL)
                cv2.imshow(f"morozovka {cam_name[int(idx)]}", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

class EmailSender:
    def __init__(self):
        pass

    def send_mail(self):
        print('Schedule start')

        # Daily task for sending mail
        def daily_task():
            date = datetime.now().strftime("%m-%d")
            path = '/home/user/PycharmProjects/mrz/runs/' + date
            shutil.make_archive(path, 'zip', folder_save_result)
            send_mail_moroz(path + '.zip', date + '.zip')
            print("sent")
            # Clear the folder
            clear_folder(folder_save_result)
            print('folder cleared')

        # Schedule the daily task
        schedule.every().day.at("08:50").do(daily_task)

        # Run the schedule
        while True:
            schedule.run_pending()
            time.sleep(1)

# Create and start threads

if __name__ == "__main__":
    model_runner = YOLOModel(weihts_yolo)
    email_sender = EmailSender()

    thread_model = Thread(target=model_runner.run_model)
    thread_schedule = Thread(target=email_sender.send_mail)

    thread_model.start()
    thread_schedule.start()
