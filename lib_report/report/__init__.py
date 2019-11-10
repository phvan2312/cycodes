#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .g_report import GReport
from .i_report import IReport

__version__ = '0.1.0'
__author__ = 'Andrew'


class Report(object):
    output = ''

    def g_report(self, is_appending_date=True, is_appending_img=True, output_dir=None):
        if output_dir is None:
            output_dir = self.output
        return GReport(output_dir, is_appending_date, is_appending_img)

    def i_report(self, is_appending_date=True, is_appending_img=True, output_dir=None):
        if output_dir is None:
            output_dir = self.output
        return IReport(output_dir, is_appending_date, is_appending_img)
