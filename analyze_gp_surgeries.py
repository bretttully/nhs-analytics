#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: brett
"""
import os
import pandas as pd


surgeries_fname = os.path.join('data', 'gp_surgeries.csv')
surgeries = pd.read_csv(surgeries_fname)
print surgeries.columns

trusts_fname = os.path.join('data', 'nhs_trusts.csv')
trusts = pd.read_csv(trusts_fname)
print trusts.columns

n = 10
top_trust_codes = surgeries.trust_code.value_counts().head(n)
top_surgeries = surgeries[surgeries.trust_code.isin(top_trust_codes.index)]
top_trusts = trusts[trusts.code.isin(top_trust_codes.index)]
top = pd.merge(top_surgeries, top_trusts, left_on='trust_code',
                  right_on='code', how='left').groupby('name_y')
print "The top prescribing trusts are:", top.mean()
top.mean().T.plot()
