import init
import pandas
from colored import fg, attr
from comet_ml import Experiment
from datetime import datetime
from pprint import pprint
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.externals import joblib
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics import accuracy_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC


def predict(train, test, model):
    """Train classifier and predict results
        :param train:
        :param test:
        :param model:
    """

    def get_text(train):
        coder = HashingVectorizer()
        result = coder.fit_transform(train.text)
        print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0))
        pprint(result)

        return result

    def get_depth(train):
        result = train.depth
        print(fg('blue') + '[' + str(datetime.now().time()) + ']' + attr(0))
        pprint(result)

        return result

    # classifier = Pipeline([
    #     ('features', FeatureUnion([
    #         ('text', FunctionTransformer(get_text, validate=False)),
    #         ('depth', FunctionTransformer(get_depth, validate=False))
    #     ])),
    #     ('clf', LinearSVC())
    # ])
    #
    # classifier.fit(train, train.category)
    # predicted = classifier.predict(test)
    # pprint(predicted)

    coder = HashingVectorizer()
    trn = coder.fit_transform(train.text)
    clf = LinearSVC().fit(trn, train.category)
    joblib.dump(clf, model)
    tst = coder.transform(test.text.values.astype('U'))
    clf = joblib.load(model)

    return pandas.Series(clf.predict(tst))


def assert_class_to_root(dataframes):
    classes = pandas.DataFrame(columns=['root', 'prediction', 'count'])
    for dataframe in dataframes:
        classes = pandas.concat(
            [classes, dataframe.groupby(['root', 'prediction'])['root'].size().reset_index(name='count')],
            axis=0, ignore_index=True).reset_index(drop=True)
    result = classes[classes['prediction'] != 'unclassified'].groupby(['root']).head(1).reset_index(drop=True)
    roots = classes.groupby(['root']).head(1).reset_index(drop=True)
    roots.loc[roots['root'].isin(result['root']), ['prediction', 'count']] = \
        result.loc[result['root'].isin(roots['root']), ['prediction', 'count']].values

    return roots


def classify(dataframe, roots):
    test = dataframe.loc[dataframe['purpose'].isin(['test'])].copy()
    validate = dataframe.loc[dataframe['purpose'].isin(['validate'])].copy()
    # pprint(test)
    # print()

    categories = []
    parameters = []
    for i in range(len(init.CATEGORIES)):
        df = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
        df.loc[df['category'] != init.CATEGORIES[i], 'category'] = 'unclassified'
        categories.append(df)
        parameters.append((df, test, init.DATA_PREFIX + init.CATEGORIES[i] + '.pkl'))

    # experiment = Experiment(api_key="Dmqg0JpLWqa5lmzvpbcDObE9A")
    predicted = init.parallel(predict, parameters, mode='starmap')

    writer = pandas.ExcelWriter(init.EXCEL)
    for i in range(len(init.CATEGORIES)):
        categories[i] = pandas.concat((predicted[i].rename('prediction'),
                                       test[['category', 'url', 'root']].reset_index(drop=True)), axis=1)
        categories[i].to_excel(writer, init.CATEGORIES[i])

    results = assert_class_to_root(categories)
    results = pandas.merge(results, roots[['root', 'category']], on='root')
    pprint(accuracy_score(results.category, results.prediction))
    results.to_excel(writer, 'results')
    init.get_output(init.RESULTS, results)
