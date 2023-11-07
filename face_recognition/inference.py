# uses webcam!!
# simply run this using "python3 inference_test.py"

import time
from collections import Counter
import cv2
from ultralytics import YOLO

model_name = "yolov8l_dataset_v6.pt"

CONF = 0.5  # Confidence threshold
DETECTION_INTERVAL = 3  # Detection interval in seconds
MIN_DETECTIONS = 5  # Minimum number of detections for a person
PERSON_CONF = 0.8  # Minimum confidence for a person

mapping = {0.0: "Artem", 1.0: "Roman"}

from collections import Counter

def determine_person_presence(detected_persons):
    # Flatten the list of lists into a single list of ids
    flat_list = [item for sublist in detected_persons for item in sublist]

    # Count the occurrences of each id
    person_counts = Counter(flat_list)

    # Find the id(s) with the maximum occurrences
    max_count = max(person_counts.values())
    mode_persons = [id for id, count in person_counts.items() if count == max_count]

    # Calculate the percentage of presence for each mode id
    total_frames = len(detected_persons)
    percentages = {person_: (count / total_frames) * 100 for person_, count in person_counts.items() if person_ in mode_persons}

    # Return mode_id and mode_presence
    mode_person = mode_persons[0] if len(mode_persons) == 1 else mode_persons
    mode_presence = percentages[mode_person] if len(mode_persons) == 1 else {person_: percentages[person_] for person_ in mode_persons}

    return mode_person, mode_presence

# load my YOLO model
model = YOLO(f"models/{model_name}")
model.conf = CONF

# using webcam
cap = cv2.VideoCapture(0)
detected_persons = []

start_time = time.time()
person_counts = Counter()

while True:
    
    elapsed_time = time.time() - start_time
    if elapsed_time > DETECTION_INTERVAL and detected_persons and len(detected_persons) > MIN_DETECTIONS: 
        prob_person, part = determine_person_presence(detected_persons)
        if part >= PERSON_CONF: 
            print("\n\n")
            print(f"OH FUCK I SEE {prob_person}!!!!! ")
            print(f"Total faces I detected during last {DETECTION_INTERVAL} seconds: {len(detected_persons)}")
            print(f"I saw {prob_person} on {part}% frames which included faces!")
            print("\n\n")
        # Well, here the business logic should start
        # I mean API calls to ChatGPT, Whisper etc...
        # new interval started
        start_time = time.time()
        detected_persons = []
    ret, frame = cap.read()
    if not ret:
        break

    # object detection
    results = model(frame)

    # Check if detections were made
    if results:
        detected_classes = []

        # Iterate over each detection
        for box in results[0].boxes:
            # Retrieve class and confidence
            cls = box.cls  # class
            conf = box.conf  # confidence score

            # Append to list if confidence is higher than threshold
            if conf > CONF:  # Adjust the threshold if needed
                detected_classes.append(cls)

        # Print the detected class IDs for the current frame
        if detected_classes:
            detected_classes = [mapping[val.item()] for val in detected_classes]
            detected_persons.append(detected_classes)
        print("Detected IDs:", detected_classes)
    
    # Visualizing annotated_frame
    annotated_frame = frame


    cv2.imshow("YOLOv8 Inference", results[0].plot())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(detected_persons)

cap.release()
cv2.destroyAllWindows()



