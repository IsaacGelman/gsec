from .ModelRunner import ModelRunner


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
    runner.ensemble()

    # lasso
    runner.lasso()

    # get best model
    best, acc = runner.get_best_model()

    # save model
    runner.save_model(best, file_dir)

    return 0
