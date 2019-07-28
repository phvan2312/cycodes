import os

class OcrWrapper:
    def __init__(self, src_model_path):
        self.models = {}
        self.accpeted_models = ['onmt', 'kush', 'anson', 'pika', 'cannet', 'lucas']
        self.src_model_path = src_model_path

    def import_model(self, model_name, model_weight_fn):
        if self.check_model_name(model_name):
            if model_name == 'onmt':
                from ocr import OnmtOCR

                return OnmtOCR(model_weight_fn)

            elif model_name == 'kush':
                from ocr import KushOCR

                return KushOCR(model_weight_fn)

            elif model_name == 'anson':
                from ocr import AnsonOCR

                return AnsonOCR(model_weight_fn)

            elif model_name == 'pika':
                from ocr import PikaOCR

                return PikaOCR(model_weight_fn)

            elif model_name == 'cannet':
                from ocr import CannetOCR

                return CannetOCR(model_weight_fn)

            elif model_name == 'kizd':
                from ocr import KizdOCR

                return KizdOCR(model_weight_fn)

            elif model_name == 'lucas':
                from ocr import LucasOCR

                return LucasOCR(model_weight_fn)
        else:
            print ("%s not found" % model_name)

            return None

    def check_model_name(self, model_name):
        return model_name in self.accpeted_models

    def add_ocr_model(self, model_name, model_weight_path):
        model_weight_path = os.path.join(self.src_model_path, model_weight_path)
        model = self.import_model(model_name, model_weight_path)

        if model is not None:
            self.models[model_name] = model
            print ("adding model %s with weight from %s successfully..." % (model_name, model_weight_path))

    def predict(self, _input):
        dct_result = {}
        for model_name, model in self.models.items():
            dct_result[model_name] = model.process(_input)['text']

        return dct_result

    def predict_folder(self, _input_folder):
        dct_results = {}
        for fn in os.listdir(_input_folder):
            full_input_path = os.path.join(_input_folder, fn)
            dct_results[full_input_path] = self.predict(full_input_path)

        return dct_results


if __name__ == "__main__":
    pass