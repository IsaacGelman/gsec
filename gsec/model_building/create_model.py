# create_model.py: driver file to train and save model
#
# Authors: Nicolas Perez, Isaac Gelman, Natalie Abreu, Shannon Brownlee,
# Tomas Angelini, Laura Cao, Shreya Havaldar
#
# This software is Copyright (C) 2020 The University of Southern
# California. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted,
# provided that the above copyright notice, this paragraph and the
# following three paragraphs appear in all copies.
#
# Permission to make commercial use of this software may be obtained
# by contacting:
#
# USC Stevens Center for Innovation
# University of Southern California
# 1150 S. Olive Street, Suite 2300
# Los Angeles, CA 90115, USA
#
# This software program and documentation are copyrighted by The
# University of Southern California. The software program and
# documentation are supplied "as is", without any accompanying
# services from USC. USC does not warrant that the operation of the
# program will be uninterrupted or error-free. The end-user
# understands that the program was developed for research purposes and
# is advised not to rely exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF SOUTHERN CALIFORNIA BE LIABLE TO
# ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
# CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE
# USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY
# OF SOUTHERN CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE. THE UNIVERSITY OF SOUTHERN CALIFORNIA SPECIFICALLY DISCLAIMS
# ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE. THE SOFTWARE PROVIDED

#!/usr/bin/env python3

from .ModelRunner import ModelRunner
import os

# function for creating and saving model
def create_model(df, maxk, id):

    # dropping nulls
    df.dropna(inplace=True)

    # file names and paths
    ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    file_name = str(id) + '.pkl'
    models_dir = os.path.join(ROOT, "models")
    file_dir = os.path.join(models_dir, file_name)

    # if models folder doesn't exist, create it
    if not os.path.exists(models_dir):
        os.mkdir(models_dir)

    # create Model class
    runner = ModelRunner(df)

    # try different models

    # log-reg
    runner.log_reg()

    # knn
    runner.knn()

    # gauss nb
    runner.gnb()

    # random forest
    runner.rf()

    # ensemble
    # runner.ensemble()

    # lasso
    # runner.lasso()

    # get best model
    best, acc = runner.get_best_model()

    # save model
    runner.save_model(best, file_dir)

    return 0
