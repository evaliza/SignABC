import cv2 as cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import mediapipe as mp
from tensorflow.keras.models import load_model, save_model


pathFolder = "C:/pco/asl/data/"
#creating a list of lables "You could add as many you want"
Labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
          "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
boucle = False
for folder in Labels:
    vid = cv2.VideoCapture(0)
    count = 0
    if boucle == False:
        print("lettre :", folder)
        
        while count<200:
            status, frame = vid.read()

            
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            mp_hands = mp.solutions.hands

            ########################################################################"
            target_size = (224, 224)
            # Background image to draw hand landmarks on
            # create a black image
            img = np.zeros((224, 224, 3), dtype=np.uint8)

            # background_img = cv2.imread("mod_background_black.jpg")
            background_img = img
            ######################################################################""

            #############################################################################
            # Empty background image
            #background_img = cv2.resize(background_img.copy(), target_size)
            ###########################################################################"
            with mp_hands.Hands(
                    model_complexity=0,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5) as hands:

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                # self.image.flags.writeable = True
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(image)

                # Draw the hand annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    annotated_image = cv2.resize(background_img.copy(), target_size)
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            annotated_image,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
                            #mp_drawing.DrawingSpec(thickness=2, circle_radius=2))


                        ################################################################################
                        # Save the processed image
                        landmarks = folder + str(count) + ".jpg"
                        l = pathFolder + folder +"/" + landmarks
                        print(l)
                        cv2.imwrite(l, cv2.flip(annotated_image, 1))
                        count = count +1
                        

           #convert the image into gray format for fast caculation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #display window with gray image
            cv2.imshow("Video Window",gray)
            
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # After the loop release the cap object
        vid.release()
        # Destroy all the windows
        cv2.destroyAllWindows()
        
        input("Press Enter to continue...")
        if folder == "Z":
            boucle=True

