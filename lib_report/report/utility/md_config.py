#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Andrew <hieu@cinnamon.is>"
import os
import json
import glob
from shutil import copyfile


class MdPath(dict):
    def __init__(self, model_root=None, config_root=None, data_root=None):
        """
        :param model_root: path of model dict
        :param config_root: path of config dict
        :param data_root: path od data dict
        """
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if model_root is not None:
            self.model_root = model_root
        else:
            self.model_root = self.root_dir

        if config_root is not None:
            self.config_root = config_root
        else:
            self.config_root = self.root_dir

        if data_root is not None:
            self.data_root = data_root
        else:
            self.data_root = self.root_dir

    @staticmethod
    def ensure_dir(directory):
        """
        Make dir if it not exist
        :param directory:
        :return:
        """
        if directory is not None:
            if not os.path.exists(directory):
                os.makedirs(directory)

    @staticmethod
    def get_file_path(root_dir, file_path):
        file_path = os.path.join(root_dir, file_path)
        return file_path

    def make_structure(self, source):
        if type(source) is str:
            self.ensure_dir(source)
        elif type(source) is list:
            for s in source:
                self.ensure_dir(s)

    def get_full_path(self, i_path: str, i_type='R'):
        """
        :param variable_name:
        :param v_type:
                'O': original,
                'R': root path,
                'C': config path,
                'M': model path,
                'D': data path
        :return:
        """
        if i_path is not None:
            if isinstance(i_path, str):
                if i_type.upper() == 'R':
                    i_path = self.get_root_path(i_path)
                elif i_type.upper() == 'C':
                    i_path = self.get_config_path(i_path)
                elif i_type.upper() == 'M':
                    i_path = self.get_model_path(i_path)
                elif i_type.upper() == 'D':
                    i_path = self.get_data_path(i_path)
            elif isinstance(i_path, list):
                for idx, i_p in enumerate(i_path):
                    i_path[idx] = self.get_full_path(i_p, i_type)

            return i_path

    def get_root_path(self, file_path):
        file_path = self.get_file_path(self.root_dir, file_path)
        self.ensure_dir(os.path.dirname(file_path))
        return file_path

    def get_model_path(self, file_path):
        file_path = self.get_file_path(self.model_root, file_path)
        self.ensure_dir(file_path)
        return file_path

    def get_config_path(self, file_path):
        file_path = self.get_file_path(self.config_root, file_path)
        self.ensure_dir(file_path)
        return file_path

    def get_data_path(self, file_path):
        file_path = self.get_file_path(self.data_root, file_path)
        self.ensure_dir(file_path)
        return file_path

    def scan_files(self, input_dir, extentions='*.jpg'):
        files = glob.glob(os.path.join(input_dir, extentions))
        return files


class MdConfig(MdPath):
    """
        Class that loads hyperparameters from json file into attributes
    """

    def __init__(self, source, model_root=None, config_root=None, data_root=None):
        super(MdConfig, self).__init__(model_root, config_root, data_root)
        """
        Args:
            source: path to json file or dict
        """
        self.source = source

        if type(source) is dict:
            self.__dict__.update(source)
        elif type(source) is list:
            for s in source:
                self.load_json(s)
        else:
            self.load_json(source)

    def load_json(self, source):
        if self.root_dir is not None:
            source = self.get_config_path(source)

        data = self.json_read(source)
        self.__dict__.update(data)

    def json_read(self, file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)

        return data

    def save(self, dir_name):
        # self.ensure_dir(dir_name)
        if type(self.source) is list:
            for s in self.source:
                c = MdConfig(s)
                c.save(dir_name)
        elif type(self.source) is dict:
            json.dumps(self.source, indent=4)
        else:
            source = self.get_root_path(self.source)
            copyfile(source, self.get_file_path(dir_name, self.export_name))

    def get(self, variable_name: str, default=None):
        if variable_name is not None:
            variable_names = variable_name.split('.')
            result = self.__dict__
            for var_name in variable_names:
                if isinstance(result, dict):
                    result = result.get(var_name)

            return result

    def get_path(self, variable_name, v_type='R'):
        """
        :param variable_name:
        :param v_type:
                'O': original,
                'R': root path,
                'C': config path,
                'M': model path,
                'D': data path
        :return:
        """
        val = self.get(variable_name)
        val = self.get_full_path(val, v_type)

        return val

    def get_files(self, variable_name, extentions='*.*', v_type='D'):
        input_dir = self.get_path(variable_name, v_type)
        return self.scan_files(input_dir, extentions)

    @property
    def dict_json(self):
        print(json.dumps(self.__dict__, indent=4))

    @staticmethod
    def show_json(json_data):
        print(json.dumps(json_data, indent=4))
