# cycodes
Reading OCR Tool for Nancy

# Running
For running OCR (Cannet and Lucas OCR) with given json folder (for splitting region), and image folder, run the following command:
```bash
python run.py -use_lucas -use_cannet -input_image "your_input_image_folder" -input_json_folder "your_input_json_folder"
```
# Example
For example, given:
- "your_input_image_folder": "/home/vanph/Desktop/for_nancy/train_json&img_55files/images"
- "your_input_json_folder": "/home/vanph/Desktop/for_nancy/train_json&img_55files/jsons"

Then, run the specified command:
```bash
python run.py -use_lucas -use_cannet -input_image "/home/vanph/Desktop/for_nancy/train_json&img_55files/images" -input_json_folder "/home/vanph/Desktop/for_nancy/train_json&img_55files/jsons"
```
