import init
import pandas
from colored import fg, attr
from comet_ml import Experiment
from datetime import datetime
from pprint import pprint
import scipy.sparse
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.externals import joblib
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC


class ItemSelector(BaseEstimator, TransformerMixin):
    """For data grouped by feature, select subset of data at a provided key.

    The data is expected to be stored in a 2D data structure, where the first
    index is over features and the second is over samples.  i.e.

    >> len(data[key]) == n_samples

    Please note that this is the opposite convention to scikit-learn feature
    matrixes (where the first index corresponds to sample).

    ItemSelector only requires that the collection implement getitem
    (data[key]).  Examples include: a dict of lists, 2D numpy array, Pandas
    DataFrame, numpy record array, etc.

    >> data = {'a': [1, 5, 2, 5, 2, 8],
               'b': [9, 4, 1, 4, 1, 3]}
    >> ds = ItemSelector(key='a')
    >> data['a'] == ds.transform(data)

    ItemSelector is not designed to handle data grouped by sample.  (e.g. a
    list of dicts).  If your data is structured this way, consider a
    transformer along the lines of `sklearn.feature_extraction.DictVectorizer`.

    Parameters
    ----------
    key : hashable, required
        The key corresponding to the desired value in a mappable.
    """
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data):
        pprint(self.key)
        pprint(data[self.key])
        return data[self.key]


def predict(train, test, model):
    """Train classifier and predict results
        :param train:
        :param test:
        :param model:
    """
    pipeline = Pipeline([
        ('union', FeatureUnion(
            transformer_list=[
                ('text', Pipeline([
                    ('selector', ItemSelector(key='text')),
                    ('hasher', HashingVectorizer(n_features=2**16)),
                ])),
                ('title', Pipeline([
                    ('selector', ItemSelector(key='title')),
                    ('hasher', HashingVectorizer(n_features=2**16)),
                ])),
                ('meta', Pipeline([
                    ('selector', ItemSelector(key='meta')),
                    ('hasher', HashingVectorizer(n_features=2**16)),
                ]))
            ],
        )),
        ('svc', LinearSVC()),
    ])
    pipeline.fit(train, train.category)
    joblib.dump(pipeline, model)
    tst = pipeline.predict(test)
    result = pandas.Series(tst)

    return result


def assert_class_to_root(dataframes):
    # classes = pandas.DataFrame(columns=['root', 'prediction', 'count'])
    # for dataframe in dataframes:
    #     classes = pandas.concat(
    #         [classes, dataframe.groupby(['root', 'prediction'])['root'].size().reset_index(name='count')],
    #         axis=0, ignore_index=True).reset_index(drop=True)
    # result = classes.groupby(['root']).head(1).reset_index(drop=True)
    # classes = pandas.concat(
    #     [classes, dataframes.groupby(['root', 'prediction'])['root'].size().reset_index(name='count')],
    #     axis=0, ignore_index=True).reset_index(drop=True)
    #
    # result = classes.groupby(['root']).head(1).reset_index(drop=True)
    # result = classes[classes['prediction'] != 'unclassified'].groupby(['root']).head(1).reset_index(drop=True)
    dataframes = dataframes.groupby(['root', 'prediction'])['root']\
        .count().reset_index(name='count').sort_values(['count'], ascending=False)
    result = dataframes.groupby(['root']).head(1).reset_index(drop=True)

    return result


def classify(dataframe, roots):
    train = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    validate = dataframe.loc[dataframe['purpose'].isin(['validate'])].copy()
    test = dataframe.loc[dataframe['purpose'].isin(['test'])].copy()

    # categories = []
    # parameters = []
    # for i in range(len(init.CATEGORIES)):
    #     df = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    #     df.loc[df['category'] != init.CATEGORIES[i], 'category'] = 'unclassified'
    #     categories.append(df)
    #     parameters.append((df, test, init.DATA_PREFIX + init.CATEGORIES[i] + '.pkl'))

    # experiment = Experiment(api_key="Dmqg0JpLWqa5lmzvpbcDObE9A")
    # predicted = init.parallel(predict, parameters, mode='starmap')

    predicted = predict(train, test, init.DATA_PREFIX + 'model.pkl')
    # pprint(predicted)

    writer = pandas.ExcelWriter(init.EXCEL)
    # for i in range(len(init.CATEGORIES)):
    #     categories[i] = pandas.concat((predicted[i].rename('prediction'),
    #                                    test[['category', 'url', 'root']].reset_index(drop=True)), axis=1)
    #     categories[i].to_excel(writer, init.CATEGORIES[i])

    # print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0), 'categories')
    # pprint(categories)
    # results = assert_class_to_root(categories)
    # results = pandas.merge(results, roots[['root', 'category']], on='root')
    categories = pandas.concat((predicted.rename('prediction'),
                                test[['category', 'url', 'root']].reset_index(drop=True)), axis=1)
    categories.to_excel(writer, 'prediction')
    results = assert_class_to_root(categories)
    results = pandas.merge(results, roots[['root', 'category']], on='root')
    print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0),
          'accuracy score: {}'.format(accuracy_score(results.category, results.prediction)))

    y_true = pandas.Series(results.category)
    y_pred = pandas.Series(results.prediction)

    print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0))
    pprint(pandas.crosstab(y_true, y_pred, rownames=['True'], colnames=['Predicted'], margins=True)
           .apply(lambda r: 100.0 * r / r.sum()))
    init.confusion_matrix('confusion_matrix.png',
                          confusion_matrix(results.category, results.prediction, labels=init.CATEGORIES))
    results.to_excel(writer, 'results')
    # init.get_output(init.RESULTS, results)
