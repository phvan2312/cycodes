#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cassia import cas_assets
from . import Report


class CasReport(Report):
    def __init__(self):
        super().__init__()
        self.output = cas_assets.get_report_dir()


cas_report = CasReport()
