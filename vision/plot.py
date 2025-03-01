import matplotlib.pyplot as plt
from class_map import get_class_mapping
import numpy as np
from processing import extract_pred
from ultralytics import YOLO

def plot(model):
    results = model(r'G:\Coding\Backend-fastapi\vision\test4.jpeg')

    names = model.names
    classes = []

    for r in results:
        for c in r.boxes.cls:
            print(names[int(c)])
            classes.append(names[int(c)])

    data = np.array(results[0].boxes.xyxyn)

    # Plotting each bounding box with class name
    for i in range(len(data)):
        x1, y1, x2, y2 = data[i, :4]
        class_label = names[int(classes[i])]
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, edgecolor='r', facecolor='none'))
        c = get_class_mapping(int(class_label))
        plt.text(x1, y1, c, color='r')
        
    # Adding legend and labels
    plt.gca().invert_yaxis()
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Bounding boxes with class names')

    # Show plot
    plt.axis('image')  # Set aspect ratio to be equal
    plt.show()

if __name__ == "__main__":
    model_path = r'G:\Coding\Backend-fastapi\models\120epoch.pt'
    model = YOLO(model_path)
    plot(model)